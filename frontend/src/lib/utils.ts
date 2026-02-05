import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Helper to safely get colors as an array (handles various formats from AI)
export const normalizeColors = (colors: unknown): Array<{ hex: string; role?: string; name?: string }> => {
  if (!colors) return [];
  if (Array.isArray(colors)) return colors;
  // If it's an object with color keys, convert to array
  if (typeof colors === 'object') {
    const colorObj = colors as Record<string, string>;
    return Object.entries(colorObj).map(([role, hex]) => ({
      hex: typeof hex === 'string' ? hex : '#888888',
      role,
      name: role,
    }));
  }
  // If it's a comma-separated string
  if (typeof colors === 'string') {
    return colors.split(',').map((hex, i) => ({
      hex: hex.trim(),
      role: i === 0 ? 'primary' : i === 1 ? 'secondary' : 'accent',
      name: `Color ${i + 1}`,
    }));
  }
  return [];
};
