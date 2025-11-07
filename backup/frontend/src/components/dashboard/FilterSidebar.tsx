import { FilterState } from "@/types/claims";
import { Filter, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";

interface FilterSidebarProps {
  filters: FilterState;
  counties: string[];
  years: string[];
  injuryGroups: string[];
  venueRatings: string[];
  impactLevels: number[];
  onFilterChange: (key: keyof FilterState, value: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

export function FilterSidebar({ filters, counties, years, injuryGroups, venueRatings, impactLevels, onFilterChange, isOpen, onClose }: FilterSidebarProps) {
  const activeFiltersCount = Object.values(filters).filter(v => v !== 'all').length;

  const resetFilters = () => {
    Object.keys(filters).forEach(key => {
      onFilterChange(key as keyof FilterState, 'all');
    });
  };

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <aside 
        className={`
          fixed lg:sticky top-0 left-0 h-screen bg-card border-r border-border z-50
          transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          w-80 flex flex-col
        `}
      >
        {/* Header */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Filter className="h-5 w-5 text-primary" />
              <h2 className="text-lg font-semibold text-foreground">Filters</h2>
              {activeFiltersCount > 0 && (
                <Badge variant="secondary" className="ml-2">
                  {activeFiltersCount}
                </Badge>
              )}
            </div>
            <Button 
              variant="ghost" 
              size="icon"
              onClick={onClose}
              className="lg:hidden"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          {activeFiltersCount > 0 && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={resetFilters}
              className="w-full"
            >
              Clear All Filters
            </Button>
          )}
        </div>

        {/* Filters */}
        <ScrollArea className="flex-1 px-6 py-4">
          <div className="space-y-6">
            {/* Version Filter - NEW */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground flex items-center gap-2">
                <span>Data Version</span>
                <Badge variant="secondary" className="text-xs">NEW</Badge>
              </label>
              <Select value={filters.version || 'all'} onValueChange={(v) => onFilterChange('version', v)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select version" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Versions</SelectItem>
                  <SelectItem value="latest">Latest Version Only</SelectItem>
                  <SelectItem value="1">Version 1</SelectItem>
                  <SelectItem value="2">Version 2</SelectItem>
                  <SelectItem value="3">Version 3</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-xs text-muted-foreground mt-1">
                Filter claims by version iteration
              </p>
            </div>

            <Separator />

            {/* Year Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Year</label>
              <Select value={filters.year} onValueChange={(v) => onFilterChange('year', v)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select year" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Years</SelectItem>
                  {years.filter(year => year && year.toString().trim() !== '').map(year => (
                    <SelectItem key={year} value={year}>{year}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Separator />

            {/* Injury Group Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Injury Group</label>
              <Select value={filters.injuryGroupCode} onValueChange={(v) => onFilterChange('injuryGroupCode', v)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select injury group" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Injury Groups</SelectItem>
                  {injuryGroups.filter(group => group && group.trim() !== '').map(group => (
                    <SelectItem key={group} value={group}>{group}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Separator />

            {/* County Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">County</label>
              <Select value={filters.county} onValueChange={(v) => onFilterChange('county', v)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select county" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Counties</SelectItem>
                  {counties.filter(county => county && county.trim() !== '').map(county => (
                    <SelectItem key={county} value={county}>{county}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Separator />

            {/* Severity Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Severity Score</label>
              <Select value={filters.severityScore} onValueChange={(v) => onFilterChange('severityScore', v)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select severity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Severity Levels</SelectItem>
                  <SelectItem value="low">Low (1-4)</SelectItem>
                  <SelectItem value="medium">Medium (4-8)</SelectItem>
                  <SelectItem value="high">High (8+)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Separator />

            {/* Caution Level Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Caution Level</label>
              <Select value={filters.cautionLevel} onValueChange={(v) => onFilterChange('cautionLevel', v)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select caution level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Caution Levels</SelectItem>
                  <SelectItem value="Low">Low</SelectItem>
                  <SelectItem value="Medium">Medium</SelectItem>
                  <SelectItem value="High">High</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Separator />

            {/* Venue Rating Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Venue Rating</label>
              <Select value={filters.venueRating} onValueChange={(v) => onFilterChange('venueRating', v)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select venue rating" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Ratings</SelectItem>
                  {venueRatings.filter(rating => rating && rating.trim() !== '').map(rating => (
                    <SelectItem key={rating} value={rating}>{rating}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Separator />

            {/* Impact Filter */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">Impact Level</label>
              <Select value={filters.impact} onValueChange={(v) => onFilterChange('impact', v)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select impact" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Impact Levels</SelectItem>
                  {impactLevels.map(level => (
                    <SelectItem key={level} value={String(level)}>
                      {level} - {level === 0 ? 'No Impact' : level === 1 ? 'Low' : level === 2 ? 'Medium' : level === 3 ? 'High' : 'Critical'}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </ScrollArea>

        {/* Footer */}
        <div className="p-6 border-t border-border">
          <p className="text-xs text-muted-foreground text-center">
            Showing {activeFiltersCount} active filter{activeFiltersCount !== 1 ? 's' : ''}
          </p>
        </div>
      </aside>
    </>
  );
}
