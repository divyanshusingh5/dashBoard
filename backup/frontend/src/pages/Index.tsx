import { useState } from "react";
import { Header } from "@/components/dashboard/Header";
import { FilterSidebar } from "@/components/dashboard/FilterSidebar";
import { TabNavigation } from "@/components/dashboard/TabNavigation";
import { OverviewTab } from "@/components/tabs/OverviewTab";
import { RecommendationsTab } from "@/components/tabs/RecommendationsTab";
import { AlignmentTab } from "@/components/tabs/AlignmentTab";
import { InjuryTab } from "@/components/tabs/InjuryTab";
import { AdjusterTab } from "@/components/tabs/AdjusterTab";
import { VenueTab } from "@/components/tabs/VenueTab";
import { useClaimsData } from "@/hooks/useClaimsData";
import { TabType } from "@/types/claims";

const Index = () => {
  const { filteredData, filters, updateFilter, counties, years, injuryGroups, venueRatings, impactLevels, isLoading, error } = useClaimsData();
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading claims data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-subtle flex items-center justify-center">
        <div className="text-center text-destructive">
          <p className="text-lg font-semibold mb-2">Error loading data</p>
          <p className="text-sm">{error}</p>
          <p className="text-xs text-muted-foreground mt-4">
            Check if the backend API is running at http://localhost:8000
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-subtle flex w-full">
      <FilterSidebar 
        filters={filters} 
        counties={counties}
        years={years}
        injuryGroups={injuryGroups}
        venueRatings={venueRatings}
        impactLevels={impactLevels}
        onFilterChange={updateFilter}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      
      <div className="flex-1 flex flex-col min-w-0">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />
        
        <main className="flex-1 px-4 lg:px-6 py-6 lg:py-8 overflow-auto">
          <div className="max-w-[1400px] mx-auto">
            {activeTab === 'overview' && <OverviewTab data={filteredData} />}
            {activeTab === 'recommendations' && <RecommendationsTab data={filteredData} />}
            {activeTab === 'alignment' && <AlignmentTab data={filteredData} />}
            {activeTab === 'injury' && <InjuryTab data={filteredData} />}
            {activeTab === 'adjuster' && <AdjusterTab data={filteredData} />}
            {activeTab === 'venue' && <VenueTab data={filteredData} />}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Index;
