import React, { useEffect, useState } from "react";
import { TrendingUp, BookOpen } from "lucide-react";
import api from "../services/goodreads-api";
import { Book } from "../types/api";
import { formatRating } from "../utils/index";
import BookCard from "../components/BookCard";
import LoadingSpinner from "../components/LoadingSpinner";

const PopularBooksPage: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(24);

  useEffect(() => {
    const fetchPopularBooks = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await api.getPopularBooks(limit);
        setBooks(response.books);
      } catch (err) {
        console.error("Error fetching popular books:", err);
        setError("Failed to load popular books. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchPopularBooks();
  }, [limit]);

  const handleLoadMore = () => {
    setLimit((prev) => prev + 24);
  };

  if (loading && books.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <TrendingUp className="h-8 w-8 text-primary-600 mr-3" />
            <h1 className="text-3xl font-bold text-gray-900">Popular Books</h1>
          </div>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Discover the most popular and highly-rated books in our collection.
            These books are loved by readers around the world.
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8 text-center">
            <p className="text-red-600">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-2 btn btn-primary"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Books Grid */}
        {books.length > 0 ? (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
              {books.map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>

            {/* Load More Button */}
            {books.length >= 24 && (
              <div className="text-center">
                <button
                  onClick={handleLoadMore}
                  disabled={loading}
                  className="btn btn-primary"
                >
                  {loading ? "Loading..." : "Load More Books"}
                </button>
              </div>
            )}
          </>
        ) : (
          !loading && (
            <div className="text-center py-12">
              <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No popular books found.</p>
            </div>
          )
        )}

        {/* Stats */}
        {books.length > 0 && (
          <div className="mt-12 bg-white rounded-xl shadow-sm p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Collection Stats
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600">
                  {books.length}
                </div>
                <div className="text-sm text-gray-600">Books Shown</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600">
                  {formatRating(
                    books.reduce((sum, book) => sum + book.rating, 0) /
                      books.length
                  )}
                </div>
                <div className="text-sm text-gray-600">Average Rating</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-primary-600">
                  {books.filter((book) => book.rating >= 4.0).length}
                </div>
                <div className="text-sm text-gray-600">Highly Rated (4.0+)</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PopularBooksPage;
