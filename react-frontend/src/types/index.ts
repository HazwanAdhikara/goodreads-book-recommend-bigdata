export interface Book {
  id: string;
  book_id?: string | number;
  name: string;
  authors: string;
  rating: number;
  publish_year: string;
  publisher: string;
  pages: string;
  description: string;
  rating_count?: number;
}

export interface Recommendation {
  book_id: string | number;
  name: string;
  authors: string;
  rating: number;
  similarity_score?: number;
  predicted_rating?: number;
  description: string;
  recommendation_type?: "content" | "collaborative" | "hybrid" | "simple";
  score?: number;
}

export interface SearchResponse {
  query: string;
  results: Book[];
  total: number;
}

export interface RecommendationResponse {
  book_id: string;
  method: string;
  recommendations: Recommendation[];
  total: number;
}

export interface PopularBooksResponse {
  books: Book[];
  total: number;
}

export interface FilterRequest {
  min_rating?: number;
  max_rating?: number;
  authors?: string[];
  publishers?: string[];
  min_year?: number;
  max_year?: number;
  limit?: number;
}

export interface FilteredRecommendationResponse {
  filters: FilterRequest;
  books: Book[];
  total: number;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  data_loaded: boolean;
  total_books: number;
}
