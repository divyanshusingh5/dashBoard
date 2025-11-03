import { TrendingUp, TrendingDown } from "lucide-react";

interface KPICardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    isPositive: boolean;
    isInverted?: boolean;
  };
  icon?: React.ReactNode;
}

export function KPICard({ title, value, change, icon }: KPICardProps) {
  const showChange = change !== undefined;
  const changeColor = change?.isInverted 
    ? (change.isPositive ? 'text-destructive' : 'text-success')
    : (change?.isPositive ? 'text-success' : 'text-destructive');

  return (
    <div className="bg-card rounded-xl p-6 border border-border shadow-md hover:shadow-lg transition-all duration-300 animate-fade-in">
      <div className="flex justify-between items-start mb-4">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        {icon && <div className="text-primary">{icon}</div>}
      </div>
      
      <p className="text-3xl font-bold text-foreground mb-2">
        {value}
      </p>
      
      {showChange && (
        <div className={`flex items-center gap-1 text-sm font-medium ${changeColor}`}>
          {change.isPositive ? (
            <TrendingUp className="h-4 w-4" />
          ) : (
            <TrendingDown className="h-4 w-4" />
          )}
          <span>
            {Math.abs(change.value).toFixed(1)}% vs LY
          </span>
        </div>
      )}
    </div>
  );
}
