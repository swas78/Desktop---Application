// For: Custom hook fetching summary, mismatch, and accuracy metrics for the dashboard
// Must never: Manipulate raw statistics or suppress API error states

import { useState, useEffect } from "react";
import { advsApi } from "../services/api-client";

export function useDashboardData() {
  const [summary, setSummary] = useState<any>(null);
  const [mismatches, setMismatches] = useState<any[]>([]);
  const [accuracy, setAccuracy] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [sumRes, misRes, accRes] = await Promise.all([
        advsApi.getDashboardSummary(),
        advsApi.getDashboardMismatches(),
        advsApi.getDashboardAccuracy(),
      ]);
      setSummary(sumRes);
      setMismatches(misRes);
      setAccuracy(accRes);
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard statistics.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  return { summary, mismatches, accuracy, isLoading, error, refetch: fetchMetrics };
}
