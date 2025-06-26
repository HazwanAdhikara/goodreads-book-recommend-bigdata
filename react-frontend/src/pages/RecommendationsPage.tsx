import React, { useState } from "react";
import { Search, Star, BookOpen, Loader2 } from "lucide-react";
import api from "../services/goodreads-api";
import { Book, Recommendation } from "../types/api";
import { formatRating } from "../utils/index";
import BookCard from "../components/BookCard";
import LoadingSpinner from "../components/LoadingSpinner";

const RecommendationsPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Book[]>([]);
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [recommendationsLoading, setRecommendationsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [recommendationMethod, setRecommendationMethod] = useState<
    "content" | "collaborative" | "hybrid"
  >("hybrid");

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    try {
      setLoading(true);
      setError(null);
      setHasSearched(true);

      const response = await api.searchBooks(searchQuery.trim(), 12);
      setSearchResults(response.results);
    } catch (err) {
      console.error("Search error:", err);
      setError("Failed to search books. Please try again.");
      setSearchResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleBookSelect = async (book: Book) => {
    setSelectedBook(book);
    setRecommendationsLoading(true);
    setError(null);

    try {
      const response = await api.getRecommendations(
        book.book_id,
        recommendationMethod,
        12
      );
      setRecommendations(response.recommendations);
    } catch (err) {
      console.error("Recommendations error:", err);
      setError("Failed to get recommendations. Please try again.");
      setRecommendations([]);
    } finally {
      setRecommendationsLoading(false);
    }
  };

  const handleMethodChange = async (
    method: "content" | "collaborative" | "hybrid"
  ) => {
    if (!selectedBook || method === recommendationMethod) return;

    setRecommendationMethod(method);
    setRecommendationsLoading(true);

    try {
      const response = await api.getRecommendations(
        selectedBook.book_id,
        method,
        12
      );
      setRecommendations(response.recommendations);
    } catch (err) {
      console.error("Error fetching recommendations:", err);
      setError("Failed to get recommendations. Please try again.");
    } finally {
      setRecommendationsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Get Book Recommendations
          </h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Search for a book you like and get personalized recommendations
            using our advanced recommendation system.
          </p>
        </div>

        {/* Search Form */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for a book to get recommendations..."
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <button
                type="submit"
                disabled={loading || !searchQuery.trim()}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 btn btn-primary py-2"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  "Search"
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8 text-center">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Search Results */}
        {hasSearched && !selectedBook && (
          <div className="bg-white rounded-xl shadow-sm overflow-hidden mb-8">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Select a Book for Recommendations
              </h2>

              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <LoadingSpinner />
                </div>
              ) : searchResults.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {searchResults.map((book) => (
                    <div
                      key={book.id}
                      onClick={() => handleBookSelect(book)}
                      className="cursor-pointer transform transition-transform duration-200 hover:scale-105"
                    >
                      <BookCard book={book} />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">
                    {hasSearched
                      ? "No books found. Try a different search term."
                      : "Search for books to get started."}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Selected Book and Recommendations */}
        {selectedBook && (
          <>
            {/* Selected Book */}
            <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">
                  Recommendations for:
                </h2>
                <button
                  onClick={() => {
                    setSelectedBook(null);
                    setRecommendations([]);
                    setError(null);
                  }}
                  className="text-gray-500 hover:text-gray-700 text-sm"
                >
                  Change Book
                </button>
              </div>

              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-16 h-20 bg-gradient-to-br from-primary-400 to-primary-600 rounded flex items-center justify-center">
                    <BookOpen className="h-6 w-6 text-white opacity-80" />
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">
                    {selectedBook.name}
                  </h3>
                  <p className="text-gray-600 text-sm">
                    {selectedBook.authors}
                  </p>
                  <div className="flex items-center mt-1">
                    <Star className="h-4 w-4 text-yellow-400 mr-1" />
                    <span className="text-sm font-medium text-gray-900">
                      {formatRating(selectedBook.rating)}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Recommended Books
                  </h2>

                  {/* Method Selector */}
                  <div className="flex bg-gray-100 rounded-lg p-1">
                    {[
                      { key: "hybrid", label: "Hybrid" },
                      { key: "content", label: "Content" },
                      { key: "collaborative", label: "Collaborative" },
                    ].map((method) => (
                      <button
                        key={method.key}
                        onClick={() =>
                          handleMethodChange(
                            method.key as "content" | "collaborative" | "hybrid"
                          )
                        }
                        className={`px-3 py-1 rounded-md text-sm font-medium transition-colors duration-200 ${
                          recommendationMethod === method.key
                            ? "bg-white text-primary-600 shadow-sm"
                            : "text-gray-600 hover:text-gray-900"
                        }`}
                      >
                        {method.label}
                      </button>
                    ))}
                  </div>
                </div>

                {recommendationsLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <LoadingSpinner />
                  </div>
                ) : recommendations.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {recommendations.map((rec) => (
                      <div key={rec.book_id} className="relative">
                        <BookCard
                          book={{
                            id: rec.book_id.toString(),
                            book_id: rec.book_id.toString(),
                            name: rec.name,
                            authors: rec.authors,
                            rating: rec.rating,
                            description: rec.description,
                            publisher: "",
                            publish_year: "",
                            pages: "",
                          }}
                        />
                        {rec.similarity_score && (
                          <div className="absolute top-2 right-2 bg-primary-600 text-white px-2 py-1 rounded-full text-xs font-medium">
                            {Math.round(rec.similarity_score * 100)}% match
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">
                      No recommendations available for this book.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default RecommendationsPage;
