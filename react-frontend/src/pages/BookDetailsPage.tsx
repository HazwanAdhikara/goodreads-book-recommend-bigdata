import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  ArrowLeft,
  Star,
  Calendar,
  User,
  BookOpen,
  Loader2,
} from "lucide-react";
import api from "../services/goodreads-api";
import { Book, Recommendation } from "../types/api";
import { formatRating, getRatingBadgeColor } from "../utils/index";
import BookCard from "../components/BookCard";
import LoadingSpinner from "../components/LoadingSpinner";

const BookDetailsPage: React.FC = () => {
  const { bookId } = useParams<{ bookId: string }>();
  const navigate = useNavigate();
  const [book, setBook] = useState<Book | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [recommendationsLoading, setRecommendationsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recommendationMethod, setRecommendationMethod] = useState<
    "content" | "collaborative" | "hybrid"
  >("hybrid");

  useEffect(() => {
    if (!bookId) {
      navigate("/");
      return;
    }

    const fetchBookDetails = async () => {
      try {
        setLoading(true);
        setError(null);

        // First, fetch just the book details quickly
        const bookData = await api.getBookDetails(bookId);
        setBook(bookData);
        setLoading(false); // Show book details immediately

        // Then fetch recommendations separately
        setRecommendationsLoading(true);
        try {
          const recData = await api.getRecommendations(
            bookId,
            recommendationMethod,
            6 // Reduced from 12 to 6 for faster loading
          );
          setRecommendations(recData.recommendations);
        } catch (recError) {
          console.error("Error fetching recommendations:", recError);
          // Don't show error for recommendations failure, just show empty state
          setRecommendations([]);
        }
      } catch (err) {
        console.error("Error fetching book details:", err);
        setError("Failed to load book details. Please try again.");
        setLoading(false);
      } finally {
        setRecommendationsLoading(false);
      }
    };

    fetchBookDetails();
  }, [bookId, navigate]); // Removed recommendationMethod from dependencies

  const handleMethodChange = async (
    method: "content" | "collaborative" | "hybrid"
  ) => {
    if (!bookId || method === recommendationMethod) return;

    setRecommendationMethod(method);
    setRecommendationsLoading(true);

    try {
      const recData = await api.getRecommendations(bookId, method, 6); // Reduced to 6
      setRecommendations(recData.recommendations);
    } catch (err) {
      console.error("Error fetching recommendations:", err);
      setRecommendations([]); // Show empty state on error
    } finally {
      setRecommendationsLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (error || !book) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Book Not Found
          </h1>
          <p className="text-gray-600 mb-6">
            {error || "The requested book could not be found."}
          </p>
          <button onClick={() => navigate("/")} className="btn btn-primary">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  const rating = book.rating || 0;

  // Generate book cover style
  const getBookCoverStyle = (bookId: string) => {
    const colors = [
      "from-blue-500 to-blue-700",
      "from-green-500 to-green-700",
      "from-purple-500 to-purple-700",
      "from-red-500 to-red-700",
      "from-indigo-500 to-indigo-700",
      "from-pink-500 to-pink-700",
      "from-yellow-500 to-yellow-600",
      "from-teal-500 to-teal-700",
      "from-orange-500 to-orange-700",
      "from-cyan-500 to-cyan-700",
    ];

    const colorIndex = parseInt(bookId.slice(-1)) % colors.length;
    return colors[colorIndex];
  };

  const coverGradient = getBookCoverStyle(book.book_id);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <button
          onClick={() => navigate(-1)}
          className="mb-6 flex items-center text-gray-600 hover:text-gray-900 transition-colors duration-200"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </button>

        {/* Book Details */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden mb-8">
          <div className="p-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Book Cover */}
              <div className="lg:col-span-1">
                <div
                  className={`aspect-[3/4] bg-gradient-to-br ${coverGradient} rounded-lg flex flex-col items-center justify-center p-6 text-center relative`}
                >
                  {/* Book Title on Cover */}
                  <div className="text-white font-bold text-lg leading-tight mb-4 shadow-text">
                    {book.name.length > 60
                      ? book.name.substring(0, 60) + "..."
                      : book.name}
                  </div>

                  {/* Author on Cover */}
                  <div className="text-white text-sm opacity-90 mb-4 shadow-text">
                    by{" "}
                    {book.authors.length > 30
                      ? book.authors.substring(0, 30) + "..."
                      : book.authors}
                  </div>

                  {/* Decorative Book Icon */}
                  <BookOpen className="h-16 w-16 text-white opacity-60 mt-auto" />

                  {/* Rating Badge on Cover */}
                  <div className="absolute top-3 right-3 bg-black bg-opacity-50 text-white px-2 py-1 rounded-full text-xs font-medium">
                    ★ {formatRating(rating)}
                  </div>
                </div>
              </div>

              {/* Book Info */}
              <div className="lg:col-span-2">
                <h1 className="text-3xl font-bold text-gray-900 mb-4">
                  {book.name}
                </h1>

                <div className="space-y-4 mb-6">
                  <div className="flex items-center text-gray-600">
                    <User className="h-5 w-5 mr-2" />
                    <span className="font-medium">Authors:</span>
                    <span className="ml-2">{book.authors}</span>
                  </div>

                  {book.publisher && (
                    <div className="flex items-center text-gray-600">
                      <BookOpen className="h-5 w-5 mr-2" />
                      <span className="font-medium">Publisher:</span>
                      <span className="ml-2">{book.publisher}</span>
                    </div>
                  )}

                  {book.publish_year && (
                    <div className="flex items-center text-gray-600">
                      <Calendar className="h-5 w-5 mr-2" />
                      <span className="font-medium">Published:</span>
                      <span className="ml-2">{book.publish_year}</span>
                    </div>
                  )}

                  <div className="flex items-center">
                    <Star className="h-5 w-5 text-yellow-400 mr-2" />
                    <span className="font-semibold text-gray-900 mr-2">
                      {formatRating(rating)}
                    </span>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getRatingBadgeColor(
                        rating
                      )}`}
                    >
                      {rating >= 4.5
                        ? "Excellent"
                        : rating >= 4.0
                        ? "Very Good"
                        : rating >= 3.5
                        ? "Good"
                        : rating >= 3.0
                        ? "Average"
                        : "Below Average"}
                    </span>
                    {book.rating_count && (
                      <span className="ml-2 text-gray-500 text-sm">
                        ({book.rating_count.toLocaleString()} ratings)
                      </span>
                    )}
                  </div>
                </div>

                {/* Description */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">
                    Description
                  </h3>
                  <p className="text-gray-700 leading-relaxed">
                    {book.description ||
                      "No description available for this book."}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recommendations Section */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="p-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                Recommendations
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
                    className={`px-4 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
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
                <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
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
      </div>
    </div>
  );
};

export default BookDetailsPage;
