import { TabType } from "@/types/claims";
import { cn } from "@/lib/utils";
import { LayoutDashboard, Lightbulb, Target, Activity, Users, MapPin } from "lucide-react";

interface TabNavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

const tabs: { id: TabType; label: string; icon: React.ElementType }[] = [
  { id: 'overview', label: 'Executive Overview', icon: LayoutDashboard },
  { id: 'recommendations', label: 'Recommendations', icon: Lightbulb },
  { id: 'alignment', label: 'Model Alignment', icon: Target },
  { id: 'injury', label: 'Injury Analysis', icon: Activity },
  { id: 'adjuster', label: 'Adjuster Performance', icon: Users },
  { id: 'venue', label: 'Venue Analysis', icon: MapPin },
];

export function TabNavigation({ activeTab, onTabChange }: TabNavigationProps) {
  return (
    <div className="bg-card/50 backdrop-blur-sm border-b border-border/50 sticky top-0 z-10">
      <div className="max-w-[1400px] mx-auto px-4 lg:px-6">
        <div className="flex gap-2 overflow-x-auto scrollbar-hide py-3">
          {tabs.map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={cn(
                  "flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-all duration-300",
                  "hover:scale-105 active:scale-95",
                  isActive
                    ? "bg-gradient-to-r from-primary/20 to-accent/20 text-primary border-2 border-primary/40 shadow-lg shadow-primary/20"
                    : "bg-card/80 text-muted-foreground hover:bg-accent/10 hover:text-foreground border-2 border-transparent"
                )}
              >
                <Icon className={cn(
                  "h-4 w-4 transition-transform duration-300",
                  isActive && "scale-110"
                )} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
