from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle
import os
import logging
from typing import List, Dict, Optional
import sys

# Add spark-apps to path to import our model
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
spark_apps_path = os.path.join(project_root, 'spark-apps')
sys.path.insert(0, spark_apps_path)
sys.path.insert(0, './models')  # Add models directory to path

try:
    from recommendation_model import GoodreadsRecommendationModel
    print("✅ Successfully imported GoodreadsRecommendationModel")
except ImportError as e:
    print(f"❌ Failed to import GoodreadsRecommendationModel: {e}")
    # Create dummy class
    class GoodreadsRecommendationModel:
        def __init__(self):
            self.models_loaded = False
        def load_model(self, models_dir):
            return False
        def get_content_recommendations(self, book_id: str, limit: int = 10):
            return []
        def get_collaborative_recommendations(self, user_id: int, limit: int = 10):
            return []
        def get_hybrid_recommendations(self, book_id: str = None, user_id: int = 1, num_recommendations: int = 10):
            return []

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class RecommendationAPI:
    def __init__(self):
        self.model = None
        self.books_pdf = None  # This should be the pandas DataFrame from your notebook
        self.load_model_and_data()
    
    def load_model_and_data(self):
        """Load the trained recommendation model and book data"""
        try:
            # Load the pandas DataFrame from your trained model (not CSV)
            books_pandas_path = './models/books_pandas.parquet'
            if os.path.exists(books_pandas_path):
                self.books_pdf = pd.read_parquet(books_pandas_path)
                logger.info(f"✅ Loaded {len(self.books_pdf)} books from trained model")
            else:
                logger.error(f"❌ Books parquet file not found at {books_pandas_path}")
                return
            
            # Load trained recommendation model
            model_path = './models'
            if os.path.exists(model_path):
                self.model = GoodreadsRecommendationModel()
                success = self.model.load_model(model_path)
                if success:
                    logger.info("✅ Recommendation model loaded successfully")
                else:
                    logger.warning("⚠️ Model loaded in fallback mode")
            else:
                logger.error(f"❌ Models directory not found at {model_path}")
                self.model = GoodreadsRecommendationModel()
                
        except Exception as e:
            logger.error(f"❌ Error loading model and data: {str(e)}")
            self.model = None
    
    def search_books(self, query: str, limit: int = 20) -> List[Dict]:
        """Search books using the function from your notebook"""
        if self.books_pdf is None:
            return []
        
        try:
            # Use the exact search logic from your notebook
            query_lower = query.lower()
            mask = (
                self.books_pdf["Name"].str.contains(query_lower, case=False, na=False) | 
                self.books_pdf["Description"].str.contains(query_lower, case=False, na=False) |
                self.books_pdf["Authors"].str.contains(query_lower, case=False, na=False)
            )
            results = self.books_pdf[mask].head(limit)
            
            return [
                {
                    'id': str(row['Id']),
                    'book_id': str(row['Id']),
                    'name': str(row['Name']),
                    'authors': str(row['Authors']),
                    'rating': self._safe_float_convert(row['Rating']),
                    'publisher': str(row['Publisher']),
                    'description': str(row['Description'])[:300] + "..." if len(str(row['Description'])) > 300 else str(row['Description'])
                }
                for idx, row in results.iterrows()
            ]
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_popular_books(self, limit: int = 20) -> List[Dict]:
        """Get popular books using the exact function from your notebook"""
        if self.books_pdf is None:
            return []
        
        try:
            # Use the exact get_popular_books function from your notebook
            df_copy = self.books_pdf.copy()
            
            # Convert Rating column to numeric (from your notebook logic)
            df_copy["Rating_Numeric"] = pd.to_numeric(df_copy["Rating"], errors='coerce')
            
            # If Rating_Numeric has NaN values, find the correct numeric column
            if df_copy["Rating_Numeric"].isna().all():
                for col_name in df_copy.columns:
                    if col_name != "Rating":
                        try:
                            numeric_col = pd.to_numeric(df_copy[col_name], errors='coerce')
                            if not numeric_col.isna().all() and numeric_col.min() >= 0 and numeric_col.max() <= 5:
                                df_copy["Rating_Numeric"] = numeric_col
                                break
                        except:
                            continue
            
            # Sort by rating and return top k (from your notebook)
            result = df_copy.nlargest(limit, "Rating_Numeric")
            
            return [
                {
                    'id': str(row['Id']),
                    'book_id': str(row['Id']),
                    'name': str(row['Name']),
                    'authors': str(row['Authors']),
                    'rating': round(row['Rating_Numeric'], 2),
                    'publisher': str(row['Publisher']),
                    'description': str(row['Description'])[:200] + "..." if len(str(row['Description'])) > 200 else str(row['Description'])
                }
                for idx, row in result.iterrows()
            ]
        except Exception as e:
            logger.error(f"Popular books error: {e}")
            return []
    
    def get_book_details(self, book_id: str) -> Optional[Dict]:
        """Get book details by ID"""
        if self.books_pdf is None:
            return None
        
        try:
            book_id_int = int(book_id)
            book_row = self.books_pdf[self.books_pdf['Id'] == book_id_int]
            
            if book_row.empty:
                return None
            
            book = book_row.iloc[0]
            return {
                'id': str(book['Id']),
                'book_id': str(book['Id']),
                'name': str(book['Name']),
                'authors': str(book['Authors']),
                'rating': self._safe_float_convert(book['Rating']),
                'publisher': str(book['Publisher']),
                'description': str(book['Description'])
            }
        except Exception as e:
            logger.error(f"Book details error: {e}")
            return None
    
    def get_recommendations(self, book_id: str, method: str = 'content', limit: int = 10) -> List[Dict]:
        """Get recommendations using your trained models"""
        if self.model is None:
            return []
        
        try:
            if method == 'content':
                return self.model.get_content_recommendations(book_id, limit)
            elif method == 'collaborative':
                return self.model.get_collaborative_recommendations(1, limit)  # Default user_id = 1
            elif method == 'hybrid':
                return self.model.get_hybrid_recommendations(book_id=book_id, num_recommendations=limit)
            else:
                return self.model.get_content_recommendations(book_id, limit)
        except Exception as e:
            logger.error(f"Recommendations error: {e}")
            return []
    
    def recommend_by_author(self, author: str, limit: int = 10) -> List[Dict]:
        """Recommend books by same author (from your notebook)"""
        if self.books_pdf is None:
            return []
        
        try:
            author_books = self.books_pdf[
                self.books_pdf['Authors'].str.contains(author, case=False, na=False)
            ].head(limit)
            
            return [
                {
                    'id': str(row['Id']),
                    'book_id': str(row['Id']),
                    'name': str(row['Name']),
                    'authors': str(row['Authors']),
                    'description': str(row['Description'])[:200] + "..." if len(str(row['Description'])) > 200 else str(row['Description']),
                    'rating': self._safe_float_convert(row['Rating']),
                    'recommendation_type': 'by_author'
                }
                for idx, row in author_books.iterrows()
            ]
        except Exception as e:
            logger.error(f"Author recommendations error: {e}")
            return []
    
    def _safe_float_convert(self, value):
        """Safely convert rating to float"""
        try:
            if pd.isna(value):
                return 0.0
            return round(float(str(value).replace(',', '.')), 2)
        except:
            return 0.0

