/**
 * Comprehensive Dashboard Filters Component
 * Filters: County, Injury Type, Severity, Year, Impact on Life
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Filter, X } from "lucide-react";

export interface FilterState {
  county: string;
  injuryGroup: string;
  severity: string;
  year: string;
  impactOnLife: string;
}

interface DashboardFiltersProps {
  filters: FilterState;
  onFilterChange: (key: keyof FilterState, value: string) => void;
  onResetFilters: () => void;
  filterOptions: {
    counties: string[];
    years: number[];
    injuryGroups: string[];
    severityCategories: string[];
  };
}

export function DashboardFilters({
  filters,
  onFilterChange,
  onResetFilters,
  filterOptions,
}: DashboardFiltersProps) {
  const activeFilterCount = Object.values(filters).filter(v => v !== "all").length;

  return (
    <Card className="border-purple-200 bg-gradient-to-r from-purple-50 to-blue-50">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-purple-900">
            <Filter className="h-5 w-5" />
            Dashboard Filters
            {activeFilterCount > 0 && (
              <Badge className="bg-purple-600">{activeFilterCount} Active</Badge>
            )}
          </CardTitle>
          {activeFilterCount > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={onResetFilters}
              className="border-purple-300 text-purple-700 hover:bg-purple-100"
            >
              <X className="h-4 w-4 mr-1" />
              Reset All
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* County Filter */}
          <div>
            <label className="text-sm font-medium mb-2 block text-purple-900">County</label>
            <Select value={filters.county} onValueChange={(value) => onFilterChange("county", value)}>
              <SelectTrigger className="border-purple-200">
                <SelectValue placeholder="All Counties" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Counties</SelectItem>
                {filterOptions.counties.map(county => (
                  <SelectItem key={county} value={county}>{county}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Injury Group Filter */}
          <div>
            <label className="text-sm font-medium mb-2 block text-purple-900">Injury Type</label>
            <Select value={filters.injuryGroup} onValueChange={(value) => onFilterChange("injuryGroup", value)}>
              <SelectTrigger className="border-purple-200">
                <SelectValue placeholder="All Injury Types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Injury Types</SelectItem>
                {filterOptions.injuryGroups.map(group => (
                  <SelectItem key={group} value={group}>{group}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Severity Filter */}
          <div>
            <label className="text-sm font-medium mb-2 block text-purple-900">Severity</label>
            <Select value={filters.severity} onValueChange={(value) => onFilterChange("severity", value)}>
              <SelectTrigger className="border-purple-200">
                <SelectValue placeholder="All Severities" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Severities</SelectItem>
                {filterOptions.severityCategories.map(severity => (
                  <SelectItem key={severity} value={severity}>{severity}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Year Filter */}
          <div>
            <label className="text-sm font-medium mb-2 block text-purple-900">Year</label>
            <Select value={filters.year} onValueChange={(value) => onFilterChange("year", value)}>
              <SelectTrigger className="border-purple-200">
                <SelectValue placeholder="All Years" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Years</SelectItem>
                {filterOptions.years.map(year => (
                  <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Impact on Life Filter */}
          <div>
            <label className="text-sm font-medium mb-2 block text-purple-900">Impact on Life</label>
            <Select value={filters.impactOnLife} onValueChange={(value) => onFilterChange("impactOnLife", value)}>
              <SelectTrigger className="border-purple-200">
                <SelectValue placeholder="All Impacts" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Impacts</SelectItem>
                <SelectItem value="permanent">Permanent Disability</SelectItem>
                <SelectItem value="temporary">Temporary Disability</SelectItem>
                <SelectItem value="minimal">Minimal Impact</SelectItem>
                <SelectItem value="unknown">Unknown</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
