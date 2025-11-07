import { ClaimData } from "@/types/claims";
import { Badge } from "@/components/ui/badge";
import { useMemo } from "react";
import { ArrowUp, ArrowDown } from "lucide-react";

interface DeviationAnalysisTableProps {
  data: ClaimData[];
}

interface DeviationCombo {
  primaryInjury: string;
  primaryBodypart: string;
  venueState: string;
  venueRating: string;
  settlementCategory: string;
  injections: string;
  painMgmt: string;
  treatmentType: string;
  cautionLevel: string;
  // New clinical factors
  injuryLocation?: string;
  injuryExtent?: string;
  surgicalIntervention?: string;
  treatmentDelays?: string;
  vehicleImpact?: string;
  nerveInvolvement?: string;
  physicalTherapy?: string;
  symptomTimeline?: string;
  avgPredicted: number;
  avgActual: number;
  gap: number;
  gapPct: number;
  stdDev: number;
  count: number;
}

export function DeviationAnalysisTable({ data }: DeviationAnalysisTableProps) {
  const analysis = useMemo(() => {
    // Group by ALL relevant factors including new clinical data
    const groups = new Map<string, ClaimData[]>();
    
    data.forEach(claim => {
      // Create settlement speed category
      const settlementYears = claim.SETTLEMENT_YEARS;
      let speedCategory = 'Unknown';
      if (settlementYears <= 0.5) speedCategory = 'Very Fast (≤6mo)';
      else if (settlementYears <= 1) speedCategory = 'Fast (6mo-1yr)';
      else if (settlementYears <= 2) speedCategory = 'Normal (1-2yr)';
      else if (settlementYears <= 3) speedCategory = 'Slow (2-3yr)';
      else speedCategory = 'Very Slow (>3yr)';
      
      // Categorize severity factors
      const injectionsCategory = claim.severity_injections > 7 ? 'High Injections' : 
                                claim.severity_injections > 4 ? 'Medium Injections' : 'Low/No Injections';
      const painMgmtCategory = claim.severity_pain_mgmt > 7 ? 'Intensive Pain Mgmt' : 
                              claim.severity_pain_mgmt > 4 ? 'Moderate Pain Mgmt' : 'Minimal Pain Mgmt';
      const treatmentCategory = claim.severity_type_tx > 7 ? 'Complex Treatment' : 
                               claim.severity_type_tx > 4 ? 'Standard Treatment' : 'Basic Treatment';
      
      // New clinical factors
      const injuryLoc = claim.Injury_Location || 'Unknown';
      const injuryExt = claim.Injury_Extent || 'Unknown';
      const surgery = claim.Surgical_Intervention || 'No';
      const delays = claim.Treatment_Delays || 'Unknown';
      const impact = claim.Vehicle_Impact || 'Unknown';
      const nerve = claim.Nerve_Involvement || 'Unknown';
      const pt = claim.Physical_Therapy || 'Unknown';
      const timeline = claim.Symptom_Timeline || 'Unknown';
      
      const key = `${claim.PRIMARY_INJURY}|${claim.PRIMARY_BODYPART}|${claim.VENUESTATE}|${claim.VENUE_RATING}|${speedCategory}|${injectionsCategory}|${painMgmtCategory}|${treatmentCategory}|${claim.CAUTION_LEVEL}|${injuryLoc}|${injuryExt}|${surgery}|${delays}|${impact}|${nerve}|${pt}|${timeline}`;
      
      if (!groups.has(key)) {
        groups.set(key, []);
      }
      groups.get(key)!.push(claim);
    });
    
    // Calculate metrics for each group
    const results: DeviationCombo[] = [];
    
    groups.forEach((claims, key) => {
      const [primaryInjury, primaryBodypart, venueState, venueRating, settlementCategory, injections, painMgmt, treatmentType, cautionLevel, injuryLocation, injuryExtent, surgicalIntervention, treatmentDelays, vehicleImpact, nerveInvolvement, physicalTherapy, symptomTimeline] = key.split('|');
      
      // Skip groups with too few claims
      if (claims.length < 2) return;
      
      const avgPredicted = claims.reduce((sum, c) => sum + c.predicted_pain_suffering, 0) / claims.length;
      const avgActual = claims.reduce((sum, c) => sum + c.DOLLARAMOUNTHIGH, 0) / claims.length;
      const gap = avgActual - avgPredicted;
      const gapPct = avgPredicted > 0 ? (gap / avgPredicted) * 100 : 0;
      
      // Calculate standard deviation
      const variance = claims.reduce((sum, c) => 
        sum + Math.pow(c.DOLLARAMOUNTHIGH - avgActual, 2), 0) / claims.length;
      const stdDev = Math.sqrt(variance);
      
      results.push({
        primaryInjury,
        primaryBodypart,
        venueState,
        venueRating,
        settlementCategory,
        injections,
        painMgmt,
        treatmentType,
        cautionLevel,
        injuryLocation,
        injuryExtent,
        surgicalIntervention,
        treatmentDelays,
        vehicleImpact,
        nerveInvolvement,
        physicalTherapy,
        symptomTimeline,
        avgPredicted,
        avgActual,
        gap,
        gapPct,
        stdDev,
        count: claims.length
      });
    });
    
    // Sort by absolute gap percentage (highest deviation first)
    return results.sort((a, b) => Math.abs(b.gapPct) - Math.abs(a.gapPct)).slice(0, 50);
  }, [data]);
  
  // Calculate summary insights
  const insights = useMemo(() => {
    const overperformCount = analysis.filter(a => a.gapPct > 20).length;
    const underperformCount = analysis.filter(a => a.gapPct < -20).length;
    
    // State-level analysis
    const stateDeviations = new Map<string, { sum: number; count: number }>();
    analysis.forEach(a => {
      if (!stateDeviations.has(a.venueState)) {
        stateDeviations.set(a.venueState, { sum: 0, count: 0 });
      }
      const state = stateDeviations.get(a.venueState)!;
      state.sum += a.gapPct;
      state.count += 1;
    });
    
    const topOverState = Array.from(stateDeviations.entries())
      .map(([state, data]) => ({ state, avgGap: data.sum / data.count }))
      .filter(s => s.avgGap > 0)
      .sort((a, b) => b.avgGap - a.avgGap)[0];
    
    const topUnderState = Array.from(stateDeviations.entries())
      .map(([state, data]) => ({ state, avgGap: data.sum / data.count }))
      .filter(s => s.avgGap < 0)
      .sort((a, b) => a.avgGap - b.avgGap)[0];
    
    return {
      overperformCount,
      underperformCount,
      topOverState,
      topUnderState
    };
  }, [analysis]);

  return (
    <div className="space-y-6">
      {/* Summary Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-card rounded-lg p-4 border border-border">
          <div className="text-sm text-muted-foreground mb-1">Overperforming Combos</div>
          <div className="text-2xl font-bold text-success flex items-center gap-2">
            <ArrowUp className="h-5 w-5" />
            {insights.overperformCount}
          </div>
          <div className="text-xs text-muted-foreground mt-1">Actual &gt; Predicted by &gt;20%</div>
        </div>
        
        <div className="bg-card rounded-lg p-4 border border-border">
          <div className="text-sm text-muted-foreground mb-1">Underperforming Combos</div>
          <div className="text-2xl font-bold text-destructive flex items-center gap-2">
            <ArrowDown className="h-5 w-5" />
            {insights.underperformCount}
          </div>
          <div className="text-xs text-muted-foreground mt-1">Predicted &gt; Actual by &gt;20%</div>
        </div>
        
        <div className="bg-card rounded-lg p-4 border border-border">
          <div className="text-sm text-muted-foreground mb-1">Top Overperforming State</div>
          <div className="text-2xl font-bold">{insights.topOverState?.state || 'N/A'}</div>
          <div className="text-xs text-success mt-1">
            +{insights.topOverState?.avgGap.toFixed(1) || 0}% avg deviation
          </div>
        </div>
        
        <div className="bg-card rounded-lg p-4 border border-border">
          <div className="text-sm text-muted-foreground mb-1">Top Underperforming State</div>
          <div className="text-2xl font-bold">{insights.topUnderState?.state || 'N/A'}</div>
          <div className="text-xs text-destructive mt-1">
            {insights.topUnderState?.avgGap.toFixed(1) || 0}% avg deviation
          </div>
        </div>
      </div>

      {/* Enhanced Deviation Table with Clinical Factors */}
      <div className="bg-card rounded-xl p-6 border border-border shadow-md">
        <div className="mb-4">
          <h3 className="text-lg font-semibold">Deviation Analysis: All Factor Combinations</h3>
          <p className="text-sm text-muted-foreground mt-1">
            Comprehensive multi-dimensional analysis including clinical factors, treatment patterns, injury characteristics, and venue dynamics
          </p>
        </div>
        
        <div className="overflow-x-auto max-h-[600px] overflow-y-auto border border-border rounded-lg">
          <table className="w-full">
            <thead className="bg-muted/50 border-b border-border sticky top-0 z-10">
              <tr>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Primary Injury</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Body Part</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Injury Location</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Injury Extent</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Surgery</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Treatment Delays</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Vehicle Impact</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Nerve</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">PT</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Symptom Timeline</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">State</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Venue</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Settlement Speed</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Injections</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Pain Mgmt</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Treatment</th>
                <th className="px-3 py-3 text-left text-xs font-semibold whitespace-nowrap">Caution</th>
                <th className="px-3 py-3 text-right text-xs font-semibold whitespace-nowrap">% Gap</th>
                <th className="px-3 py-3 text-center text-xs font-semibold whitespace-nowrap">Count</th>
              </tr>
            </thead>
            <tbody>
              {analysis.map((item, idx) => {
                const isHighDeviation = Math.abs(item.gapPct) > 30;
                const isOverperform = item.gapPct > 0;
                
                return (
                  <tr key={idx} className="border-b border-border hover:bg-muted/30 transition-colors">
                    <td className="px-3 py-3 text-xs font-medium max-w-[120px] truncate" title={item.primaryInjury}>
                      {item.primaryInjury}
                    </td>
                    <td className="px-3 py-3 text-xs max-w-[100px] truncate" title={item.primaryBodypart}>
                      {item.primaryBodypart}
                    </td>
                    <td className="px-3 py-3 text-xs max-w-[120px] truncate" title={item.injuryLocation}>
                      {item.injuryLocation}
                    </td>
                    <td className="px-3 py-3 text-xs">
                      <Badge variant={item.injuryExtent === 'Severe' ? 'destructive' : item.injuryExtent === 'Moderate' ? 'default' : 'outline'} className="text-xs">
                        {item.injuryExtent}
                      </Badge>
                    </td>
                    <td className="px-3 py-3 text-xs">
                      <Badge variant={item.surgicalIntervention?.includes('Yes') ? 'destructive' : 'outline'} className="text-xs">
                        {item.surgicalIntervention?.includes('Yes') ? 'Yes' : 'No'}
                      </Badge>
                    </td>
                    <td className="px-3 py-3 text-xs max-w-[100px] truncate" title={item.treatmentDelays}>
                      <Badge variant={item.treatmentDelays?.includes('Delay and Gaps') ? 'destructive' : 'outline'} className="text-xs">
                        {item.treatmentDelays}
                      </Badge>
                    </td>
                    <td className="px-3 py-3 text-xs">
                      <Badge variant={item.vehicleImpact === 'Heavy' ? 'destructive' : item.vehicleImpact === 'Moderate' ? 'default' : 'outline'} className="text-xs">
                        {item.vehicleImpact}
                      </Badge>
                    </td>
                    <td className="px-3 py-3 text-xs">
                      {item.nerveInvolvement === 'Yes' ? '✓' : '—'}
                    </td>
                    <td className="px-3 py-3 text-xs">
                      {item.physicalTherapy?.includes('Yes') ? '✓' : '—'}
                    </td>
                    <td className="px-3 py-3 text-xs max-w-[100px] truncate" title={item.symptomTimeline}>
                      {item.symptomTimeline}
                    </td>
                    <td className="px-3 py-3 text-xs">
                      <Badge variant="outline" className="text-xs">{item.venueState}</Badge>
                    </td>
                    <td className="px-3 py-3 text-xs">{item.venueRating}</td>
                    <td className="px-3 py-3 text-xs whitespace-nowrap">{item.settlementCategory}</td>
                    <td className="px-3 py-3 text-xs whitespace-nowrap">{item.injections}</td>
                    <td className="px-3 py-3 text-xs whitespace-nowrap">{item.painMgmt}</td>
                    <td className="px-3 py-3 text-xs whitespace-nowrap">{item.treatmentType}</td>
                    <td className="px-3 py-3 text-xs">
                      <Badge variant={item.cautionLevel === 'High' ? 'destructive' : item.cautionLevel === 'Medium' ? 'default' : 'secondary'} className="text-xs">
                        {item.cautionLevel}
                      </Badge>
                    </td>
                    <td className={`px-3 py-3 text-xs text-right font-bold ${
                      isOverperform ? 'text-success' : 'text-destructive'
                    }`}>
                      {isOverperform ? '+' : ''}{item.gapPct.toFixed(1)}%
                    </td>
                    <td className="px-3 py-3 text-xs text-center">
                      <Badge variant={isHighDeviation ? "destructive" : "secondary"} className="text-xs">
                        {item.count}
                      </Badge>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
