import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onReset?: () => void;
  componentName?: string;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

/**
 * Error Boundary Component
 * Catches JavaScript errors anywhere in the child component tree
 * Prevents entire app from crashing due to a single component error
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error to console in development
    console.error(`Error in ${this.props.componentName || 'Component'}:`, error, errorInfo);

    // Store error info in state
    this.setState({
      error,
      errorInfo,
    });

    // TODO: Send to error tracking service in production
    // Examples: Sentry, LogRocket, DataDog
    // if (process.env.NODE_ENV === 'production') {
    //   Sentry.captureException(error, { contexts: { react: { componentStack: errorInfo.componentStack } } });
    // }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
    this.props.onReset?.();
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-900">
              <AlertTriangle className="h-5 w-5" />
              {this.props.componentName
                ? `Error in ${this.props.componentName}`
                : "Something went wrong"}
            </CardTitle>
            <CardDescription className="text-red-700">
              An unexpected error occurred. Please try again or contact support if the problem
              persists.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {this.state.error && (
              <div className="mb-4">
                <p className="text-sm font-mono text-red-800 bg-red-100 p-3 rounded border border-red-200">
                  {this.state.error.message}
                </p>
              </div>
            )}

            <div className="flex gap-2">
              <Button onClick={this.handleReset} variant="default" size="sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                Try Again
              </Button>
              <Button onClick={() => window.location.reload()} variant="outline" size="sm">
                Reload Page
              </Button>
            </div>

            {/* Show stack trace in development */}
            {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
              <details className="mt-4">
                <summary className="text-sm text-red-700 cursor-pointer hover:underline">
                  Show technical details
                </summary>
                <pre className="text-xs mt-2 p-3 bg-red-100 border border-red-200 rounded overflow-auto max-h-60">
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
          </CardContent>
        </Card>
      );
    }

    return this.props.children;
  }
}

/**
 * Tab Error Fallback Component
 * Specialized error UI for tab components
 */
export function TabErrorFallback({ tabName, onRetry }: { tabName: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 border border-red-200 rounded-lg bg-red-50">
      <AlertTriangle className="h-12 w-12 text-red-500 mb-4" />
      <h3 className="text-lg font-semibold text-red-900 mb-2">
        Error loading {tabName} tab
      </h3>
      <p className="text-sm text-red-700 mb-4 text-center max-w-md">
        There was a problem loading this tab. This error has been logged and we're working to fix it.
      </p>
      {onRetry && (
        <Button onClick={onRetry} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Retry
        </Button>
      )}
    </div>
  );
}

/**
 * Card Error Fallback Component
 * Specialized error UI for card components
 */
export function CardErrorFallback({ cardName, error }: { cardName: string; error?: Error }) {
  return (
    <Card className="border-red-200 bg-red-50">
      <CardContent className="p-6">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-red-900 mb-1">
              Error loading {cardName}
            </p>
            {error && (
              <p className="text-xs text-red-700">
                {error.message}
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
