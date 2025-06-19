import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { BookOpen, TrendingUp, Users, Star } from "lucide-react";
import { api } from "../services/api";
import { Book, HealthResponse } from "../types";
import { formatRating, getRatingBadgeColor, truncateText } from "../utils";
import BookCard from "./BookCard";
import LoadingSpinner from "./LoadingSpinner";

const HomePage: React.FC = () => {
  const [popularBooks, setPopularBooks] = useState<Book[]>([]);
  const [healthData, setHealthData] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHomeData = async () => {
      try {
        setLoading(true);

        // Fetch health data and popular books in parallel
        const [healthResponse, popularResponse] = await Promise.all([
          api.health(),
          api.getPopularBooks(12),
        ]);

        setHealthData(healthResponse);
        setPopularBooks(popularResponse.books);
      } catch (err) {
        console.error("Error fetching home data:", err);
        setError("Failed to load data. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchHomeData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-96">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 text-lg mb-4">{error}</div>
        <button
          onClick={() => window.location.reload()}
          className="btn-primary"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12 bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl text-white">
        <div className="max-w-4xl mx-auto px-6">
          <BookOpen className="h-16 w-16 mx-auto mb-6 opacity-90" />
          <h1 className="text-4xl font-bold mb-4">
            Discover Your Next Great Read
          </h1>
          <p className="text-xl mb-8 opacity-90">
            Get personalized book recommendations powered by advanced machine
            learning
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/search" className="btn-secondary">
              Search Books
            </Link>
            <Link
              to="/recommendations"
              className="btn-primary bg-white text-primary-600 hover:bg-gray-100"
            >
              Get Recommendations
            </Link>
          </div>
        </div>
      </section>

      {/* System Status */}
      {healthData && (
        <section className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <TrendingUp className="h-6 w-6 mr-2 text-primary-600" />
            System Status
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div className="text-3xl font-bold text-primary-600">
                {healthData.total_books.toLocaleString()}
              </div>
              <div className="text-gray-600">Total Books</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div
                className={`text-3xl font-bold ${
                  healthData.model_loaded ? "text-green-600" : "text-red-600"
                }`}
              >
                {healthData.model_loaded ? "Active" : "Inactive"}
              </div>
              <div className="text-gray-600">ML Model</div>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <div
                className={`text-3xl font-bold ${
                  healthData.data_loaded ? "text-green-600" : "text-red-600"
                }`}
              >
                {healthData.data_loaded ? "Ready" : "Loading"}
              </div>
              <div className="text-gray-600">Data Status</div>
            </div>
          </div>
        </section>
      )}

      {/* Popular Books */}
      <section>
        <div className="flex items-center justify-between mb-8">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            <Star className="h-6 w-6 mr-2 text-primary-600" />
            Popular Books
          </h2>
          <Link
            to="/search"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            View All →
          </Link>
        </div>

        {popularBooks.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {popularBooks.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            No popular books available at the moment.
          </div>
        )}
      </section>

      {/* Features */}
      <section className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">
          How It Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-primary-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
              <BookOpen className="h-8 w-8 text-primary-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Choose a Book</h3>
            <p className="text-gray-600">
              Search or select from our collection of books to get started
            </p>
          </div>
          <div className="text-center">
            <div className="bg-primary-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
              <TrendingUp className="h-8 w-8 text-primary-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">AI Analysis</h3>
            <p className="text-gray-600">
              Our ML model analyzes content, ratings, and metadata for
              similarity
            </p>
          </div>
          <div className="text-center">
            <div className="bg-primary-100 rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
              <Star className="h-8 w-8 text-primary-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Get Recommendations</h3>
            <p className="text-gray-600">
              Receive personalized book recommendations tailored to your taste
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
