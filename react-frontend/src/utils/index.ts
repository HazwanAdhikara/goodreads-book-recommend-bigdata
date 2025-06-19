import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function truncateText(text: string, maxLength: number = 150): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + "...";
}

export function formatRating(rating: number): string {
  return rating.toFixed(1);
}

export function getRatingColor(rating: number): string {
  if (rating >= 4.5) return "text-green-600";
  if (rating >= 4.0) return "text-blue-600";
  if (rating >= 3.5) return "text-yellow-600";
  if (rating >= 3.0) return "text-orange-600";
  return "text-red-600";
}

export function getRatingBadgeColor(rating: number): string {
  if (rating >= 4.5) return "bg-green-100 text-green-800";
  if (rating >= 4.0) return "bg-blue-100 text-blue-800";
  if (rating >= 3.5) return "bg-yellow-100 text-yellow-800";
  if (rating >= 3.0) return "bg-orange-100 text-orange-800";
  return "bg-red-100 text-red-800";
}