# Initialize API
api = RecommendationAPI()

# ===== ENDPOINTS MATCHING YOUR NOTEBOOK =====

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': api.model is not None and api.model.models_loaded,
        'data_loaded': api.books_pdf is not None,
        'total_books': len(api.books_pdf) if api.books_pdf is not None else 0
    })

@app.route('/books/search', methods=['GET'])
def search_books():
    """Search books endpoint - matches your notebook search_books function"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 20))
    
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400
    
    results = api.search_books(query, limit)
    
    return jsonify({
        'query': query,
        'results': results,
        'total': len(results)
    })

@app.route('/books/popular', methods=['GET'])
def get_popular_books():
    """Popular books endpoint - matches your notebook get_popular_books function"""
    limit = int(request.args.get('limit', 20))
    books = api.get_popular_books(limit)
    
    return jsonify({
        'books': books,
        'total': len(books)
    })

@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    """Get book details endpoint"""
    book = api.get_book_details(book_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    return jsonify(book)

@app.route('/books/<book_id>/recommendations', methods=['GET'])
def get_recommendations(book_id):
    """Get recommendations endpoint - uses your LSH and ALS models"""
    method = request.args.get('method', 'content')
    limit = int(request.args.get('limit', 10))
    
    recommendations = api.get_recommendations(book_id, method, limit)
    
    return jsonify({
        'book_id': book_id,
        'method': method,
        'recommendations': recommendations,
        'total': len(recommendations)
    })

@app.route('/books/author/<author>/recommendations', methods=['GET'])
def get_author_recommendations(author):
    """Get books by same author - matches your recommend_by_author function"""
    limit = int(request.args.get('limit', 10))
    
    recommendations = api.recommend_by_author(author, limit)
    
    return jsonify({
        'author': author,
        'recommendations': recommendations,
        'total': len(recommendations)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
