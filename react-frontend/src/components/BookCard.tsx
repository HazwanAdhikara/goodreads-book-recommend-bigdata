import React from "react";
import { Link } from "react-router-dom";
import { Star, Calendar, User, BookOpen } from "lucide-react";
import { Book } from "../types";
import { formatRating, getRatingBadgeColor, truncateText } from "../utils";

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
  const rating =
    typeof book.rating === "string"
      ? parseFloat(book.rating.replace(",", "."))
      : book.rating;

  return (
    <div className="card group">
      {/* Book Cover Placeholder */}
      <div className="aspect-[3/4] bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center relative">
        <BookOpen className="h-12 w-12 text-white opacity-80" />

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
          <Link to={`/book/${book.id}`}>{book.name}</Link>
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
