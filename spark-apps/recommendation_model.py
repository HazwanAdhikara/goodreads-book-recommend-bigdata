from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.ml.feature import *
from pyspark.ml.recommendation import ALS
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoodreadsRecommendationModel:
    def __init__(self, spark_session=None):
        if spark_session is None:
            self.spark = SparkSession.builder \
                .appName("GoodreadsRecommendationSystem") \
                .config("spark.sql.adaptive.enabled", "true") \
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                .getOrCreate()
        else:
            self.spark = spark_session
        
        self.content_model = None
        self.collaborative_model = None
        self.book_features = None
        self.tfidf_matrix = None
        self.book_index_map = None
        
    def load_data(self, csv_path):
        """Load and preprocess the dataset"""
        logger.info(f"Loading data from {csv_path}")
        
        # Load data
        df = self.spark.read.csv(csv_path, header=True, inferSchema=True)
        
        # Clean and preprocess
        df = df.dropna(subset=["Name", "Authors", "Description", "Rating"])
        
        # Convert rating to numeric
        df = df.withColumn("Rating", regexp_replace(col("Rating"), ",", ".").cast("double"))
        
        # Extract publish year
        df = df.withColumn("PublishYear", 
                          when(col("PublishYear").isNotNull(), col("PublishYear").cast("int"))
                          .otherwise(2000))
        
        # Convert pages to numeric
        df = df.withColumn("PagesNumber", 
                          regexp_extract(col("PagesNumber"), r"(\d+)", 1).cast("int"))
        
        # Create book ID if not exists
        df = df.withColumn("BookID", monotonically_increasing_id())
        
        logger.info(f"Loaded {df.count()} books after cleaning")
        return df
    
    def prepare_content_features(self, df):
        """Prepare features for content-based recommendation"""
        logger.info("Preparing content-based features...")
        
        # Convert to Pandas for easier text processing
        pandas_df = df.toPandas()
        
        # Combine text features
        pandas_df['combined_features'] = (
            pandas_df['Authors'].fillna('') + ' ' +
            pandas_df['Publisher'].fillna('') + ' ' +
            pandas_df['Description'].fillna('')
        ).str.lower()
        
        # Create TF-IDF matrix for descriptions
        tfidf = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )
        
        self.tfidf_matrix = tfidf.fit_transform(pandas_df['combined_features'])
        
        # Create book index mapping
        self.book_index_map = dict(zip(pandas_df['BookID'], range(len(pandas_df))))
        self.reverse_book_map = dict(zip(range(len(pandas_df)), pandas_df['BookID']))
        
        # Store book metadata
        self.book_features = pandas_df[[
            'BookID', 'Name', 'Authors', 'Rating', 'PublishYear', 
            'Publisher', 'PagesNumber', 'Description'
        ]].set_index('BookID')
        
        logger.info("Content features prepared successfully")
        
    def train_content_model(self, df):
        """Train content-based recommendation model"""
        logger.info("Training content-based model...")
        
        self.prepare_content_features(df)
        
        # The model is essentially the TF-IDF matrix and cosine similarity
        # We'll compute similarities on-demand to save memory
        
        logger.info("Content-based model trained successfully")
    
    def prepare_collaborative_data(self, df):
        """Prepare data for collaborative filtering"""
        logger.info("Preparing collaborative filtering data...")
        
        # For demo purposes, we'll create synthetic user interactions
        # In real scenario, you'd have user-book interaction data
        
        pandas_df = df.toPandas()
        
        # Create synthetic users based on book popularity and ratings
        np.random.seed(42)
        
        users_data = []
        user_id = 1
        
        for _, book in pandas_df.iterrows():
            # Number of users who rated this book (based on RatingDistTotal)
            num_users = min(int(book['RatingDistTotal'] * 0.1), 1000)  # Scale down for demo
            
            if num_users > 0:
                # Generate ratings around the actual book rating
                ratings = np.random.normal(book['Rating'], 0.5, num_users)
                ratings = np.clip(ratings, 1, 5)  # Clip to valid rating range
                
                for rating in ratings:
                    users_data.append({
                        'UserID': user_id,
                        'BookID': book['BookID'],
                        'Rating': float(rating)
                    })
                    user_id += 1
                    if user_id > 10000:  # Limit for demo
                        break
            
            if user_id > 10000:
                break
        
        # Convert to Spark DataFrame
        users_df = self.spark.createDataFrame(users_data)
        
        logger.info(f"Created {len(users_data)} synthetic user-book interactions")
        return users_df
    
    def train_collaborative_model(self, df):
        """Train collaborative filtering model using ALS"""
        logger.info("Training collaborative filtering model...")
        
        # Prepare user-book interactions
        interactions_df = self.prepare_collaborative_data(df)
        
        # Split data
        train_df, test_df = interactions_df.randomSplit([0.8, 0.2], seed=42)
        
        # Configure ALS
        als = ALS(
            maxIter=10,
            regParam=0.1,
            userCol="UserID",
            itemCol="BookID", 
            ratingCol="Rating",
            coldStartStrategy="drop",
            rank=50
        )
        
        # Train model
        self.collaborative_model = als.fit(train_df)
        
        # Evaluate model
        predictions = self.collaborative_model.transform(test_df)
        evaluator = RegressionEvaluator(
            metricName="rmse",
            labelCol="Rating",
            predictionCol="prediction"
        )
        rmse = evaluator.evaluate(predictions)
        logger.info(f"Collaborative model RMSE: {rmse:.3f}")
        
        logger.info("Collaborative filtering model trained successfully")
    
    def get_content_recommendations(self, book_id, num_recommendations=10):
        """Get content-based recommendations for a book"""
        if book_id not in self.book_index_map:
            logger.warning(f"Book ID {book_id} not found")
            return []
        
        # Get book index
        book_idx = self.book_index_map[book_id]
        
        # Compute cosine similarities
        book_vector = self.tfidf_matrix[book_idx]
        similarities = cosine_similarity(book_vector, self.tfidf_matrix).flatten()
        
        # Get top similar books (excluding the book itself)
        similar_indices = similarities.argsort()[::-1][1:num_recommendations+1]
        
        recommendations = []
        for idx in similar_indices:
            similar_book_id = self.reverse_book_map[idx]
            book_info = self.book_features.loc[similar_book_id]
            
            recommendations.append({
                'book_id': similar_book_id,
                'name': book_info['Name'],
                'authors': book_info['Authors'],
                'rating': book_info['Rating'],
                'similarity_score': similarities[idx],
                'description': book_info['Description'][:200] + "..."
            })
        
        return recommendations
    
    def get_collaborative_recommendations(self, user_id, num_recommendations=10):
        """Get collaborative filtering recommendations for a user"""
        if self.collaborative_model is None:
            logger.warning("Collaborative model not trained")
            return []
        
        # Get user recommendations
        user_df = self.spark.createDataFrame([(user_id,)], ["UserID"])
        recommendations = self.collaborative_model.recommendForUserSubset(user_df, num_recommendations)
        
        recs = []
        if recommendations.count() > 0:
            recommendations_list = recommendations.collect()[0]['recommendations']
            
            for rec in recommendations_list:
                book_id = rec['BookID']
                if book_id in self.book_features.index:
                    book_info = self.book_features.loc[book_id]
                    recs.append({
                        'book_id': book_id,
                        'name': book_info['Name'],
                        'authors': book_info['Authors'],
                        'rating': book_info['Rating'],
                        'predicted_rating': rec['rating'],
                        'description': book_info['Description'][:200] + "..."
                    })
        
        return recs
    
    def get_hybrid_recommendations(self, book_id=None, user_id=None, num_recommendations=10):
        """Get hybrid recommendations combining content and collaborative filtering"""
        recommendations = []
        
        # Get content-based recommendations
        if book_id is not None:
            content_recs = self.get_content_recommendations(book_id, num_recommendations)
            for rec in content_recs:
                rec['recommendation_type'] = 'content'
                rec['score'] = rec['similarity_score']
            recommendations.extend(content_recs)
        
        # Get collaborative recommendations
        if user_id is not None and self.collaborative_model is not None:
            collab_recs = self.get_collaborative_recommendations(user_id, num_recommendations)
            for rec in collab_recs:
                rec['recommendation_type'] = 'collaborative'
                rec['score'] = rec['predicted_rating'] / 5.0  # Normalize to 0-1
            recommendations.extend(collab_recs)
        
        # Remove duplicates and sort by score
        seen_books = set()
        unique_recs = []
        for rec in sorted(recommendations, key=lambda x: x['score'], reverse=True):
            if rec['book_id'] not in seen_books:
                unique_recs.append(rec)
                seen_books.add(rec['book_id'])
        
        return unique_recs[:num_recommendations]
    
    def save_model(self, model_path):
        """Save the trained models"""
        logger.info(f"Saving models to {model_path}")
        
        os.makedirs(model_path, exist_ok=True)
        
        # Save content-based model components
        with open(f"{model_path}/tfidf_matrix.pkl", "wb") as f:
            pickle.dump(self.tfidf_matrix, f)
        
        with open(f"{model_path}/book_index_map.pkl", "wb") as f:
            pickle.dump(self.book_index_map, f)
        
        with open(f"{model_path}/reverse_book_map.pkl", "wb") as f:
            pickle.dump(self.reverse_book_map, f)
        
        self.book_features.to_pickle(f"{model_path}/book_features.pkl")
        
        # Save collaborative model
        if self.collaborative_model is not None:
            self.collaborative_model.write().overwrite().save(f"{model_path}/collaborative_model")
        
        logger.info("Models saved successfully")
    
    def load_model(self, model_path):
        """Load pre-trained models"""
        logger.info(f"Loading models from {model_path}")
        
        # Load content-based model components
        with open(f"{model_path}/tfidf_matrix.pkl", "rb") as f:
            self.tfidf_matrix = pickle.load(f)
        
        with open(f"{model_path}/book_index_map.pkl", "rb") as f:
            self.book_index_map = pickle.load(f)
        
        with open(f"{model_path}/reverse_book_map.pkl", "rb") as f:
            self.reverse_book_map = pickle.load(f)
        
        self.book_features = pd.read_pickle(f"{model_path}/book_features.pkl")
        
        # Load collaborative model if exists
        try:
            from pyspark.ml.recommendation import ALSModel
            self.collaborative_model = ALSModel.load(f"{model_path}/collaborative_model")
        except Exception as e:
            logger.warning(f"Could not load collaborative model: {e}")
        
        logger.info("Models loaded successfully")

