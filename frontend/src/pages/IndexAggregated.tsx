/**
 * Main Dashboard Page - API-Powered Real-Time Aggregation
 * Data flow: SQLite Database → FastAPI Backend → React Frontend
 * No CSV files needed - all data fetched via REST API endpoints
 * Supports 1M+ records with efficient server-side aggregation
 */

import { useState, useEffect } from "react";
import { Header } from "@/components/dashboard/Header";
import { FilterSidebar } from "@/components/dashboard/FilterSidebar";
import { OverviewTabAggregated } from "@/components/tabs/OverviewTabAggregated";
import { RecommendationsTabAggregated } from "@/components/tabs/RecommendationsTabAggregated";
import { InjuryAnalysisTabAggregated } from "@/components/tabs/InjuryAnalysisTabAggregated";
import { AdjusterPerformanceTabAggregated } from "@/components/tabs/AdjusterPerformanceTabAggregated";
import { ModelPerformanceTabAggregated } from "@/components/tabs/ModelPerformanceTabAggregated";
import RecalibrationTab from "@/components/tabs/RecalibrationTab";
import { useAggregatedClaimsDataAPI } from "@/hooks/useAggregatedClaimsDataAPI";
import { FilterState } from "@/types/claims";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertCircle, Loader2 } from "lucide-react";
import axios from "axios";
import { ErrorBoundary, TabErrorFallback } from "@/components/ErrorBoundary";

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const IndexAggregated = () => {
  const { data, kpis, filterOptions, isLoading, error } = useAggregatedClaimsDataAPI();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  // Lazy load raw claims only when recalibration tab is active
  const [rawClaims, setRawClaims] = useState<any[]>([]);
  const [rawLoading, setRawLoading] = useState(false);
  const [rawError, setRawError] = useState<string | null>(null);

  useEffect(() => {
    if (activeTab === "recalibration" && rawClaims.length === 0 && !rawLoading) {
      setRawLoading(true);
      axios.get(`${API_BASE_URL}/claims/claims/full`, { timeout: 60000 })
        .then(response => {
          // Extract the claims array from the response
          const claims = response.data.claims || response.data;
          setRawClaims(Array.isArray(claims) ? claims : []);
          setRawLoading(false);
        })
        .catch(err => {
          setRawError(err.message);
          setRawLoading(false);
        });
    }
  }, [activeTab]);

  // Global filter state
  const [filters, setFilters] = useState<FilterState>({
    version: 'all',  // NEW: Version filter
    injuryGroupCode: 'all',
    county: 'all',
    severityScore: 'all',
    cautionLevel: 'all',
    venueRating: 'all',
    impact: 'all',
    year: 'all',
  });

  const handleFilterChange = (key: keyof FilterState, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading aggregated claims data from API...</p>
          <p className="text-xs text-muted-foreground mt-2">
            (Real-time aggregation from SQLite database)
          </p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <p className="text-lg font-semibold mb-2 text-destructive">Error loading data</p>
          <p className="text-sm text-muted-foreground mb-4">{error}</p>
          <div className="bg-muted p-4 rounded-lg text-left text-sm space-y-2">
            <p className="font-semibold">To fix this:</p>
            <ol className="list-decimal list-inside space-y-1">
              <li>Make sure the backend API is running at <code className="bg-background px-2 py-1 rounded">http://localhost:8000</code></li>
              <li>Check the backend terminal for errors</li>
              <li>Verify the database exists at <code className="bg-background px-2 py-1 rounded">backend/app/db/claims_analytics.db</code></li>
              <li>If needed, run migration: <code className="bg-background px-2 py-1 rounded">python migrate_csv_to_sqlite.py</code></li>
            </ol>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gradient-subtle overflow-hidden">
      {/* Left Sidebar with Filters */}
      <FilterSidebar
        filters={filters}
        counties={filterOptions?.counties || []}
        years={filterOptions?.years?.map(String) || []}
        injuryGroups={filterOptions?.injuryGroups || []}
        venueRatings={filterOptions?.venueRatings || []}
        impactLevels={[1, 2, 3, 4, 5]}
        onFilterChange={handleFilterChange}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

        <main className="flex-1 overflow-auto">
          <div className="container mx-auto px-4 py-6">
            <div className="mb-6">
              <h2 className="text-2xl font-bold mb-2">Claims Variance Analytics Dashboard</h2>
              <p className="text-muted-foreground">
                Analyzing {kpis.totalClaims.toLocaleString()} claims from aggregated data
              </p>
            </div>

            <Tabs defaultValue="overview" className="w-full" onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-6 mb-6">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
                <TabsTrigger value="injury">Injury Analysis</TabsTrigger>
                <TabsTrigger value="adjuster">Adjuster Performance</TabsTrigger>
                <TabsTrigger value="model">Model Performance</TabsTrigger>
                <TabsTrigger value="recalibration">Weight Recalibration</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                <ErrorBoundary
                  componentName="Overview Tab"
                  fallback={<TabErrorFallback tabName="Overview" />}
                >
                  <OverviewTabAggregated data={data} kpis={kpis} filterOptions={filterOptions} />
                </ErrorBoundary>
              </TabsContent>

              <TabsContent value="recommendations" className="space-y-4">
                <ErrorBoundary
                  componentName="Recommendations Tab"
                  fallback={<TabErrorFallback tabName="Recommendations" />}
                >
                  <RecommendationsTabAggregated data={data} />
                </ErrorBoundary>
              </TabsContent>

              <TabsContent value="injury" className="space-y-4">
                <ErrorBoundary
                  componentName="Injury Analysis Tab"
                  fallback={<TabErrorFallback tabName="Injury Analysis" />}
                >
                  <InjuryAnalysisTabAggregated data={data} />
                </ErrorBoundary>
              </TabsContent>

              <TabsContent value="adjuster" className="space-y-4">
                <ErrorBoundary
                  componentName="Adjuster Performance Tab"
                  fallback={<TabErrorFallback tabName="Adjuster Performance" />}
                >
                  <AdjusterPerformanceTabAggregated data={data} />
                </ErrorBoundary>
              </TabsContent>

              <TabsContent value="model" className="space-y-4">
                <ErrorBoundary
                  componentName="Model Performance Tab"
                  fallback={<TabErrorFallback tabName="Model Performance" />}
                >
                  <ModelPerformanceTabAggregated data={data} />
                </ErrorBoundary>
              </TabsContent>

              <TabsContent value="recalibration" className="space-y-4">
                {activeTab === "recalibration" && (
                  <ErrorBoundary
                    componentName="Weight Recalibration Tab"
                    fallback={<TabErrorFallback tabName="Weight Recalibration" />}
                  >
                    {rawLoading && (
                      <div className="flex items-center justify-center h-64">
                        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                        <span className="ml-3 text-lg">Loading raw claims data for recalibration...</span>
                      </div>
                    )}
                    {rawError && (
                      <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <AlertCircle className="h-6 w-6 text-yellow-600 mb-2" />
                        <p className="font-semibold text-yellow-900">Unable to load raw claims data</p>
                        <p className="text-sm text-yellow-700 mt-2">
                          Error: {rawError}. The recalibration feature requires the full dat.csv file.
                        </p>
                      </div>
                    )}
                    {!rawLoading && !rawError && rawClaims.length > 0 && (
                      <RecalibrationTab claims={rawClaims} />
                    )}
                  </ErrorBoundary>
                )}
              </TabsContent>
            </Tabs>
          </div>
        </main>
      </div>
    </div>
  );
};

export default IndexAggregated;
