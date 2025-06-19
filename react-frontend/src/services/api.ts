import axios from "axios";
import {
  Book,
  SearchResponse,
  RecommendationResponse,
  PopularBooksResponse,
  FilterRequest,
  FilteredRecommendationResponse,
  HealthResponse,
} from "../types";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error);
    return Promise.reject(error);
  }
);

export const api = {
  // Health check
  health: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>("/health");
    return response.data;
  },

  // Search books
  searchBooks: async (
    query: string,
    limit: number = 20
  ): Promise<SearchResponse> => {
    const response = await apiClient.get<SearchResponse>("/books/search", {
      params: { q: query, limit },
    });
    return response.data;
  },

  // Get book details
  getBook: async (bookId: string): Promise<Book> => {
    const response = await apiClient.get<Book>(`/books/${bookId}`);
    return response.data;
  },

  // Get book recommendations
  getRecommendations: async (
    bookId: string,
    method: "content" | "collaborative" | "hybrid" = "content",
    limit: number = 10
  ): Promise<RecommendationResponse> => {
    const response = await apiClient.get<RecommendationResponse>(
      `/books/${bookId}/recommendations`,
      {
        params: { method, limit },
      }
    );
    return response.data;
  },

  // Get popular books
  getPopularBooks: async (
    limit: number = 20
  ): Promise<PopularBooksResponse> => {
    const response = await apiClient.get<PopularBooksResponse>(
      "/books/popular",
      {
        params: { limit },
      }
    );
    return response.data;
  },

  // Get filtered recommendations
  getFilteredRecommendations: async (
    filters: FilterRequest
  ): Promise<FilteredRecommendationResponse> => {
    const response = await apiClient.post<FilteredRecommendationResponse>(
      "/recommendations/filter",
      filters
    );
    return response.data;
  },
};

export default api;
