import axios from "axios";
import {
  Book,
  SearchResponse,
  PopularBooksResponse,
  RecommendationResponse,
  AuthorRecommendationResponse,
  HealthResponse,
} from "../types/api";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5001";

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

const api = {
  // Health check
  healthCheck: async (): Promise<HealthResponse> => {
    const response = await apiClient.get("/health");
    return response.data;
  },

  // Search books
  searchBooks: async (
    query: string,
    limit: number = 20
  ): Promise<SearchResponse> => {
    const response = await apiClient.get("/books/search", {
      params: { q: query, limit },
    });
    return response.data;
  },

  // Get popular books
  getPopularBooks: async (
    limit: number = 20
  ): Promise<PopularBooksResponse> => {
    const response = await apiClient.get("/books/popular", {
      params: { limit },
    });
    return response.data;
  },

  // Get book details
  getBookDetails: async (bookId: string): Promise<Book> => {
    const response = await apiClient.get(`/books/${bookId}`);
    return response.data;
  },

  // Get book recommendations
  getRecommendations: async (
    bookId: string,
    method: "content" | "collaborative" | "hybrid" = "content",
    limit: number = 10
  ): Promise<RecommendationResponse> => {
    const response = await apiClient.get(`/books/${bookId}/recommendations`, {
      params: { method, limit },
    });
    return response.data;
  },

  // Get author recommendations
  getAuthorRecommendations: async (
    author: string,
    limit: number = 10
  ): Promise<AuthorRecommendationResponse> => {
    const response = await apiClient.get(
      `/books/author/${encodeURIComponent(author)}/recommendations`,
      {
        params: { limit },
      }
    );
    return response.data;
  },
};

export default api;
