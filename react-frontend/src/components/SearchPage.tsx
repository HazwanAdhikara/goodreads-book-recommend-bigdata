import React, { useState } from "react";
import { Search, Filter, X } from "lucide-react";
import { api } from "../services/api";
import { Book } from "../types";
import BookCard from "./BookCard";
import LoadingSpinner from "./LoadingSpinner";

const SearchPage: React.FC = () => {
  const [query, setQuery] = useState("");
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      setLoading(true);
      setError(null);

      const response = await api.searchBooks(query.trim(), 24);
      setBooks(response.results);
      setHasSearched(true);
    } catch (err) {
      console.error("Search error:", err);
      setError("Failed to search books. Please try again.");
      setBooks([]);
    } finally {
      setLoading(false);
    }
  };

  const clearSearch = () => {
    setQuery("");
    setBooks([]);
    setHasSearched(false);
    setError(null);
  };

  return (
    <div className="space-y-6">
      {/* Search Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Search Books</h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Search through our collection of books by title, author, or
          description
        </p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for books, authors, or topics..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="btn-primary px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {loading ? (
              <LoadingSpinner size="small" className="mr-2" />
            ) : (
              <Search className="h-4 w-4 mr-2" />
            )}
            Search
          </button>
          {hasSearched && (
            <button
              type="button"
              onClick={clearSearch}
              className="btn-secondary px-4 py-3 flex items-center"
            >
              <X className="h-4 w-4 mr-2" />
              Clear
            </button>
          )}
        </form>
      </div>

      {/* Search Results */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {loading && (
        <div className="flex justify-center py-12">
          <LoadingSpinner size="large" />
        </div>
      )}

      {hasSearched && !loading && books.length === 0 && !error && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg mb-2">No books found</div>
          <p className="text-gray-400">Try searching with different keywords</p>
        </div>
      )}

      {books.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              Search Results ({books.length} books found)
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {books.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchPage;
