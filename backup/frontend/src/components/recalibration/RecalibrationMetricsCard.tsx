import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { RecalibrationMetrics } from '../../types/claims';

interface RecalibrationMetricsCardProps {
  metrics: RecalibrationMetrics;
}

export default function RecalibrationMetricsCard({ metrics }: RecalibrationMetricsCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recalibration Performance Metrics</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Total Claims</p>
            <p className="text-2xl font-bold">{metrics.total_claims}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Improved</p>
            <p className="text-2xl font-bold text-green-600">{metrics.improved_count}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Unchanged</p>
            <p className="text-2xl font-bold text-gray-600">{metrics.unchanged_count}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Degraded</p>
            <p className="text-2xl font-bold text-red-600">{metrics.degraded_count}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
