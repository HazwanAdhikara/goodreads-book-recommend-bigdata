import pandas as pd
import pickle
import os
import sys
from typing import List, Dict, Optional

# Handle imports based on environment
try:
    from pyspark.sql import SparkSession
    from pyspark.ml.recommendation import ALSModel
    from pyspark.ml.feature import BucketedRandomProjectionLSHModel, CountVectorizerModel
    from pyspark.sql.functions import col
    SPARK_AVAILABLE = True
except ImportError:
    print("⚠️ PySpark not available - running in fallback mode")
    SPARK_AVAILABLE = False

class GoodreadsRecommendationModel:
    def __init__(self):
        self.spark = None
        self.als_model = None
        self.lsh_model = None
        self.cv_model = None
        self.books_df = None
        self.books_pdf = None
        self.metadata = None
        self.spark_available = SPARK_AVAILABLE
        self.models_loaded = False
        
    def load_model(self, models_dir):
        """Load all trained models exactly as saved from your notebook"""
        try:
            if not self.spark_available:
                print("⚠️ Spark not available, using fallback mode")
                # Load pandas data only
                books_pandas_path = f"{models_dir}/books_pandas.parquet"
                if os.path.exists(books_pandas_path):
                    self.books_pdf = pd.read_parquet(books_pandas_path)
                    print(f"✅ Loaded {len(self.books_pdf)} books in fallback mode")
                
                self.models_loaded = True
                return True
            
            # Initialize Spark with same config as your notebook
            self.spark = SparkSession.builder \
                .appName("GoodreadsAPI") \
                .config("spark.sql.adaptive.enabled", "true") \
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
                .getOrCreate()
            
            # Load Spark models (exactly as saved in your notebook)
            self.als_model = ALSModel.load(f"{models_dir}/als_model")
            self.lsh_model = BucketedRandomProjectionLSHModel.load(f"{models_dir}/lsh_model")
            self.cv_model = CountVectorizerModel.load(f"{models_dir}/cv_model")
            
            # Load data (exactly as saved in your notebook)
            self.books_df = self.spark.read.parquet(f"{models_dir}/books_features.parquet")
            self.books_pdf = pd.read_parquet(f"{models_dir}/books_pandas.parquet")
            
            # Load metadata
            with open(f"{models_dir}/model_metadata.pkl", "rb") as f:
                self.metadata = pickle.load(f)
            
            self.models_loaded = True
            print(f"✅ All models loaded successfully: {self.metadata['total_books']} books")
            return True
                
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            self.models_loaded = False
            return False
    
    def get_content_recommendations(self, book_id: str, limit: int = 10) -> List[Dict]:
        """Content-based recommendations using LSH - exact function from your notebook"""
        if not self.models_loaded:
            return self._fallback_content_recommendations(book_id, limit)
        
        if not self.spark_available or not self.lsh_model or not self.books_df:
            return self._fallback_content_recommendations(book_id, limit)
        
        try:
            # This is your exact recommend_similar_books_lsh function from the notebook
            book_id_int = int(book_id)
            
            # Get target book features
            target_row = self.books_df.filter(col("Id") == book_id_int).first()
            if not target_row:
                return []
            
            target_vec = target_row["features"]
            
            # Find similar books using LSH (exact logic from notebook)
            neighbors = self.lsh_model.approxNearestNeighbors(self.books_df, target_vec, limit + 1)
            similar_books = neighbors.filter(col("Id") != book_id_int).select("Id", "Name", "Authors", "Description", "Rating", "distCol").orderBy("distCol").limit(limit)
            
            results = similar_books.toPandas()
            
            return [
                {
                    'book_id': str(row['Id']),
                    'name': str(row['Name']),
                    'authors': str(row['Authors']),
                    'description': str(row['Description'])[:200] + "..." if len(str(row['Description'])) > 200 else str(row['Description']),
                    'rating': self._safe_rating_convert(row['Rating']),
                    'similarity_score': round(1.0 / (1.0 + row['distCol']), 3),
                    'recommendation_type': 'content_based'
                }
                for _, row in results.iterrows()
            ]
            
        except Exception as e:
            print(f"Error in LSH recommendations: {e}")
            return self._fallback_content_recommendations(book_id, limit)
    
    def get_collaborative_recommendations(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Collaborative filtering using ALS - exact function from your notebook"""
        if not self.models_loaded or not self.spark_available or not self.als_model:
            return self._fallback_collaborative_recommendations(user_id, limit)
        
        try:
            # This is your exact recommend_for_user function from the notebook
            user_df = self.spark.createDataFrame([(user_id,)], ["userId"])
            recs = self.als_model.recommendForUserSubset(user_df, limit)
            
            if recs.count() > 0:
                rec_items = recs.select("recommendations").first()["recommendations"]
                book_ids = [item["bookId"] for item in rec_items]
                
                # Get book details (exact logic from notebook)
                recommended_books = self.books_df.filter(col("Id").isin(book_ids)).select("Id", "Name", "Authors", "Description", "Rating").toPandas()
                
                return [
                    {
                        'book_id': str(row['Id']),
                        'name': str(row['Name']),
                        'authors': str(row['Authors']),
                        'description': str(row['Description'])[:200] + "..." if len(str(row['Description'])) > 200 else str(row['Description']),
                        'rating': self._safe_rating_convert(row['Rating']),
                        'similarity_score': 0.9,  # Default from your notebook
                        'recommendation_type': 'collaborative'
                    }
                    for _, row in recommended_books.iterrows()
                ]
            return []
            
        except Exception as e:
            print(f"Error in ALS recommendations: {e}")
            return self._fallback_collaborative_recommendations(user_id, limit)
    
    def get_hybrid_recommendations(self, book_id: str = None, user_id: int = 1, num_recommendations: int = 10) -> List[Dict]:
        """Hybrid recommendations combining both methods"""
        content_recs = []
        collaborative_recs = []
        
        if book_id:
            content_recs = self.get_content_recommendations(book_id, num_recommendations // 2)
        
        collaborative_recs = self.get_collaborative_recommendations(user_id, num_recommendations // 2)
        
        # Combine and deduplicate
        all_recs = content_recs + collaborative_recs
        seen_ids = set()
        unique_recs = []
        
        for rec in all_recs:
            if rec['book_id'] not in seen_ids:
                seen_ids.add(rec['book_id'])
                rec['recommendation_type'] = 'hybrid'
                unique_recs.append(rec)
        
        return unique_recs[:num_recommendations]
    
    def _fallback_content_recommendations(self, book_id: str, limit: int = 10) -> List[Dict]:
        """Fallback content recommendations using pandas only"""
        if self.books_pdf is None:
            return []
        
        try:
            book_id_int = int(book_id)
            target_book = self.books_pdf[self.books_pdf['Id'] == book_id_int]
            
            if target_book.empty:
                return []
            
            target_author = target_book.iloc[0]['Authors']
            
            # Find books by same author (simple fallback)
            similar_books = self.books_pdf[
                (self.books_pdf['Authors'].str.contains(target_author, case=False, na=False)) &
                (self.books_pdf['Id'] != book_id_int)
            ].head(limit)
            
            return [
                {
                    'book_id': str(row['Id']),
                    'name': str(row['Name']),
                    'authors': str(row['Authors']),
                    'description': str(row['Description'])[:200] + "..." if len(str(row['Description'])) > 200 else str(row['Description']),
                    'rating': self._safe_rating_convert(row['Rating']),
                    'similarity_score': 0.7,
                    'recommendation_type': 'fallback_content'
                }
                for _, row in similar_books.iterrows()
            ]
        except Exception as e:
            print(f"Fallback content error: {e}")
            return []
    
    def _fallback_collaborative_recommendations(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Fallback collaborative recommendations"""
        if self.books_pdf is None:
            return []
        
        # Return top rated books as fallback
        try:
            top_books = self.books_pdf.nlargest(limit, 'Rating')
            return [
                {
                    'book_id': str(row['Id']),
                    'name': str(row['Name']),
                    'authors': str(row['Authors']),
                    'description': str(row['Description'])[:200] + "..." if len(str(row['Description'])) > 200 else str(row['Description']),
                    'rating': self._safe_rating_convert(row['Rating']),
                    'similarity_score': 0.8,
                    'recommendation_type': 'fallback_collaborative'
                }
                for _, row in top_books.iterrows()
            ]
        except Exception as e:
            print(f"Fallback collaborative error: {e}")
            return []
    
    def _safe_rating_convert(self, rating):
        """Safely convert rating to float"""
        try:
            if pd.isna(rating):
                return 0.0
            return round(float(str(rating).replace(',', '.')), 2)
        except:
            return 0.0