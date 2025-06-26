import React from "react";
import { Link } from "react-router-dom";
import { Star, Calendar, User, BookOpen } from "lucide-react";
import { Book } from "../types/api";
import {
  formatRating,
  getRatingBadgeColor,
  truncateText,
} from "../utils/index";

interface BookCardProps {
  book: Book;
  showRecommendationButton?: boolean;
  recommendationType?: string;
  similarity?: number;
}

const BookCard: React.FC<BookCardProps> = ({
  book,
  showRecommendationButton = false,
  recommendationType,
  similarity,
}) => {
  const rating = book.rating || 0;

  // Generate consistent color based on book ID for variety
  const getBookCoverStyle = (bookId: string, title: string) => {
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

    const patterns = [
      "", // solid gradient
      "bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))]",
      "bg-[conic-gradient(from_0deg,_var(--tw-gradient-stops))]",
    ];

    // Use book ID to consistently pick the same color/pattern
    const colorIndex = parseInt(bookId.slice(-1)) % colors.length;
    const patternIndex = parseInt(bookId.slice(-2)) % patterns.length;

    return {
      gradient: colors[colorIndex],
      pattern: patterns[patternIndex],
    };
  };

  const coverStyle = getBookCoverStyle(book.book_id, book.name);

  return (
    <div className="card group">
      {/* Book Cover with Title */}
      <div
        className={`aspect-[3/4] bg-gradient-to-br ${coverStyle.gradient} ${coverStyle.pattern} flex flex-col items-center justify-center relative p-4 text-center`}
      >
        {/* Book Title on Cover */}
        <div className="text-white font-bold text-sm leading-tight mb-2 line-clamp-4 shadow-text">
          {book.name.length > 50
            ? book.name.substring(0, 50) + "..."
            : book.name}
        </div>

        {/* Decorative Book Icon */}
        <BookOpen className="h-8 w-8 text-white opacity-60 mt-auto" />

        {/* Recommendation Badge */}
        {recommendationType && (
          <div className="absolute top-2 right-2">
            <span className="badge badge-primary text-xs">
              {recommendationType}
            </span>
          </div>
        )}

        {/* Similarity Score */}
        {similarity && (
          <div className="absolute bottom-2 left-2">
            <span className="bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
              {Math.round(similarity * 100)}% match
            </span>
          </div>
        )}
      </div>

      {/* Book Info */}
      <div className="p-4 flex-1 flex flex-col">
        <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-primary-600 transition-colors">
          <Link to={`/book/${book.book_id}`}>{book.name}</Link>
        </h3>

        <div className="flex items-center text-sm text-gray-600 mb-2">
          <User className="h-4 w-4 mr-1" />
          <span className="truncate">{book.authors}</span>
        </div>

        <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
          <div className="flex items-center">
            <Calendar className="h-4 w-4 mr-1" />
            <span>{book.publish_year}</span>
          </div>
          <div className="flex items-center">
            <Star className="h-4 w-4 mr-1 text-yellow-500 fill-current" />
            <span className={getRatingBadgeColor(rating).split(" ")[1]}>
              {formatRating(rating)}
            </span>
          </div>
        </div>

        <p className="text-sm text-gray-600 mb-4 flex-1">
          {truncateText(book.description, 100)}
        </p>

        <div className="flex items-center justify-between">
          <div className="text-xs text-gray-500">{book.publisher}</div>

          {showRecommendationButton && (
            <Link
              to={`/book/${book.id}`}
              className="text-primary-600 hover:text-primary-700 text-sm font-medium"
            >
              View Details →
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};

export default BookCard;
