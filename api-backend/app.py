from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import pickle
import os
import logging
from typing import List, Dict, Optional
import sys

# Add spark-apps to path to import our model
sys.path.append('/app/spark-apps')

try:
    from recommendation_model import GoodreadsRecommendationModel
except ImportError:
    # Fallback for development
    sys.path.append('../spark-apps')
    from recommendation_model import GoodreadsRecommendationModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

class RecommendationAPI:
    def __init__(self):
        self.model = None
        self.books_df = None
        self.load_model_and_data()
    
    def load_model_and_data(self):
        """Load the trained recommendation model and book data"""
        try:
            # Load book data
            data_path = '/app/data/goodreads.csv'
            if os.path.exists(data_path):
                self.books_df = pd.read_csv(data_path)
                logger.info(f"Loaded {len(self.books_df)} books")
            else:
                logger.warning(f"Data file not found at {data_path}")
                return
            
            # Load trained model
            model_path = '/app/models'
            if os.path.exists(model_path):
                self.model = GoodreadsRecommendationModel()
                self.model.load_model(model_path)
                logger.info("Recommendation model loaded successfully")
            else:
                logger.warning(f"Model not found at {model_path}")
                # Initialize model without loading for basic functionality
                self.model = GoodreadsRecommendationModel()
                
        except Exception as e:
            logger.error(f"Error loading model and data: {str(e)}")
            self.model = None
    
    def search_books(self, query: str, limit: int = 20) -> List[Dict]:
        """Search books by title, author, or description"""
        if self.books_df is None:
            return []
        
        query = query.lower()
        
        # Search in multiple fields
        mask = (
            self.books_df['Name'].str.lower().str.contains(query, na=False) |
            self.books_df['Authors'].str.lower().str.contains(query, na=False) |
            self.books_df['Description'].str.lower().str.contains(query, na=False)
        )
        
        results = self.books_df[mask].head(limit)
        
        return [
            {
                'id': str(row['Id']) if 'Id' in row else str(idx),
                'book_id': getattr(row, 'BookID', idx),
                'name': row['Name'],
                'authors': row['Authors'],
                'rating': float(str(row['Rating']).replace(',', '.')),
                'publish_year': str(row['PublishYear']),
                'publisher': row['Publisher'],
                'pages': str(row['PagesNumber']),
                'description': row['Description'][:300] + "..." if len(str(row['Description'])) > 300 else row['Description']
            }
            for idx, row in results.iterrows()
        ]
    
    def get_book_details(self, book_id: str) -> Optional[Dict]:
        """Get detailed information about a specific book"""
        if self.books_df is None:
            return None
        
        # Try to find by Id first, then by index
        book = None
        if 'Id' in self.books_df.columns:
            book_match = self.books_df[self.books_df['Id'] == book_id]
            if not book_match.empty:
                book = book_match.iloc[0]
        
        if book is None:
            try:
                book_idx = int(book_id)
                if book_idx < len(self.books_df):
                    book = self.books_df.iloc[book_idx]
            except (ValueError, IndexError):
                return None
        
        if book is None:
            return None
        
        return {
            'id': str(book['Id']) if 'Id' in book else book_id,
            'book_id': getattr(book, 'BookID', book_id),
            'name': book['Name'],
            'authors': book['Authors'],
            'rating': float(str(book['Rating']).replace(',', '.')),
            'publish_year': str(book['PublishYear']),
            'publisher': book['Publisher'],
            'pages': str(book['PagesNumber']),
            'rating_count': int(book['RatingDistTotal']) if 'RatingDistTotal' in book else 0,
            'description': book['Description']
        }
    
    def get_recommendations(self, book_id: str, method: str = 'content', limit: int = 10) -> List[Dict]:
        """Get book recommendations"""
        if self.model is None:
            # Fallback to simple similarity if model not loaded
            return self.get_simple_recommendations(book_id, limit)
        
        try:
            if method == 'content':
                return self.model.get_content_recommendations(book_id, limit)
            elif method == 'collaborative':
                # For collaborative, we need a user_id, use a default one
                return self.model.get_collaborative_recommendations(1, limit)
            elif method == 'hybrid':
                return self.model.get_hybrid_recommendations(book_id=book_id, num_recommendations=limit)
            else:
                return self.get_simple_recommendations(book_id, limit)
        except Exception as e:
            logger.error(f"Error getting recommendations: {str(e)}")
            return self.get_simple_recommendations(book_id, limit)
    
    def get_simple_recommendations(self, book_id: str, limit: int = 10) -> List[Dict]:
        """Simple fallback recommendation based on same author/publisher"""
        if self.books_df is None:
            return []
        
        book = self.get_book_details(book_id)
        if not book:
            return []
        
        # Find books by same author or publisher
        same_author = self.books_df[
            self.books_df['Authors'].str.contains(book['authors'], case=False, na=False)
        ]
        
        same_publisher = self.books_df[
            self.books_df['Publisher'].str.contains(book['publisher'], case=False, na=False)
        ]
        
        # Combine and remove duplicates
        recommendations = pd.concat([same_author, same_publisher]).drop_duplicates()
        
        # Remove the original book
        if 'Id' in recommendations.columns:
            recommendations = recommendations[recommendations['Id'] != book_id]
        
        # Sort by rating and limit results
        recommendations = recommendations.sort_values('Rating', ascending=False).head(limit)
        
        return [
            {
                'book_id': str(row['Id']) if 'Id' in row else str(idx),
                'name': row['Name'],
                'authors': row['Authors'],
                'rating': float(str(row['Rating']).replace(',', '.')),
                'similarity_score': 0.8,  # Default similarity
                'description': row['Description'][:200] + "..." if len(str(row['Description'])) > 200 else row['Description'],
                'recommendation_type': 'simple'
            }
            for idx, row in recommendations.iterrows()
        ]
    
    def get_popular_books(self, limit: int = 20) -> List[Dict]:
        """Get popular books based on rating and rating count"""
        if self.books_df is None:
            return []
        
        # Sort by rating and rating count
        popular = self.books_df.copy()
        popular['Rating'] = popular['Rating'].astype(str).str.replace(',', '.').astype(float)
        popular = popular.sort_values(['Rating', 'RatingDistTotal'], ascending=[False, False]).head(limit)
        
        return [
            {
                'id': str(row['Id']) if 'Id' in row else str(idx),
                'book_id': getattr(row, 'BookID', idx),
                'name': row['Name'],
                'authors': row['Authors'],
                'rating': row['Rating'],
                'publish_year': str(row['PublishYear']),
                'publisher': row['Publisher'],
                'pages': str(row['PagesNumber']),
                'description': row['Description'][:200] + "..." if len(str(row['Description'])) > 200 else row['Description']
            }
            for idx, row in popular.iterrows()
        ]

