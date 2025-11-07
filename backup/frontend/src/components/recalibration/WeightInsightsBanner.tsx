import React from 'react';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import { Button } from '../ui/button';
import { Lightbulb, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

interface WeightInsightsBannerProps {
  message?: string;
  showLink?: boolean;
}

export default function WeightInsightsBanner({
  message = "Want to improve model predictions? Try adjusting factor weights in the Recalibration tab.",
  showLink = true
}: WeightInsightsBannerProps) {
  return (
    <Alert className="bg-blue-50 border-blue-200">
      <Lightbulb className="h-4 w-4 text-blue-600" />
      <AlertTitle className="text-blue-900">Weight Recalibration Available</AlertTitle>
      <AlertDescription className="flex items-center justify-between">
        <span className="text-blue-800">{message}</span>
        {showLink && (
          <Link to="/?tab=recalibration">
            <Button variant="outline" size="sm" className="ml-4">
              Go to Recalibration
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        )}
      </AlertDescription>
    </Alert>
  );
}
