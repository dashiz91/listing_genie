import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { apiClient, CreditsInfo } from '@/api/client';
import { useAuth } from './AuthContext';

interface CreditContextType {
  credits: CreditsInfo | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  // Convenience getters
  balance: number;
  isAdmin: boolean;
  planTier: string;
  planName: string;
  // Credit usage tracking
  lastUsage: CreditUsage | null;
  recordUsage: (usage: CreditUsage) => void;
  clearUsage: () => void;
}

export interface CreditUsage {
  operation: string;
  creditsUsed: number;
  newBalance: number;
  isAdmin: boolean;
  timestamp: number;
}

const CreditContext = createContext<CreditContextType | undefined>(undefined);

export const CreditProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const [credits, setCredits] = useState<CreditsInfo | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUsage, setLastUsage] = useState<CreditUsage | null>(null);

  // Track if we've fetched to avoid duplicate calls
  const hasFetched = useRef(false);

  const fetchCredits = useCallback(async () => {
    if (!user) {
      setCredits(null);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const data = await apiClient.getCredits();
      setCredits(data);
    } catch (err) {
      console.error('Failed to fetch credits:', err);
      setError('Failed to load credits');
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  // Fetch credits when user changes
  useEffect(() => {
    if (user && !hasFetched.current) {
      hasFetched.current = true;
      fetchCredits();
    } else if (!user) {
      hasFetched.current = false;
      setCredits(null);
    }
  }, [user, fetchCredits]);

  // Record credit usage (called after generation)
  const recordUsage = useCallback((usage: CreditUsage) => {
    setLastUsage(usage);
    // Also update local balance immediately for responsiveness
    if (credits && !usage.isAdmin) {
      setCredits(prev => prev ? { ...prev, balance: usage.newBalance } : prev);
    }
  }, [credits]);

  // Clear usage (after toast is dismissed)
  const clearUsage = useCallback(() => {
    setLastUsage(null);
  }, []);

  // Convenience getters with defaults
  const balance = credits?.balance ?? 0;
  const isAdmin = credits?.is_admin ?? false;
  const planTier = credits?.plan_tier ?? 'free';
  const planName = credits?.plan_name ?? 'Free';

  return (
    <CreditContext.Provider
      value={{
        credits,
        isLoading,
        error,
        refetch: fetchCredits,
        balance,
        isAdmin,
        planTier,
        planName,
        lastUsage,
        recordUsage,
        clearUsage,
      }}
    >
      {children}
    </CreditContext.Provider>
  );
};

export const useCredits = (): CreditContextType => {
  const context = useContext(CreditContext);
  if (context === undefined) {
    throw new Error('useCredits must be used within a CreditProvider');
  }
  return context;
};

// Hook for estimating costs
export const useCreditCost = () => {
  const { balance, isAdmin } = useCredits();

  const estimateCost = useCallback((operation: string, model: string = 'gemini-3-pro-image-preview') => {
    // Model costs
    const modelCost = model.includes('flash') ? 1 : 3;

    // Calculate based on operation
    switch (operation) {
      case 'framework':
        // 1 analysis + 4 previews (Flash)
        return { total: 5, breakdown: { analysis: 1, previews: 4 } };

      case 'listing_images':
        // 6 listing images
        return { total: 6 * modelCost, breakdown: { images: 6 * modelCost } };

      case 'full_listing':
        // Analysis (1) + Previews (4) + Listing (6) + A+ Desktop (6) + A+ Mobile (6)
        const listingCost = 6 * modelCost;
        const aplusDesktopCost = 6 * modelCost;
        const aplusMobileCost = 6; // Always 1 credit each
        return {
          total: 1 + 4 + listingCost + aplusDesktopCost + aplusMobileCost,
          breakdown: {
            analysis: 1,
            previews: 4,
            listing: listingCost,
            aplus_desktop: aplusDesktopCost,
            aplus_mobile: aplusMobileCost,
          }
        };

      case 'single_image':
        return { total: modelCost, breakdown: { image: modelCost } };

      case 'edit':
        return { total: 1, breakdown: { edit: 1 } };

      case 'aplus_module':
        return { total: modelCost, breakdown: { module: modelCost } };

      case 'aplus_mobile':
        return { total: 1, breakdown: { transform: 1 } };

      default:
        return { total: modelCost, breakdown: { unknown: modelCost } };
    }
  }, []);

  const canAfford = useCallback((cost: number) => {
    if (isAdmin) return true;
    return balance >= cost;
  }, [balance, isAdmin]);

  const getSuggestion = useCallback((cost: number, currentModel: string) => {
    if (isAdmin) return null;
    if (balance >= cost) return null;

    // If using Pro and can't afford, check if Flash would work
    if (currentModel.includes('pro')) {
      const flashCost = Math.ceil(cost / 3); // Rough estimate
      if (balance >= flashCost) {
        return {
          type: 'switch_model',
          message: `Switch to Flash (${flashCost} credits) to fit your budget`,
          flashCost,
        };
      }
    }

    return {
      type: 'upgrade',
      message: `You need ${cost - balance} more credits`,
      deficit: cost - balance,
    };
  }, [balance, isAdmin]);

  return { estimateCost, canAfford, getSuggestion };
};