def main():
    """Main training function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Train Goodreads Recommendation Model')
    parser.add_argument('--data-path', default='/opt/spark-data/goodreads.csv',
                       help='Path to the CSV data file')
    parser.add_argument('--model-path', default='/opt/spark-apps/models',
                       help='Path to save the trained models')
    parser.add_argument('--train-content', action='store_true', default=True,
                       help='Train content-based model')
    parser.add_argument('--train-collaborative', action='store_true', default=True,
                       help='Train collaborative filtering model')
    
    args = parser.parse_args()
    
    # Initialize model
    model = GoodreadsRecommendationModel()
    
    try:
        # Load and prepare data
        df = model.load_data(args.data_path)
        
        # Train models
        if args.train_content:
            model.train_content_model(df)
        
        if args.train_collaborative:
            model.train_collaborative_model(df)
        
        # Save models
        model.save_model(args.model_path)
        
        # Test recommendations
        logger.info("Testing recommendations...")
        pandas_df = df.toPandas()
        sample_book_id = pandas_df['BookID'].iloc[0]
        
        content_recs = model.get_content_recommendations(sample_book_id, 5)
        logger.info(f"Content recommendations for book {sample_book_id}:")
        for i, rec in enumerate(content_recs, 1):
            logger.info(f"  {i}. {rec['name']} by {rec['authors']} (score: {rec['similarity_score']:.3f})")
        
        logger.info("Model training completed successfully!")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise
    finally:
        model.spark.stop()

if __name__ == "__main__":
    main()
