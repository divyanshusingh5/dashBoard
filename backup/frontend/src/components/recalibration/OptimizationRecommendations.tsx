import React from 'react';
import { WeightOptimizationRecommendation } from '../../types/claims';
import { Badge } from '../ui/badge';
import { TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '../ui/alert';

interface OptimizationRecommendationsProps {
  recommendations: WeightOptimizationRecommendation[];
}

export default function OptimizationRecommendations({
  recommendations,
}: OptimizationRecommendationsProps) {
  if (recommendations.length === 0) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          No optimization recommendations at this time. Current weights are performing well.
        </AlertDescription>
      </Alert>
    );
  }

  const getConfidenceBadge = (confidence: string) => {
    const variants = {
      high: 'default',
      medium: 'secondary',
      low: 'outline',
    } as const;

    const colors = {
      high: 'bg-green-100 text-green-800 border-green-300',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      low: 'bg-gray-100 text-gray-800 border-gray-300',
    };

    return (
      <Badge variant={variants[confidence as keyof typeof variants]} className={colors[confidence as keyof typeof colors]}>
        {confidence.toUpperCase()}
      </Badge>
    );
  };

  const highConfidence = recommendations.filter((r) => r.confidence === 'high');
  const mediumConfidence = recommendations.filter((r) => r.confidence === 'medium');
  const lowConfidence = recommendations.filter((r) => r.confidence === 'low');

  return (
    <div className="space-y-6">
      {/* High Confidence Recommendations */}
      {highConfidence.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <Badge className="bg-green-600">High Priority</Badge>
            {highConfidence.length} Recommendations
          </h3>
          <div className="space-y-3">
            {highConfidence.map((rec, index) => (
              <div
                key={index}
                className="p-4 border-2 border-green-200 bg-green-50 rounded-lg"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-semibold">{rec.factor_name}</h4>
                      {getConfidenceBadge(rec.confidence)}
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{rec.reason}</p>
                    <div className="flex items-center gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Current: </span>
                        <span className="font-semibold">{rec.current_weight.toFixed(3)}</span>
                      </div>
                      <div className="flex items-center">
                        {rec.suggested_weight > rec.current_weight ? (
                          <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-blue-600 mr-1" />
                        )}
                      </div>
                      <div>
                        <span className="text-muted-foreground">Suggested: </span>
                        <span className="font-semibold text-green-700">{rec.suggested_weight.toFixed(3)}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Expected: </span>
                        <span className="font-semibold text-green-700">+{rec.expected_improvement}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Medium Confidence Recommendations */}
      {mediumConfidence.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <Badge className="bg-yellow-600">Medium Priority</Badge>
            {mediumConfidence.length} Recommendations
          </h3>
          <div className="space-y-3">
            {mediumConfidence.map((rec, index) => (
              <div
                key={index}
                className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-semibold">{rec.factor_name}</h4>
                      {getConfidenceBadge(rec.confidence)}
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{rec.reason}</p>
                    <div className="flex items-center gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Current: </span>
                        <span className="font-semibold">{rec.current_weight.toFixed(3)}</span>
                      </div>
                      <div className="flex items-center">
                        {rec.suggested_weight > rec.current_weight ? (
                          <TrendingUp className="h-4 w-4 text-green-600 mr-1" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-blue-600 mr-1" />
                        )}
                      </div>
                      <div>
                        <span className="text-muted-foreground">Suggested: </span>
                        <span className="font-semibold text-yellow-700">{rec.suggested_weight.toFixed(3)}</span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Expected: </span>
                        <span className="font-semibold text-yellow-700">+{rec.expected_improvement}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Low Confidence Recommendations */}
      {lowConfidence.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <Badge variant="outline">Low Priority</Badge>
            {lowConfidence.length} Recommendations
          </h3>
          <div className="space-y-2">
            {lowConfidence.map((rec, index) => (
              <div
                key={index}
                className="p-3 border border-gray-200 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium text-sm">{rec.factor_name}</h4>
                      {getConfidenceBadge(rec.confidence)}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{rec.reason}</p>
                  </div>
                  <div className="text-right text-xs">
                    <div>{rec.current_weight.toFixed(3)} → {rec.suggested_weight.toFixed(3)}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Summary */}
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          <strong>Total Recommendations:</strong> {recommendations.length} |{' '}
          <strong>Potential Improvement:</strong>{' '}
          {recommendations.reduce((sum, r) => sum + r.expected_improvement, 0).toFixed(1)}% combined
        </AlertDescription>
      </Alert>
    </div>
  );
}
