import React from 'react';
import { WeightConfig } from '../../types/claims';
import { Slider } from '../ui/slider';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Badge } from '../ui/badge';
import { RotateCcw } from 'lucide-react';
import { Button } from '../ui/button';

interface WeightAdjustmentPanelProps {
  weights: WeightConfig[];
  adjustedWeights: Map<string, number>;
  onWeightChange: (factorName: string, newWeight: number) => void;
}

export default function WeightAdjustmentPanel({
  weights,
  adjustedWeights,
  onWeightChange,
}: WeightAdjustmentPanelProps) {
  const getCurrentWeight = (factorName: string, baseWeight: number) => {
    return adjustedWeights.get(factorName) ?? baseWeight;
  };

  const isAdjusted = (factorName: string, baseWeight: number) => {
    const current = getCurrentWeight(factorName, baseWeight);
    return Math.abs(current - baseWeight) > 0.001;
  };

  const handleReset = (factorName: string, baseWeight: number) => {
    onWeightChange(factorName, baseWeight);
  };

  return (
    <div className="space-y-4 max-h-[600px] overflow-y-auto">
      {weights.map((weight) => {
        const currentWeight = getCurrentWeight(weight.factor_name, weight.base_weight);
        const adjusted = isAdjusted(weight.factor_name, weight.base_weight);

        return (
          <div
            key={weight.factor_name}
            className={`p-4 border rounded-lg ${adjusted ? 'bg-blue-50 border-blue-300' : 'bg-white'}`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <Label className="font-semibold">{weight.factor_name}</Label>
                  <Badge variant="outline" className="text-xs">
                    {weight.category}
                  </Badge>
                  {adjusted && <Badge variant="default">Adjusted</Badge>}
                </div>
                <p className="text-sm text-muted-foreground mt-1">{weight.description}</p>
              </div>
              {adjusted && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleReset(weight.factor_name, weight.base_weight)}
                  className="ml-2"
                >
                  <RotateCcw className="h-4 w-4" />
                </Button>
              )}
            </div>

            <div className="grid grid-cols-12 gap-4 items-center">
              <div className="col-span-8">
                <Slider
                  value={[currentWeight]}
                  min={weight.min_weight}
                  max={weight.max_weight}
                  step={0.01}
                  onValueChange={(values) => onWeightChange(weight.factor_name, values[0])}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>Min: {weight.min_weight}</span>
                  <span>Recommended: {weight.recommended_weight}</span>
                  <span>Max: {weight.max_weight}</span>
                </div>
              </div>

              <div className="col-span-4">
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    value={currentWeight.toFixed(3)}
                    onChange={(e) => {
                      const val = parseFloat(e.target.value);
                      if (!isNaN(val) && val >= weight.min_weight && val <= weight.max_weight) {
                        onWeightChange(weight.factor_name, val);
                      }
                    }}
                    step={0.01}
                    min={weight.min_weight}
                    max={weight.max_weight}
                    className="w-24"
                  />
                  {adjusted && (
                    <div className="text-xs text-blue-600">
                      {currentWeight > weight.base_weight ? '+' : ''}
                      {((currentWeight - weight.base_weight) / weight.base_weight * 100).toFixed(1)}%
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