# Initialize API
api = RecommendationAPI()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': api.model is not None,
        'data_loaded': api.books_df is not None,
        'total_books': len(api.books_df) if api.books_df is not None else 0
    })

@app.route('/books/search', methods=['GET'])
def search_books():
    """Search books endpoint"""
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

@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    """Get book details endpoint"""
    book = api.get_book_details(book_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    return jsonify(book)

@app.route('/books/<book_id>/recommendations', methods=['GET'])
def get_recommendations(book_id):
    """Get book recommendations endpoint"""
    method = request.args.get('method', 'content')
    limit = int(request.args.get('limit', 10))
    
    recommendations = api.get_recommendations(book_id, method, limit)
    
    return jsonify({
        'book_id': book_id,
        'method': method,
        'recommendations': recommendations,
        'total': len(recommendations)
    })

@app.route('/books/popular', methods=['GET'])
def get_popular_books():
    """Get popular books endpoint"""
    limit = int(request.args.get('limit', 20))
    
    books = api.get_popular_books(limit)
    
    return jsonify({
        'books': books,
        'total': len(books)
    })

@app.route('/recommendations/filter', methods=['POST'])
def get_filtered_recommendations():
    """Get recommendations with filters"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'JSON data required'}), 400
    
    # Extract filters
    min_rating = data.get('min_rating', 0)
    max_rating = data.get('max_rating', 5)
    authors = data.get('authors', [])
    publishers = data.get('publishers', [])
    min_year = data.get('min_year', 1900)
    max_year = data.get('max_year', 2024)
    limit = data.get('limit', 20)
    
    if api.books_df is None:
        return jsonify({'error': 'Book data not available'}), 500
    
    # Apply filters
    filtered_df = api.books_df.copy()
    filtered_df['Rating'] = filtered_df['Rating'].astype(str).str.replace(',', '.').astype(float)
    
    # Rating filter
    filtered_df = filtered_df[
        (filtered_df['Rating'] >= min_rating) & 
        (filtered_df['Rating'] <= max_rating)
    ]
    
    # Author filter
    if authors:
        author_mask = filtered_df['Authors'].str.contains('|'.join(authors), case=False, na=False)
        filtered_df = filtered_df[author_mask]
    
    # Publisher filter
    if publishers:
        publisher_mask = filtered_df['Publisher'].str.contains('|'.join(publishers), case=False, na=False)
        filtered_df = filtered_df[publisher_mask]
    
    # Year filter
    filtered_df['PublishYear'] = pd.to_numeric(filtered_df['PublishYear'], errors='coerce')
    filtered_df = filtered_df[
        (filtered_df['PublishYear'] >= min_year) & 
        (filtered_df['PublishYear'] <= max_year)
    ]
    
    # Sort by rating and limit
    results = filtered_df.sort_values('Rating', ascending=False).head(limit)
    
    books = [
        {
            'id': str(row['Id']) if 'Id' in row else str(idx),
            'book_id': getattr(row, 'BookID', idx),
            'name': row['Name'],
            'authors': row['Authors'],
            'rating': row['Rating'],
            'publish_year': int(row['PublishYear']) if pd.notna(row['PublishYear']) else None,
            'publisher': row['Publisher'],
            'pages': str(row['PagesNumber']),
            'description': row['Description'][:200] + "..." if len(str(row['Description'])) > 200 else row['Description']
        }
        for idx, row in results.iterrows()
    ]
    
    return jsonify({
        'filters': data,
        'books': books,
        'total': len(books)
    })

try:
    from trino.dbapi import connect
except ImportError:
    connect = None

@app.route('/books/query', methods=['POST'])
def query_books():
    """
    Run custom SQL query on the data lakehouse via Trino.
    Expects JSON: { "sql": "SELECT * FROM books LIMIT 10" }
    """
    if connect is None:
        return jsonify({'error': 'Trino client not installed'}), 500
    data = request.get_json()
    if not data or 'sql' not in data:
        return jsonify({'error': 'SQL query required'}), 400
    sql = data['sql']
    try:
        conn = connect(
            host='trino', port=8080, user='user',
            catalog='hive', schema='default'
        )
        cur = conn.cursor()
        cur.execute(sql)
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        return jsonify({'columns': columns, 'rows': rows})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
