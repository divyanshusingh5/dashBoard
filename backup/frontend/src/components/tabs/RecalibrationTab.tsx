import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Alert, AlertDescription } from '../ui/alert';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Download, RefreshCw, TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-react';
import { ClaimData, WeightConfig } from '../../types/claims';
import { useWeightsData } from '../../hooks/useWeightsData';
import {
  recalibrateAllClaims,
  calculateFactorImpact,
  generateOptimizationRecommendations,
  exportWeightsToCSV,
} from '../../utils/recalibrationEngine';
import WeightAdjustmentPanel from '../recalibration/WeightAdjustmentPanel';
import RecalibrationMetricsCard from '../recalibration/RecalibrationMetricsCard';
import FactorImpactChart from '../recalibration/FactorImpactChart';
import OptimizationRecommendations from '../recalibration/OptimizationRecommendations';
import SensitivityAnalysisChart from '../recalibration/SensitivityAnalysisChart';
import BeforeAfterComparison from '../recalibration/BeforeAfterComparison';
import AdvancedOptimization from '../recalibration/AdvancedOptimization';
import FactorWeightImpactAnalyzer from '../recalibration/FactorWeightImpactAnalyzer';
import SingleInjuryRecalibration from '../recalibration/SingleInjuryRecalibration';

interface RecalibrationTabProps {
  claims: ClaimData[];
}

