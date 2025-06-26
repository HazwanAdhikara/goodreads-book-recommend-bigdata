// API Response Types matching your backend exactly
export interface Book {
  id: string;
  book_id: string;
  name: string;
  authors: string;
  rating: number;
  publisher?: string;
  description: string;
  publish_year?: string;
  pages?: string;
  rating_count?: number;
}

export interface Recommendation {
  book_id: string;
  name: string;
  authors: string;
  description: string;
  rating: number;
  similarity_score: number;
  recommendation_type:
    | "content_based"
    | "collaborative"
    | "hybrid"
    | "by_author"
    | "fallback_content"
    | "fallback_collaborative";
}

export interface SearchResponse {
  query: string;
  results: Book[];
  total: number;
}

export interface PopularBooksResponse {
  books: Book[];
  total: number;
}

export interface RecommendationResponse {
  book_id: string;
  method: string;
  recommendations: Recommendation[];
  total: number;
}

export interface AuthorRecommendationResponse {
  author: string;
  recommendations: Recommendation[];
  total: number;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  data_loaded: boolean;
  total_books: number;
}

// Component Props Types
export interface BookCardProps {
  book: Book | Recommendation;
  onBookClick?: (book: Book | Recommendation) => void;
  showSimilarity?: boolean;
}

export interface SearchBarProps {
  onSearch: (query: string) => void;
  loading?: boolean;
  placeholder?: string;
}

export interface RecommendationMethodProps {
  method: "content" | "collaborative" | "hybrid";
  onMethodChange: (method: "content" | "collaborative" | "hybrid") => void;
}
