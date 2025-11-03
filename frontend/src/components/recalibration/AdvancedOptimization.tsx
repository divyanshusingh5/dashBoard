import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { ClaimData, WeightConfig } from '../../types/claims';
import { Play, Loader2, CheckCircle, TrendingDown, Zap } from 'lucide-react';
import {
  optimizeWeightsGradientDescent,
  optimizeWeightsGridSearch,
  optimizeWeightsSmart,
  OptimizationConfig,
  OptimizationResult,
} from '../../utils/dynamicWeightOptimizer';
import { calculateFactorImpact } from '../../utils/recalibrationEngine';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface AdvancedOptimizationProps {
  claims: ClaimData[];
  weights: WeightConfig[];
  currentWeights: Map<string, number>;
  onApplyOptimizedWeights: (optimizedWeights: Map<string, number>) => void;
}

export default function AdvancedOptimization({
  claims,
  weights,
  currentWeights,
  onApplyOptimizedWeights,
}: AdvancedOptimizationProps) {
  const [algorithm, setAlgorithm] = useState<'gradient' | 'grid' | 'smart'>('smart');
  const [targetMetric, setTargetMetric] = useState<'mape' | 'rmse' | 'both'>('mape');
  const [maxIterations, setMaxIterations] = useState(50);
  const [learningRate, setLearningRate] = useState(0.1);
  const [gridSteps, setGridSteps] = useState(5);
  const [keepConstant, setKeepConstant] = useState<string[]>([]);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [result, setResult] = useState<OptimizationResult | null>(null);

  const handleOptimize = async () => {
    setIsOptimizing(true);
    setResult(null);

    // Run optimization in a timeout to allow UI to update
    setTimeout(() => {
      try {
        const config: OptimizationConfig = {
          targetMetric,
          maxIterations,
          learningRate,
          convergenceThreshold: 0.001,
          keepFactorsConstant: keepConstant,
        };

        let optimizationResult: OptimizationResult;

        if (algorithm === 'gradient') {
          optimizationResult = optimizeWeightsGradientDescent(claims, weights, config);
        } else if (algorithm === 'grid') {
          optimizationResult = optimizeWeightsGridSearch(claims, weights, { ...config, gridSteps });
        } else {
          // Smart optimization
          const factorImpacts = calculateFactorImpact(claims, currentWeights);
          optimizationResult = optimizeWeightsSmart(claims, weights, factorImpacts, config);
        }

        setResult(optimizationResult);
      } catch (error) {
        console.error('Optimization error:', error);
      } finally {
        setIsOptimizing(false);
      }
    }, 100);
  };

  const handleApply = () => {
    if (result) {
      onApplyOptimizedWeights(result.optimizedWeights);
    }
  };

  return (
    <div className="space-y-6">
      {/* Configuration Card */}
      <Card>
        <CardHeader>
          <CardTitle>Advanced Weight Optimization</CardTitle>
          <CardDescription>
            Use machine learning algorithms to automatically find optimal weights
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Algorithm Selection */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Optimization Algorithm</Label>
              <Select value={algorithm} onValueChange={(v) => setAlgorithm(v as any)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="smart">
                    <div className="flex items-center">
                      <Zap className="h-4 w-4 mr-2" />
                      Smart (Recommended)
                    </div>
                  </SelectItem>
                  <SelectItem value="gradient">Gradient Descent</SelectItem>
                  <SelectItem value="grid">Grid Search</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground">
                {algorithm === 'smart' && 'Optimizes top 10 high-impact factors'}
                {algorithm === 'gradient' && 'Iterative hill-climbing optimization'}
                {algorithm === 'grid' && 'Exhaustive search across weight ranges'}
              </p>
            </div>

            <div className="space-y-2">
              <Label>Target Metric</Label>
              <Select value={targetMetric} onValueChange={(v) => setTargetMetric(v as any)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="mape">MAPE (Percentage Error)</SelectItem>
                  <SelectItem value="rmse">RMSE (Dollar Error)</SelectItem>
                  <SelectItem value="both">Both (Combined)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Max Iterations</Label>
              <Input
                type="number"
                value={maxIterations}
                onChange={(e) => setMaxIterations(parseInt(e.target.value) || 50)}
                min={10}
                max={200}
              />
            </div>
          </div>

          {/* Advanced Options */}
          {algorithm === 'gradient' && (
            <div className="space-y-2">
              <Label>Learning Rate</Label>
              <Input
                type="number"
                value={learningRate}
                onChange={(e) => setLearningRate(parseFloat(e.target.value) || 0.1)}
                min={0.01}
                max={0.5}
                step={0.01}
              />
              <p className="text-xs text-muted-foreground">
                Higher = faster but may overshoot optimal values
              </p>
            </div>
          )}

          {algorithm === 'grid' && (
            <div className="space-y-2">
              <Label>Grid Steps</Label>
              <Input
                type="number"
                value={gridSteps}
                onChange={(e) => setGridSteps(parseInt(e.target.value) || 5)}
                min={3}
                max={10}
              />
              <p className="text-xs text-muted-foreground">
                Number of test points between min and max weight (higher = slower)
              </p>
            </div>
          )}

          {/* Run Button */}
          <Button
            onClick={handleOptimize}
            disabled={isOptimizing}
            size="lg"
            className="w-full"
          >
            {isOptimizing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Optimizing...
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Run Optimization
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Iterations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{result.iterations}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Final MAPE</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {result.finalMAPE.toFixed(2)}%
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Final RMSE</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  ${(result.finalRMSE / 1000).toFixed(1)}k
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm">Improvement</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center">
                  <TrendingDown className="h-5 w-5 text-green-600 mr-2" />
                  <div className="text-2xl font-bold text-green-600">
                    {result.improvementPct.toFixed(1)}%
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Convergence History */}
          <Card>
            <CardHeader>
              <CardTitle>Optimization Convergence</CardTitle>
              <CardDescription>How the metric improved over iterations</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={result.convergenceHistory}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="iteration" label={{ value: 'Iteration', position: 'insideBottom', offset: -5 }} />
                  <YAxis label={{ value: 'MAPE (%)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="mape" stroke="#3b82f6" name="MAPE" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Optimized Weights */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Optimized Weights</CardTitle>
                <CardDescription>
                  {result.optimizedWeights.size} weights were adjusted
                </CardDescription>
              </div>
              <Button onClick={handleApply} variant="default">
                <CheckCircle className="mr-2 h-4 w-4" />
                Apply These Weights
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {Array.from(result.optimizedWeights.entries())
                  .filter(([factor, optimizedWeight]) => {
                    const baseWeight = weights.find(w => w.factor_name === factor)?.base_weight || 0;
                    return Math.abs(optimizedWeight - baseWeight) > 0.01;
                  })
                  .sort((a, b) => {
                    const changeA = Math.abs(a[1] - (weights.find(w => w.factor_name === a[0])?.base_weight || 0));
                    const changeB = Math.abs(b[1] - (weights.find(w => w.factor_name === b[0])?.base_weight || 0));
                    return changeB - changeA;
                  })
                  .map(([factor, optimizedWeight]) => {
                    const weightConfig = weights.find(w => w.factor_name === factor);
                    if (!weightConfig) return null;

                    const baseWeight = weightConfig.base_weight;
                    const change = optimizedWeight - baseWeight;
                    const changePercent = (change / baseWeight) * 100;

                    return (
                      <div
                        key={factor}
                        className="flex items-center justify-between p-3 border rounded hover:bg-gray-50"
                      >
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{factor}</span>
                            <Badge variant="outline">{weightConfig.category}</Badge>
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">
                            {weightConfig.description}
                          </p>
                        </div>
                        <div className="text-right ml-4">
                          <div className="text-sm">
                            <span className="text-muted-foreground">{baseWeight.toFixed(3)}</span>
                            <span className="mx-2">→</span>
                            <span className="font-semibold text-blue-600">{optimizedWeight.toFixed(3)}</span>
                          </div>
                          <div className={`text-xs ${change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {change > 0 ? '+' : ''}{changePercent.toFixed(1)}%
                          </div>
                        </div>
                      </div>
                    );
                  })}
              </div>
            </CardContent>
          </Card>

          {/* Success Alert */}
          <Alert className="bg-green-50 border-green-200">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-900">
              Optimization completed successfully! The algorithm found weights that improve predictions by{' '}
              <strong>{result.improvementPct.toFixed(1)}%</strong> over {result.iterations} iterations.
              Click "Apply These Weights" to use them.
            </AlertDescription>
          </Alert>
        </>
      )}
    </div>
  );
}