export default function RecalibrationTab({ claims }: RecalibrationTabProps) {
  const { weights, loading: weightsLoading, error: weightsError } = useWeightsData();
  const [adjustedWeights, setAdjustedWeights] = useState<Map<string, number>>(new Map());
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Create weight maps
  const originalWeightMap = useMemo(() => {
    const map = new Map<string, number>();
    weights.forEach((w) => map.set(w.factor_name, w.base_weight));
    return map;
  }, [weights]);

  const currentWeightMap = useMemo(() => {
    const map = new Map(originalWeightMap);
    adjustedWeights.forEach((value, key) => map.set(key, value));
    return map;
  }, [originalWeightMap, adjustedWeights]);

  // Calculate recalibration results
  const recalibrationResults = useMemo(() => {
    if (claims.length === 0 || originalWeightMap.size === 0) {
      return null;
    }

    return recalibrateAllClaims(claims, originalWeightMap, currentWeightMap);
  }, [claims, originalWeightMap, currentWeightMap]);

  // Calculate factor impacts
  const factorImpacts = useMemo(() => {
    if (claims.length === 0 || currentWeightMap.size === 0) {
      return new Map();
    }

    return calculateFactorImpact(claims, currentWeightMap);
  }, [claims, currentWeightMap]);

  // Generate recommendations
  const recommendations = useMemo(() => {
    if (claims.length === 0 || weights.length === 0) {
      return [];
    }

    return generateOptimizationRecommendations(claims, weights, factorImpacts);
  }, [claims, weights, factorImpacts]);

  // Filter weights by category
  const filteredWeights = useMemo(() => {
    if (selectedCategory === 'all') return weights;
    return weights.filter((w) => w.category === selectedCategory);
  }, [weights, selectedCategory]);

  const handleWeightChange = (factorName: string, newWeight: number) => {
    setAdjustedWeights((prev) => {
      const updated = new Map(prev);
      updated.set(factorName, newWeight);
      return updated;
    });
  };

  const handleResetWeights = () => {
    setAdjustedWeights(new Map());
  };

  const handleApplyRecommendations = () => {
    const newAdjustments = new Map<string, number>();
    recommendations.forEach((rec) => {
      if (rec.confidence === 'high' || rec.confidence === 'medium') {
        newAdjustments.set(rec.factor_name, rec.suggested_weight);
      }
    });
    setAdjustedWeights(newAdjustments);
  };

  const handleExportWeights = () => {
    const csv = exportWeightsToCSV(weights, currentWeightMap);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `weights_adjusted_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const categories = ['all', 'Causation', 'Severity', 'Treatment', 'Clinical', 'Disability'];

  if (weightsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
        <span className="ml-3 text-lg">Loading weights configuration...</span>
      </div>
    );
  }

  if (weightsError) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Error loading weights: {weightsError}
          <br />
          <strong>Possible solutions:</strong>
          <ul className="list-disc ml-5 mt-2">
            <li>Ensure the backend server is running on port 8000</li>
            <li>Check that weights.csv exists in backend/data/ folder</li>
            <li>As a fallback, ensure weights.csv exists in frontend/public/ folder</li>
            <li>Restart the backend server to load the new endpoint</li>
          </ul>
        </AlertDescription>
      </Alert>
    );
  }

  const hasAdjustments = adjustedWeights.size > 0;
  const metrics = recalibrationResults?.metrics;

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-3xl font-bold">Weight Recalibration & Optimization</h2>
          <p className="text-muted-foreground mt-2">
            Adjust factor weights to optimize model predictions and analyze impact on variance
          </p>
        </div>
        <div className="flex gap-2">
          {hasAdjustments && (
            <Button variant="outline" onClick={handleResetWeights}>
              <RefreshCw className="mr-2 h-4 w-4" />
              Reset All
            </Button>
          )}
          <Button variant="default" onClick={handleExportWeights}>
            <Download className="mr-2 h-4 w-4" />
            Export Weights
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      {metrics && hasAdjustments && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Improved Claims</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {metrics.improved_count}
              </div>
              <p className="text-xs text-muted-foreground">
                {((metrics.improved_count / metrics.total_claims) * 100).toFixed(1)}% of total
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Avg Improvement</CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${metrics.avg_improvement_pct > 0 ? 'text-green-600' : 'text-red-600'}`}>
                {metrics.avg_improvement_pct > 0 ? '+' : ''}{metrics.avg_improvement_pct.toFixed(2)}%
              </div>
              <p className="text-xs text-muted-foreground">Variance reduction</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">MAPE Change</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metrics.mape_before.toFixed(2)}% → {metrics.mape_after.toFixed(2)}%
              </div>
              <div className="flex items-center text-xs">
                {metrics.mape_after < metrics.mape_before ? (
                  <>
                    <TrendingDown className="h-3 w-3 text-green-600 mr-1" />
                    <span className="text-green-600">
                      {((metrics.mape_before - metrics.mape_after) / metrics.mape_before * 100).toFixed(1)}% better
                    </span>
                  </>
                ) : (
                  <>
                    <TrendingUp className="h-3 w-3 text-red-600 mr-1" />
                    <span className="text-red-600">
                      {((metrics.mape_after - metrics.mape_before) / metrics.mape_before * 100).toFixed(1)}% worse
                    </span>
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Adjustments Made</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{adjustedWeights.size}</div>
              <p className="text-xs text-muted-foreground">
                of {weights.length} total factors
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Tabs */}
      <Tabs defaultValue="single-injury" className="space-y-4">
        <TabsList className="grid w-full grid-cols-8">
          <TabsTrigger value="single-injury">Single Injury</TabsTrigger>
          <TabsTrigger value="factor-analyzer">Multi-Factor</TabsTrigger>
          <TabsTrigger value="adjust">Adjust Weights</TabsTrigger>
          <TabsTrigger value="impact">Factor Impact</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          <TabsTrigger value="advanced">Auto-Optimize</TabsTrigger>
          <TabsTrigger value="comparison">Before/After</TabsTrigger>
          <TabsTrigger value="sensitivity">Sensitivity</TabsTrigger>
        </TabsList>

        {/* Single Injury Recalibration */}
        <TabsContent value="single-injury" className="space-y-4">
          <SingleInjuryRecalibration claims={claims} />
        </TabsContent>

        {/* Factor Weight Impact Analyzer */}
        <TabsContent value="factor-analyzer" className="space-y-4">
          <FactorWeightImpactAnalyzer
            claims={claims}
            weights={weights}
          />
        </TabsContent>

        {/* Weight Adjustment Panel */}
        <TabsContent value="adjust" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Factor Weight Configuration</CardTitle>
              <CardDescription>
                Adjust individual factor weights to see their impact on model predictions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4 flex gap-2">
                {categories.map((cat) => (
                  <Badge
                    key={cat}
                    variant={selectedCategory === cat ? 'default' : 'outline'}
                    className="cursor-pointer"
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat}
                  </Badge>
                ))}
              </div>

              <WeightAdjustmentPanel
                weights={filteredWeights}
                adjustedWeights={adjustedWeights}
                onWeightChange={handleWeightChange}
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Factor Impact Analysis */}
        <TabsContent value="impact" className="space-y-4">
          <FactorImpactChart
            factorImpacts={factorImpacts}
            weights={weights}
            adjustedWeights={currentWeightMap}
          />
        </TabsContent>

        {/* Optimization Recommendations */}
        <TabsContent value="recommendations" className="space-y-4">
          <Alert className="bg-blue-50 border-blue-200">
            <AlertDescription className="text-blue-900">
              <strong>Dynamic Recommendations:</strong> These suggestions are calculated in real-time based on your actual claims data.
              Factors with high correlation to variance and high impact scores will be recommended for weight increases.
            </AlertDescription>
          </Alert>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Optimization Recommendations</CardTitle>
                <CardDescription>
                  Data-driven suggestions calculated from correlation analysis and factor impact
                </CardDescription>
              </div>
              {recommendations.length > 0 && (
                <Button onClick={handleApplyRecommendations}>
                  Apply High Confidence
                </Button>
              )}
            </CardHeader>
            <CardContent>
              <OptimizationRecommendations recommendations={recommendations} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Advanced Optimization */}
        <TabsContent value="advanced" className="space-y-4">
          <AdvancedOptimization
            claims={claims}
            weights={weights}
            currentWeights={currentWeightMap}
            onApplyOptimizedWeights={(optimizedWeights) => {
              const newAdjustments = new Map<string, number>();
              optimizedWeights.forEach((weight, factor) => {
                newAdjustments.set(factor, weight);
              });
              setAdjustedWeights(newAdjustments);
            }}
          />
        </TabsContent>

        {/* Before/After Comparison */}
        <TabsContent value="comparison" className="space-y-4">
          {recalibrationResults && (
            <BeforeAfterComparison
              results={recalibrationResults.results}
              metrics={recalibrationResults.metrics}
            />
          )}
        </TabsContent>

        {/* Sensitivity Analysis */}
        <TabsContent value="sensitivity" className="space-y-4">
          <SensitivityAnalysisChart
            claims={claims}
            weights={weights}
            baseWeights={currentWeightMap}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
