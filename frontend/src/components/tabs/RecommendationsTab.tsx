import { ClaimData } from "@/types/claims";
import { Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip, Legend, Line, LineChart, CartesianGrid, Cell, ScatterChart, Scatter, ZAxis } from "recharts";
import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, TrendingUp, TrendingDown, Info, CheckCircle2, XCircle, Target, Users, Activity, BarChart3 } from "lucide-react";

interface RecommendationsTabProps {
  data: ClaimData[];
}

export function RecommendationsTab({ data }: RecommendationsTabProps) {
  const [selectedCombo, setSelectedCombo] = useState<string | null>(null);

  // ===== EXECUTIVE SUMMARY CALCULATIONS =====
  const executiveSummary = useMemo(() => {
    const totalClaims = data.length;
    const avgVariance = data.reduce((sum, c) => sum + Math.abs(c.variance_pct), 0) / totalClaims;
    const highVarianceClaims = data.filter(c => Math.abs(c.variance_pct) > 30).length;
    const modelAccuracy = ((totalClaims - highVarianceClaims) / totalClaims) * 100;
    
    const varianceByFactor = {
      injuryGroup: {} as Record<string, number[]>,
      severity: {} as Record<string, number[]>,
      county: {} as Record<string, number[]>,
      venueRating: {} as Record<string, number[]>,
      impactLife: {} as Record<string, number[]>
    };

    data.forEach(claim => {
      const abs = Math.abs(claim.variance_pct);
      if (!varianceByFactor.injuryGroup[claim.INJURY_GROUP_CODE]) varianceByFactor.injuryGroup[claim.INJURY_GROUP_CODE] = [];
      varianceByFactor.injuryGroup[claim.INJURY_GROUP_CODE].push(abs);
      
      const sevBucket = claim.SEVERITY_SCORE <= 4 ? 'Low' : claim.SEVERITY_SCORE <= 8 ? 'Medium' : 'High';
      if (!varianceByFactor.severity[sevBucket]) varianceByFactor.severity[sevBucket] = [];
      varianceByFactor.severity[sevBucket].push(abs);
      
      if (!varianceByFactor.county[claim.COUNTYNAME]) varianceByFactor.county[claim.COUNTYNAME] = [];
      varianceByFactor.county[claim.COUNTYNAME].push(abs);
      
      if (!varianceByFactor.venueRating[claim.VENUE_RATING]) varianceByFactor.venueRating[claim.VENUE_RATING] = [];
      varianceByFactor.venueRating[claim.VENUE_RATING].push(abs);
      
      const impactKey = `Impact-${claim.IMPACT}`;
      if (!varianceByFactor.impactLife[impactKey]) varianceByFactor.impactLife[impactKey] = [];
      varianceByFactor.impactLife[impactKey].push(abs);
    });

    const topDrivers = Object.entries(varianceByFactor).flatMap(([factorType, values]) => 
      Object.entries(values).map(([key, variances]) => ({
        factor: factorType,
        value: key,
        avgVariance: variances.reduce((a, b) => a + b, 0) / variances.length,
        count: variances.length
      }))
    ).sort((a, b) => b.avgVariance - a.avgVariance).slice(0, 5);

    return { totalClaims, avgVariance, highVarianceClaims, modelAccuracy, topDrivers };
  }, [data]);

  // ===== MULTI-INJURY CLAIM ANALYSIS =====
  const multiInjuryAnalysis = useMemo(() => {
    // Detect multi-injury claims by checking if multiple body parts or complex injury descriptions
    const singleInjury: number[] = [];
    const multiInjury: number[] = [];
    const singleInjurySettlements: number[] = [];
    const multiInjurySettlements: number[] = [];
    
    data.forEach(claim => {
      const absVariance = Math.abs(claim.variance_pct);
      // Heuristic: if body_part contains comma, slash, "and", or "multiple" it's multi-injury
      const bodyPartLower = claim.PRIMARY_BODYPART.toLowerCase();
      const isMulti = bodyPartLower.includes(',') || 
                      bodyPartLower.includes('/') || 
                      bodyPartLower.includes(' and ') ||
                      bodyPartLower.includes('multiple') ||
                      claim.IMPACT >= 4; // High impact often indicates multiple injuries
      
      if (isMulti) {
        multiInjury.push(absVariance);
        multiInjurySettlements.push(claim.DOLLARAMOUNTHIGH);
      } else {
        singleInjury.push(absVariance);
        singleInjurySettlements.push(claim.DOLLARAMOUNTHIGH);
      }
    });

    const singleAvg = singleInjury.reduce((a, b) => a + b, 0) / singleInjury.length;
    const multiAvg = multiInjury.reduce((a, b) => a + b, 0) / multiInjury.length;
    const singleSettlementAvg = singleInjurySettlements.reduce((a, b) => a + b, 0) / singleInjurySettlements.length;
    const multiSettlementAvg = multiInjurySettlements.reduce((a, b) => a + b, 0) / multiInjurySettlements.length;

    const varianceDiff = ((multiAvg - singleAvg) / singleAvg) * 100;
    
    return {
      singleCount: singleInjury.length,
      multiCount: multiInjury.length,
      singleAvgVariance: singleAvg,
      multiAvgVariance: multiAvg,
      singleAvgSettlement: singleSettlementAvg,
      multiAvgSettlement: multiSettlementAvg,
      varianceDifferential: varianceDiff,
      pattern: varianceDiff > 15 ? 'Multi-injury claims show significantly higher variance' :
               varianceDiff < -15 ? 'Single-injury claims show higher variance' :
               'No significant pattern difference'
    };
  }, [data]);

  // ===== FACTOR COMBINATION ANALYSIS =====
  const factorCombinations = useMemo(() => {
    const combos: Record<string, {
      claims: ClaimData[];
      variance: number[];
      key: string;
      injuryGroup: string;
      severityBucket: string;
      venueRating: string;
      impactLife: number;
      factors: Record<string, any>;
    }> = {};

    data.forEach(claim => {
      const sevBucket = claim.SEVERITY_SCORE <= 4 ? 'Low-Sev' : claim.SEVERITY_SCORE <= 8 ? 'Mid-Sev' : 'High-Sev';
      const comboKey = `${claim.INJURY_GROUP_CODE}|${sevBucket}|${claim.VENUE_RATING}|${claim.IMPACT}`;
      const absVariance = Math.abs(claim.variance_pct);
      
      if (!combos[comboKey]) {
        combos[comboKey] = {
          claims: [],
          variance: [],
          key: comboKey,
          injuryGroup: claim.INJURY_GROUP_CODE,
          severityBucket: sevBucket,
          venueRating: claim.VENUE_RATING,
          impactLife: claim.IMPACT,
          factors: {
            injury_group: claim.INJURY_GROUP_CODE,
            severity: sevBucket,
            venue_rating: claim.VENUE_RATING,
            impact_life: claim.IMPACT
          }
        };
      }
      
      combos[comboKey].claims.push(claim);
      combos[comboKey].variance.push(Math.abs(claim.variance_pct));
    });

    return Object.values(combos)
      .filter(combo => combo.claims.length >= 3) // Only meaningful combinations
      .map(combo => {
        const avgVariance = combo.variance.reduce((a, b) => a + b, 0) / combo.variance.length;
        const avgSettlement = combo.claims.reduce((sum, c) => sum + c.DOLLARAMOUNTHIGH, 0) / combo.claims.length;
        const avgSeverity = combo.claims.reduce((sum, c) => sum + c.SEVERITY_SCORE, 0) / combo.claims.length;
        
        // Factor impact analysis for this combination
        const countyVariance: Record<string, number[]> = {};
        const adjusterVariance: Record<string, number[]> = {};
        
        combo.claims.forEach(c => {
          if (!countyVariance[c.COUNTYNAME]) countyVariance[c.COUNTYNAME] = [];
          countyVariance[c.COUNTYNAME].push(Math.abs(c.variance_pct));
          
          if (!adjusterVariance[c.adjuster]) adjusterVariance[c.adjuster] = [];
          adjusterVariance[c.adjuster].push(Math.abs(c.variance_pct));
        });
        
        // Top contributing factors
        const topCounties = Object.entries(countyVariance)
          .map(([name, vars]) => ({ name, avgVar: vars.reduce((a, b) => a + b) / vars.length, count: vars.length }))
          .sort((a, b) => b.avgVar - a.avgVar)
          .slice(0, 3);
        
        const topAdjusters = Object.entries(adjusterVariance)
          .map(([name, vars]) => ({ name, avgVar: vars.reduce((a, b) => a + b) / vars.length, count: vars.length }))
          .sort((a, b) => b.avgVar - a.avgVar)
          .slice(0, 3);
        
        const topCountyDriver = topCounties[0];
        const topAdjusterDriver = topAdjusters[0];

        return {
          ...combo,
          avgVariance,
          avgSettlement,
          avgSeverity,
          count: combo.claims.length,
          topCounties,
          topAdjusters,
          topCountyDriver,
          topAdjusterDriver,
          displayName: `${combo.injuryGroup} + ${combo.severityBucket} + ${combo.venueRating}`
        };
      })
      .sort((a, b) => b.avgVariance - a.avgVariance);
  }, [data]);

  const topProblemCombos = useMemo(() => factorCombinations.slice(0, 10), [factorCombinations]);
  const wellPerformingCombos = useMemo(() => 
    factorCombinations.filter(c => c.avgVariance < 15).slice(0, 5),
    [factorCombinations]
  );

  // ===== ADJUSTER RECOMMENDATIONS WITH REASONING =====
  const adjusterRecommendations = useMemo(() => {
    const adjusterStats: Record<string, {
      totalClaims: number;
      avgVariance: number;
      variances: number[];
      settlements: number[];
      severities: number[];
      handledCombos: Set<string>;
      performanceByCombo: Record<string, { variance: number[]; count: number }>;
    }> = {};

    data.forEach(claim => {
      const sevBucket = claim.SEVERITY_SCORE <= 4 ? 'Low-Sev' : claim.SEVERITY_SCORE <= 8 ? 'Mid-Sev' : 'High-Sev';
      const comboKey = `${claim.INJURY_GROUP_CODE}|${sevBucket}`;
      
      if (!adjusterStats[claim.adjuster]) {
        adjusterStats[claim.adjuster] = {
          totalClaims: 0,
          avgVariance: 0,
          variances: [],
          settlements: [],
          severities: [],
          handledCombos: new Set(),
          performanceByCombo: {}
        };
      }
      
      const stats = adjusterStats[claim.adjuster];
      stats.totalClaims++;
      stats.variances.push(Math.abs(claim.variance_pct));
      stats.settlements.push(claim.DOLLARAMOUNTHIGH);
      stats.severities.push(claim.SEVERITY_SCORE);
      stats.handledCombos.add(comboKey);
      
      if (!stats.performanceByCombo[comboKey]) {
        stats.performanceByCombo[comboKey] = { variance: [], count: 0 };
      }
      stats.performanceByCombo[comboKey].variance.push(Math.abs(claim.variance_pct));
      stats.performanceByCombo[comboKey].count++;
    });

    return Object.entries(adjusterStats)
      .map(([name, stats]) => {
        const avgVariance = stats.variances.reduce((a, b) => a + b, 0) / stats.variances.length;
        const consistency = 1 - (Math.sqrt(stats.variances.reduce((sum, v) => sum + Math.pow(v - avgVariance, 2), 0) / stats.variances.length) / avgVariance);
        const avgSettlement = stats.settlements.reduce((a, b) => a + b, 0) / stats.settlements.length;
        const avgSeverity = stats.severities.reduce((a, b) => a + b, 0) / stats.severities.length;
        
        // Experience diversity score
        const diversityScore = stats.handledCombos.size / stats.totalClaims;
        
        // Best performing combo
        const bestCombo = Object.entries(stats.performanceByCombo)
          .filter(([_, perf]) => perf.count >= 2)
          .map(([combo, perf]) => ({
            combo,
            avgVar: perf.variance.reduce((a, b) => a + b) / perf.count,
            count: perf.count
          }))
          .sort((a, b) => a.avgVar - b.avgVar)[0];

        // Calculate calibration score (0-100)
        const calibrationScore = Math.max(0, Math.min(100, 
          ((100 - avgVariance) * 0.4) +  // Low variance = good
          (consistency * 100 * 0.3) +     // Consistency = good
          (Math.min(stats.totalClaims / 20, 1) * 100 * 0.2) + // Experience = good
          (diversityScore * 100 * 0.1)    // Diversity = good
        ));

        return {
          name,
          totalClaims: stats.totalClaims,
          avgVariance,
          consistency,
          avgSettlement,
          avgSeverity,
          diversityScore,
          bestCombo,
          calibrationScore,
          recommendation: calibrationScore > 70 ? 'Excellent for recalibration' :
                         calibrationScore > 50 ? 'Good for specific segments' :
                         'Not recommended for recalibration'
        };
      })
      .sort((a, b) => b.calibrationScore - a.calibrationScore);
  }, [data]);

  const recommendedForCalibration = useMemo(() => 
    adjusterRecommendations.filter(a => a.calibrationScore > 60 && a.totalClaims >= 10).slice(0, 8),
    [adjusterRecommendations]
  );

  // ===== COUNTY VARIANCE ANALYSIS =====


  const countyAnalysis = useMemo(() => {
    const counties: { 
      [key: string]: { 
        signedVariance: number;
        absVariance: number;
        count: number;
        settlement: number;
        overpredicted: number;
        underpredicted: number;
        avgSeverity: number;
        avgCaution: number;
        liberalCount: number;
        conservativeCount: number;
      } 
    } = {};
    
    data.forEach(claim => {
      if (!counties[claim.COUNTYNAME]) {
        counties[claim.COUNTYNAME] = { 
          signedVariance: 0, 
          absVariance: 0,
          count: 0, 
          settlement: 0,
          overpredicted: 0,
          underpredicted: 0,
          avgSeverity: 0,
          avgCaution: 0,
          liberalCount: 0,
          conservativeCount: 0
        };
      }
      
      counties[claim.COUNTYNAME].signedVariance += claim.variance_pct;
      counties[claim.COUNTYNAME].absVariance += Math.abs(claim.variance_pct);
      counties[claim.COUNTYNAME].count += 1;
      counties[claim.COUNTYNAME].settlement += claim.DOLLARAMOUNTHIGH;
      counties[claim.COUNTYNAME].avgSeverity += claim.SEVERITY_SCORE;
      counties[claim.COUNTYNAME].avgCaution += (claim.CAUTION_LEVEL === 'High' ? 1 : 0);
      
      if (claim.variance_pct > 0) {
        counties[claim.COUNTYNAME].underpredicted += 1;
        if (claim.variance_pct > 15) counties[claim.COUNTYNAME].liberalCount += 1;
      } else {
        counties[claim.COUNTYNAME].overpredicted += 1;
        if (claim.variance_pct < -15) counties[claim.COUNTYNAME].conservativeCount += 1;
      }
    });

    return Object.entries(counties)
      .map(([name, stats]) => {
        const avgSignedVariance = stats.signedVariance / stats.count;
        const avgAbsVariance = stats.absVariance / stats.count;
        const underpredictRate = (stats.underpredicted / stats.count) * 100;
        
        let tendency = 'Neutral';
        let tendencyBadge: 'destructive' | 'success' | 'default' = 'default';
        
        if (avgSignedVariance > 10 && underpredictRate > 55) {
          tendency = 'Liberal';
          tendencyBadge = 'destructive';
        } else if (avgSignedVariance < -10 && underpredictRate < 45) {
          tendency = 'Conservative';
          tendencyBadge = 'success';
        }
        
        return {
          name,
          state: data.find(d => d.COUNTYNAME === name)?.VENUESTATE || '',
          avgSignedVariance,
          avgAbsVariance,
          avgSettlement: stats.settlement / stats.count,
          avgSeverity: stats.avgSeverity / stats.count,
          cautionHighPct: (stats.avgCaution / stats.count) * 100,
          count: stats.count,
          underpredictRate,
          tendency,
          tendencyBadge,
          liberalCount: stats.liberalCount,
          conservativeCount: stats.conservativeCount
        };
      })
      .sort((a, b) => b.avgAbsVariance - a.avgAbsVariance);
  }, [data]);

  const highVarianceCounties = useMemo(() => {
    return countyAnalysis.filter(c => c.avgAbsVariance > 20).slice(0, 10);
  }, [countyAnalysis]);

  const temporalData = useMemo(() => {
    const monthly: { [key: string]: { variance: number; count: number } } = {};
    
    data.forEach(claim => {
      const month = claim.claim_date.substring(0, 7);
      if (!monthly[month]) {
        monthly[month] = { variance: 0, count: 0 };
      }
      monthly[month].variance += Math.abs(claim.variance_pct);
      monthly[month].count += 1;
    });

    return Object.entries(monthly)
      .map(([month, { variance, count }]) => ({
        month,
        avgVariance: variance / count
      }))
      .sort((a, b) => a.month.localeCompare(b.month));
  }, [data]);

  // ===== MODEL FACTOR WEIGHT ANALYSIS =====
  const factorWeightAnalysis = useMemo(() => {
    const causationFactors = [
      { name: 'Causation Probability', field: 'causation_probability' as keyof ClaimData, weights: [0.3257, 0.2212, 0.4478, 0.0000] },
      { name: 'Tx Delay', field: 'causation_tx_delay' as keyof ClaimData, weights: [0.1226, 0.0000] },
      { name: 'Tx Gaps', field: 'causation_tx_gaps' as keyof ClaimData, weights: [0.1313, 0.0000] },
      { name: 'Compliance', field: 'causation_compliance' as keyof ClaimData, weights: [0.1474, 0.0864] }
    ];

    const severityFactors = [
      { name: 'Allowed Tx Period', field: 'severity_allowed_tx_period' as keyof ClaimData, weights: [1.4488, 0.0000, 2.3490, 3.1606, 3.8533, 4.3507] },
      { name: 'Initial Tx', field: 'severity_initial_tx' as keyof ClaimData, weights: [1.5445, 1.2406, 0.6738, 0.0000] },
      { name: 'Injections', field: 'severity_injections' as keyof ClaimData, weights: [0.0000, 1.9855, 3.0855, 3.4370, 5.1228] },
      { name: 'Objective Findings', field: 'severity_objective_findings' as keyof ClaimData, weights: [2.7611, 0.0] },
      { name: 'Pain Mgmt', field: 'severity_pain_mgmt' as keyof ClaimData, weights: [0.0000, 0.6396, 1.1258] },
      { name: 'Type of Tx', field: 'severity_type_tx' as keyof ClaimData, weights: [2.0592, 3.2501] },
      { name: 'Injury Site', field: 'severity_injury_site' as keyof ClaimData, weights: [1.8450, 1.1767, 0.9862, 0.4866, 0.0000] },
      { name: 'Code', field: 'severity_code' as keyof ClaimData, weights: [0.4864, 0.3803, 0.8746, 0.0000] }
    ];

    const analyzeFactor = (factorName: string, field: keyof ClaimData, weights: number[]) => {
      const weightVariance: Record<number, number[]> = {};
      
      data.forEach(claim => {
        const weight = claim[field] as number;
        if (!weightVariance[weight]) weightVariance[weight] = [];
        weightVariance[weight].push(Math.abs(claim.variance_pct));
      });

      const weightStats = weights.map(w => {
        const variances = weightVariance[w] || [];
        const avgVar = variances.length > 0 ? variances.reduce((a, b) => a + b, 0) / variances.length : 0;
        return {
          weight: w,
          avgVariance: avgVar,
          count: variances.length,
          needsReview: avgVar > 25 || (w === Math.max(...weights) && avgVar > 20)
        };
      }).sort((a, b) => b.avgVariance - a.avgVariance);

      const maxVarianceWeight = weightStats[0];
      const needsRecalibration = maxVarianceWeight.avgVariance > 25 || weightStats.filter(w => w.needsReview).length > weights.length / 2;

      return {
        factorName,
        field,
        weights: weightStats,
        needsRecalibration,
        maxVarianceWeight,
        recommendation: needsRecalibration 
          ? `High variance detected (${maxVarianceWeight.avgVariance.toFixed(1)}%). Review weight ${maxVarianceWeight.weight}.`
          : `Performing well. Average variance below threshold.`
      };
    };

    const causationAnalysis = causationFactors.map(f => analyzeFactor(f.name, f.field, f.weights));
    const severityAnalysis = severityFactors.map(f => analyzeFactor(f.name, f.field, f.weights));

    return {
      causation: causationAnalysis,
      severity: severityAnalysis,
      totalNeedingRecalibration: [...causationAnalysis, ...severityAnalysis].filter(f => f.needsRecalibration).length
    };
  }, [data]);

  // ===== STATISTICAL WEIGHT OPTIMIZATION & SIMULATION =====
  const weightOptimization = useMemo(() => {
    const causationFactors = [
      { name: 'Causation Probability', field: 'causation_probability' as keyof ClaimData, weights: [0.3257, 0.2212, 0.4478, 0.0000] },
      { name: 'Tx Delay', field: 'causation_tx_delay' as keyof ClaimData, weights: [0.1226, 0.0000] },
      { name: 'Tx Gaps', field: 'causation_tx_gaps' as keyof ClaimData, weights: [0.1313, 0.0000] },
      { name: 'Compliance', field: 'causation_compliance' as keyof ClaimData, weights: [0.1474, 0.0864] }
    ];

    const severityFactors = [
      { name: 'Allowed Tx Period', field: 'severity_allowed_tx_period' as keyof ClaimData, weights: [1.4488, 0.0000, 2.3490, 3.1606, 3.8533, 4.3507] },
      { name: 'Initial Tx', field: 'severity_initial_tx' as keyof ClaimData, weights: [1.5445, 1.2406, 0.6738, 0.0000] },
      { name: 'Injections', field: 'severity_injections' as keyof ClaimData, weights: [0.0000, 1.9855, 3.0855, 3.4370, 5.1228] },
      { name: 'Objective Findings', field: 'severity_objective_findings' as keyof ClaimData, weights: [2.7611, 0.0] },
      { name: 'Pain Mgmt', field: 'severity_pain_mgmt' as keyof ClaimData, weights: [0.0000, 0.6396, 1.1258] },
      { name: 'Type of Tx', field: 'severity_type_tx' as keyof ClaimData, weights: [2.0592, 3.2501] },
      { name: 'Injury Site', field: 'severity_injury_site' as keyof ClaimData, weights: [1.8450, 1.1767, 0.9862, 0.4866, 0.0000] },
      { name: 'Code', field: 'severity_code' as keyof ClaimData, weights: [0.4864, 0.3803, 0.8746, 0.0000] }
    ];

    const optimizeFactor = (factorName: string, field: keyof ClaimData, currentWeights: number[]) => {
      // Collect variance data by weight
      const weightData: Record<number, { variances: number[]; settlements: number[] }> = {};
      
      data.forEach(claim => {
        const weight = claim[field] as number;
        if (!weightData[weight]) weightData[weight] = { variances: [], settlements: [] };
        weightData[weight].variances.push(Math.abs(claim.variance_pct));
        weightData[weight].settlements.push(claim.DOLLARAMOUNTHIGH);
      });

      // Calculate statistics for each weight
      const weightStats = currentWeights.map(w => {
        const variances = weightData[w]?.variances || [];
        const settlements = weightData[w]?.settlements || [];
        const avgVar = variances.length > 0 ? variances.reduce((a, b) => a + b, 0) / variances.length : 0;
        const avgSettlement = settlements.length > 0 ? settlements.reduce((a, b) => a + b, 0) / settlements.length : 0;
        const stdDev = variances.length > 0 
          ? Math.sqrt(variances.reduce((sum, v) => sum + Math.pow(v - avgVar, 2), 0) / variances.length)
          : 0;
        
        return {
          currentWeight: w,
          avgVariance: avgVar,
          stdDev,
          count: variances.length,
          avgSettlement,
          performanceScore: avgVar > 0 ? 1 / avgVar : 1000 // Inverse variance = better performance
        };
      });

      // Calculate correlation between weight value and variance
      const weights = weightStats.map(w => w.currentWeight);
      const variances = weightStats.map(w => w.avgVariance);
      const n = weights.length;
      
      const meanWeight = weights.reduce((a, b) => a + b, 0) / n;
      const meanVariance = variances.reduce((a, b) => a + b, 0) / n;
      
      const covariance = weights.reduce((sum, w, i) => 
        sum + (w - meanWeight) * (variances[i] - meanVariance), 0) / n;
      const weightStdDev = Math.sqrt(weights.reduce((sum, w) => 
        sum + Math.pow(w - meanWeight, 2), 0) / n);
      const varianceStdDev = Math.sqrt(variances.reduce((sum, v) => 
        sum + Math.pow(v - meanVariance, 2), 0) / n);
      
      const correlation = weightStdDev > 0 && varianceStdDev > 0 
        ? covariance / (weightStdDev * varianceStdDev)
        : 0;

      // Propose optimized weights using inverse variance weighting
      const totalPerformance = weightStats.reduce((sum, w) => sum + w.performanceScore, 0);
      const proposedWeights = weightStats.map(w => {
        // Normalize performance score to maintain weight scale
        const maxCurrentWeight = Math.max(...currentWeights);
        const scaleFactor = maxCurrentWeight / totalPerformance;
        const optimizedWeight = w.performanceScore * scaleFactor * (currentWeights.length / 2);
        
        return {
          ...w,
          proposedWeight: parseFloat(optimizedWeight.toFixed(4)),
          improvement: w.avgVariance > 0 ? ((w.avgVariance - meanVariance) / w.avgVariance * 100) : 0,
          recommendation: w.avgVariance > 25 
            ? `Reduce weight from ${w.currentWeight} to ${optimizedWeight.toFixed(4)}`
            : w.avgVariance < 15
            ? `Maintain or increase weight (performing well)`
            : `Monitor performance`
        };
      });

      // Calculate expected variance reduction with proposed weights
      const currentAvgVariance = meanVariance;
      const expectedVarianceReduction = weightStats
        .filter(w => w.avgVariance > 25)
        .reduce((sum, w) => sum + (w.avgVariance - meanVariance), 0) / weightStats.length;

      return {
        factorName,
        field,
        correlation,
        correlationStrength: Math.abs(correlation) > 0.7 ? 'Strong' : Math.abs(correlation) > 0.4 ? 'Moderate' : 'Weak',
        currentAvgVariance,
        expectedVarianceReduction: Math.max(0, expectedVarianceReduction),
        proposedWeights,
        needsOptimization: Math.abs(correlation) > 0.3 && currentAvgVariance > 20
      };
    };

    const causationOptimization = causationFactors.map(f => optimizeFactor(f.name, f.field, f.weights));
    const severityOptimization = severityFactors.map(f => optimizeFactor(f.name, f.field, f.weights));

    // Calculate overall simulation metrics
    const currentOverallVariance = data.reduce((sum, c) => sum + Math.abs(c.variance_pct), 0) / data.length;
    
    // Simulate variance with optimized weights (simplified simulation)
    const allOptimizations = [...causationOptimization, ...severityOptimization];
    const totalExpectedReduction = allOptimizations.reduce((sum, opt) => sum + opt.expectedVarianceReduction, 0) / allOptimizations.length;
    const simulatedVariance = Math.max(0, currentOverallVariance - totalExpectedReduction);

    return {
      causation: causationOptimization,
      severity: severityOptimization,
      currentOverallVariance,
      simulatedVariance,
      expectedImprovement: ((currentOverallVariance - simulatedVariance) / currentOverallVariance * 100),
      totalNeedingOptimization: allOptimizations.filter(opt => opt.needsOptimization).length
    };
  }, [data]);

  return (
    <div className="space-y-6">
      {/* ===== 1. EXECUTIVE SUMMARY ===== */}
      <Card className="border-primary/20 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-2xl">
            <BarChart3 className="h-6 w-6 text-primary" />
            Executive Summary
          </CardTitle>
          <CardDescription>High-level model performance overview and key insights</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-muted/30 rounded-lg p-4 border border-border">
              <div className="text-sm text-muted-foreground mb-1">Total Claims</div>
              <div className="text-2xl font-bold">{executiveSummary.totalClaims.toLocaleString()}</div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 border border-border">
              <div className="text-sm text-muted-foreground mb-1">Avg Variance</div>
              <div className="text-2xl font-bold text-warning">{executiveSummary.avgVariance.toFixed(1)}%</div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 border border-border">
              <div className="text-sm text-muted-foreground mb-1">Model Accuracy</div>
              <div className="text-2xl font-bold text-success">{executiveSummary.modelAccuracy.toFixed(1)}%</div>
            </div>
            <div className="bg-muted/30 rounded-lg p-4 border border-border">
              <div className="text-sm text-muted-foreground mb-1">High Variance Claims</div>
              <div className="text-2xl font-bold text-destructive">{executiveSummary.highVarianceClaims}</div>
            </div>
          </div>

          <div className="bg-info/10 border border-info/20 rounded-lg p-4">
            <h4 className="font-semibold text-info mb-3 flex items-center gap-2">
              <Info className="h-4 w-4" />
              Top Variance Drivers
            </h4>
            <div className="space-y-2">
              {executiveSummary.topDrivers.map((driver, idx) => (
                <div key={idx} className="flex items-center justify-between bg-background/50 rounded p-2">
                  <span className="text-sm">
                    <span className="font-medium">{driver.factor}</span>: {driver.value}
                  </span>
                  <div className="flex items-center gap-2">
                    <Badge variant={driver.avgVariance > 30 ? "destructive" : "warning"}>
                      {driver.avgVariance.toFixed(1)}%
                    </Badge>
                    <span className="text-xs text-muted-foreground">{driver.count} claims</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ===== 2. DETAILED ANALYSIS ===== */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-2xl">
            <Activity className="h-6 w-6 text-primary" />
            Detailed Factor Analysis
          </CardTitle>
          <CardDescription>Deep dive into factor combinations and multi-injury patterns</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Multi-Injury Analysis */}
          <div className="bg-warning/10 border border-warning/20 rounded-lg p-5">
            <h4 className="font-semibold text-warning mb-3 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Multi-Injury Claim Analysis
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="bg-background/50 rounded p-3">
                <div className="text-xs text-muted-foreground mb-1">Single Injury Claims</div>
                <div className="text-xl font-bold">{multiInjuryAnalysis.singleCount}</div>
                <div className="text-sm text-muted-foreground">Avg Variance: {multiInjuryAnalysis.singleAvgVariance.toFixed(1)}%</div>
              </div>
              <div className="bg-background/50 rounded p-3">
                <div className="text-xs text-muted-foreground mb-1">Multi-Injury Claims</div>
                <div className="text-xl font-bold">{multiInjuryAnalysis.multiCount}</div>
                <div className="text-sm text-muted-foreground">Avg Variance: {multiInjuryAnalysis.multiAvgVariance.toFixed(1)}%</div>
              </div>
              <div className="bg-background/50 rounded p-3">
                <div className="text-xs text-muted-foreground mb-1">Variance Differential</div>
                <div className={`text-xl font-bold ${multiInjuryAnalysis.varianceDifferential > 0 ? 'text-destructive' : 'text-success'}`}>
                  {multiInjuryAnalysis.varianceDifferential > 0 ? '+' : ''}{multiInjuryAnalysis.varianceDifferential.toFixed(1)}%
                </div>
              </div>
            </div>
            <div className="bg-background/50 rounded p-3">
              <p className="text-sm font-medium">{multiInjuryAnalysis.pattern}</p>
              <p className="text-xs text-muted-foreground mt-2">
                Multi-injury claims average ${Math.round(multiInjuryAnalysis.multiAvgSettlement).toLocaleString()} settlements vs. 
                ${Math.round(multiInjuryAnalysis.singleAvgSettlement).toLocaleString()} for single-injury claims.
                {multiInjuryAnalysis.varianceDifferential > 15 && 
                  " The model significantly underperforms on complex multi-injury cases, suggesting need for enhanced multi-injury prediction algorithms."}
              </p>
            </div>
          </div>

          {/* Factor Combination Analysis */}
          <div>
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              High-Variance Factor Combinations
            </h4>
            <p className="text-sm text-muted-foreground mb-4">
              These factor combinations show the poorest model performance. Click to see detailed breakdown and contributing factors.
            </p>
            <div className="space-y-3 max-h-[500px] overflow-y-auto">
              {topProblemCombos.map((combo, idx) => (
                <div
                  key={combo.key}
                  onClick={() => setSelectedCombo(combo.key)}
                  className={`border rounded-lg p-4 cursor-pointer transition-all ${
                    selectedCombo === combo.key
                      ? 'border-primary bg-primary/5 shadow-md'
                      : 'border-border hover:border-primary/50 hover:bg-accent'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline" className="font-mono text-xs">#{idx + 1}</Badge>
                        <span className="font-semibold">{combo.displayName}</span>
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Impact Life: {combo.impactLife} | Avg Severity: {combo.avgSeverity.toFixed(1)} | {combo.count} claims
                      </div>
                    </div>
                    <Badge variant={combo.avgVariance > 35 ? "destructive" : "warning"} className="ml-2">
                      {combo.avgVariance.toFixed(1)}% variance
                    </Badge>
                  </div>
                  
                  {selectedCombo === combo.key && (
                    <div className="border-t border-border pt-3 mt-3 space-y-2">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div className="bg-muted/30 rounded p-3">
                          <div className="text-xs text-muted-foreground mb-1">Primary Geographic Driver</div>
                          <div className="font-semibold">{combo.topCountyDriver?.name}</div>
                          <div className="text-sm text-destructive">{combo.topCountyDriver?.avgVar.toFixed(1)}% avg variance</div>
                        </div>
                        <div className="bg-muted/30 rounded p-3">
                          <div className="text-xs text-muted-foreground mb-1">Avg Settlement</div>
                          <div className="font-semibold">${Math.round(combo.avgSettlement).toLocaleString()}</div>
                        </div>
                      </div>
                      <div className="bg-info/10 rounded p-3 text-sm">
                        <span className="font-medium">Insight: </span>
                        This combination requires {combo.avgVariance > 40 ? 'urgent' : 'significant'} recalibration. 
                        {combo.avgVariance > 40 && ' Consider creating a specialized sub-model for this segment.'}
                        {combo.avgVariance <= 40 && combo.avgVariance > 30 && ' Geographic factors appear to be major contributors.'}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Well-Performing Combinations */}
          <div>
            <h4 className="font-semibold mb-3 flex items-center gap-2 text-success">
              <CheckCircle2 className="h-5 w-5" />
              Well-Performing Combinations (Keep Current Parameters)
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {wellPerformingCombos.map((combo) => (
                <div key={combo.key} className="border border-success/30 bg-success/5 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-sm">{combo.displayName}</span>
                    <Badge variant="success">{combo.avgVariance.toFixed(1)}%</Badge>
                  </div>
                  <div className="text-xs text-muted-foreground">{combo.count} claims | No recalibration needed</div>
                </div>
              ))}
            </div>
          </div>

          {/* County Variance Analysis */}
          <div>
            <h4 className="font-semibold mb-3">Geographic Variance Patterns</h4>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-muted/50 border-b border-border">
                  <tr>
                    <th className="px-3 py-2 text-left font-semibold">County</th>
                    <th className="px-3 py-2 text-left font-semibold">Tendency</th>
                    <th className="px-3 py-2 text-left font-semibold">Avg Variance</th>
                    <th className="px-3 py-2 text-left font-semibold">Claims</th>
                  </tr>
                </thead>
                <tbody>
                  {highVarianceCounties.slice(0, 5).map((county) => (
                    <tr key={county.name} className="border-b border-border hover:bg-muted/20">
                      <td className="px-3 py-2 font-medium">{county.name}, {county.state}</td>
                      <td className="px-3 py-2">
                        <Badge variant={county.tendencyBadge}>
                          {county.tendency === 'Liberal' && <TrendingUp className="h-3 w-3 mr-1 inline" />}
                          {county.tendency === 'Conservative' && <TrendingDown className="h-3 w-3 mr-1 inline" />}
                          {county.tendency}
                        </Badge>
                      </td>
                      <td className={`px-3 py-2 font-semibold ${county.avgSignedVariance > 0 ? 'text-destructive' : 'text-success'}`}>
                        {county.avgSignedVariance > 0 ? '+' : ''}{county.avgSignedVariance.toFixed(1)}%
                      </td>
                      <td className="px-3 py-2">{county.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ===== 3. MODEL RECOMMENDATIONS ===== */}
      <Card className="border-success/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-2xl">
            <Users className="h-6 w-6 text-success" />
            Model Recalibration Recommendations
          </CardTitle>
          <CardDescription>Data-driven recommendations for model improvement and adjuster selection</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* What to Change */}
          <div>
            <h4 className="font-semibold mb-3 flex items-center gap-2 text-destructive">
              <XCircle className="h-5 w-5" />
              Priority Areas for Recalibration
            </h4>
            <div className="space-y-3">
              {topProblemCombos.slice(0, 5).map((combo, idx) => (
                <div key={combo.key} className="bg-destructive/5 border border-destructive/20 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <span className="font-medium">{combo.displayName}</span>
                      <div className="text-xs text-muted-foreground mt-1">
                        Avg Variance: {combo.avgVariance.toFixed(1)}% | {combo.count} claims
                      </div>
                    </div>
                    <Badge variant="destructive">Priority {idx + 1}</Badge>
                  </div>
                  <div className="text-sm bg-background/50 rounded p-2 mt-2">
                    <span className="font-medium">Recommendation: </span>
                    {combo.avgVariance > 40 ? 
                      `Critical recalibration needed. Consider creating specialized parameters for ${combo.injuryGroup} cases in ${combo.venueRating} rated venues.` :
                      `Moderate adjustment required. Focus on ${combo.topCountyDriver?.name} geographic patterns and ${combo.severityBucket} severity modeling.`
                    }
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* What to Keep */}
          <div>
            <h4 className="font-semibold mb-3 flex items-center gap-2 text-success">
              <CheckCircle2 className="h-5 w-5" />
              Maintain Current Parameters
            </h4>
            <div className="bg-success/5 border border-success/20 rounded-lg p-4">
              <p className="text-sm mb-3">
                These combinations show strong model performance. Avoid recalibrating these segments to prevent regression.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                {wellPerformingCombos.map((combo) => (
                  <div key={combo.key} className="bg-background/50 rounded p-2 text-sm">
                    <div className="font-medium">{combo.displayName}</div>
                    <div className="text-xs text-success">{combo.avgVariance.toFixed(1)}% variance ✓</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Adjuster Selection */}
          <div>
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              Recommended Adjusters for Recalibration
            </h4>
            <p className="text-sm text-muted-foreground mb-4">
              Adjusters are ranked by calibration score based on: low variance (40%), consistency (30%), experience (20%), and segment diversity (10%).
              Higher scores indicate better candidates for training data in model recalibration.
            </p>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {recommendedForCalibration.map((adjuster, idx) => (
                <div
                  key={adjuster.name}
                  className={`border rounded-lg p-4 ${
                    adjuster.calibrationScore > 80 ? 'border-success bg-success/5' :
                    adjuster.calibrationScore > 70 ? 'border-primary bg-primary/5' :
                    'border-border'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${
                        idx === 0 ? 'bg-success text-success-foreground' :
                        idx === 1 ? 'bg-primary text-primary-foreground' :
                        idx === 2 ? 'bg-secondary text-secondary-foreground' :
                        'bg-muted text-muted-foreground'
                      }`}>
                        {idx + 1}
                      </div>
                      <div>
                        <div className="font-semibold text-lg">{adjuster.name}</div>
                        <div className="text-xs text-muted-foreground">
                          {adjuster.totalClaims} claims | {adjuster.bestCombo?.combo || 'Various segments'}
                        </div>
                      </div>
                    </div>
                    <Badge variant={adjuster.calibrationScore > 80 ? "success" : "default"} className="text-base px-3 py-1">
                      Score: {adjuster.calibrationScore.toFixed(0)}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                    <div className="bg-muted/30 rounded p-2">
                      <div className="text-xs text-muted-foreground">Avg Variance</div>
                      <div className="font-semibold text-success">{adjuster.avgVariance.toFixed(1)}%</div>
                    </div>
                    <div className="bg-muted/30 rounded p-2">
                      <div className="text-xs text-muted-foreground">Consistency</div>
                      <div className="font-semibold">{(adjuster.consistency * 100).toFixed(0)}%</div>
                    </div>
                    <div className="bg-muted/30 rounded p-2">
                      <div className="text-xs text-muted-foreground">Experience</div>
                      <div className="font-semibold">{adjuster.totalClaims} claims</div>
                    </div>
                    <div className="bg-muted/30 rounded p-2">
                      <div className="text-xs text-muted-foreground">Diversity</div>
                      <div className="font-semibold">{(adjuster.diversityScore * 100).toFixed(0)}%</div>
                    </div>
                  </div>

                  <div className="bg-info/10 rounded p-3 text-sm">
                    <span className="font-medium text-info">Why Recommended: </span>
                    {adjuster.calibrationScore > 80 && 
                      `Exceptional performer with ${adjuster.avgVariance.toFixed(1)}% variance across ${adjuster.totalClaims} claims. High consistency (${(adjuster.consistency * 100).toFixed(0)}%) makes their decisions ideal training data. `}
                    {adjuster.calibrationScore > 70 && adjuster.calibrationScore <= 80 && 
                      `Strong performer with good consistency. Their experience across ${adjuster.totalClaims} claims provides valuable training signal. `}
                    {adjuster.bestCombo && 
                      `Best performance in ${adjuster.bestCombo.combo} segment (${adjuster.bestCombo.avgVar.toFixed(1)}% variance).`}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* ===== 4. MODEL FACTOR WEIGHT ANALYSIS ===== */}
      <Card className="border-warning/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-warning" />
            Model Factor Weight Analysis
          </CardTitle>
          <CardDescription>
            Evaluate causation and severity factor weights to determine if recalibration is needed
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Summary */}
          <div className="bg-warning/10 border border-warning/20 rounded-lg p-4">
            <h4 className="font-semibold text-warning mb-2">Analysis Summary</h4>
            <p className="text-sm text-muted-foreground">
              {factorWeightAnalysis.totalNeedingRecalibration === 0 
                ? "All factor weights are performing within acceptable variance thresholds. No immediate recalibration needed."
                : `${factorWeightAnalysis.totalNeedingRecalibration} factor${factorWeightAnalysis.totalNeedingRecalibration > 1 ? 's' : ''} showing high variance and requiring review for potential recalibration.`
              }
            </p>
          </div>

          {/* Causation Factors */}
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Target className="h-5 w-5" />
              Causation Factors
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {factorWeightAnalysis.causation.map((factor) => (
                <div key={factor.factorName} className={`border rounded-lg p-4 ${factor.needsRecalibration ? 'border-destructive/50 bg-destructive/5' : 'border-border'}`}>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-sm">{factor.factorName}</h4>
                    {factor.needsRecalibration ? (
                      <Badge variant="destructive" className="text-xs">
                        <AlertTriangle className="h-3 w-3 mr-1" />
                        Review
                      </Badge>
                    ) : (
                      <Badge variant="success" className="text-xs">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        OK
                      </Badge>
                    )}
                  </div>
                  <div className="space-y-2 mb-3">
                    {factor.weights.slice(0, 3).map((w, idx) => (
                      <div key={idx} className="flex justify-between text-xs">
                        <span className="text-muted-foreground">Weight {w.weight}:</span>
                        <span className={w.needsReview ? 'text-destructive font-semibold' : ''}>
                          {w.avgVariance.toFixed(1)}% ({w.count} claims)
                        </span>
                      </div>
                    ))}
                    {factor.weights.length > 3 && (
                      <div className="text-xs text-muted-foreground italic">
                        +{factor.weights.length - 3} more weights...
                      </div>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground border-t border-border pt-2">
                    {factor.recommendation}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Severity Factors */}
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Target className="h-5 w-5" />
              Severity Factors
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {factorWeightAnalysis.severity.map((factor) => (
                <div key={factor.factorName} className={`border rounded-lg p-4 ${factor.needsRecalibration ? 'border-destructive/50 bg-destructive/5' : 'border-border'}`}>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-sm">{factor.factorName}</h4>
                    {factor.needsRecalibration ? (
                      <Badge variant="destructive" className="text-xs">
                        <AlertTriangle className="h-3 w-3 mr-1" />
                        Review
                      </Badge>
                    ) : (
                      <Badge variant="success" className="text-xs">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        OK
                      </Badge>
                    )}
                  </div>
                  <div className="space-y-2 mb-3">
                    {factor.weights.slice(0, 3).map((w, idx) => (
                      <div key={idx} className="flex justify-between text-xs">
                        <span className="text-muted-foreground">Weight {w.weight}:</span>
                        <span className={w.needsReview ? 'text-destructive font-semibold' : ''}>
                          {w.avgVariance.toFixed(1)}% ({w.count} claims)
                        </span>
                      </div>
                    ))}
                    {factor.weights.length > 3 && (
                      <div className="text-xs text-muted-foreground italic">
                        +{factor.weights.length - 3} more weights...
                      </div>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground border-t border-border pt-2">
                    {factor.recommendation}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Recalibration Recommendations */}
          {factorWeightAnalysis.totalNeedingRecalibration > 0 && (
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
              <h4 className="font-semibold text-destructive mb-3 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                Recommended Actions
              </h4>
              <ul className="space-y-2 text-sm">
                {[...factorWeightAnalysis.causation, ...factorWeightAnalysis.severity]
                  .filter(f => f.needsRecalibration)
                  .map((factor, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-destructive mt-0.5">•</span>
                      <span>
                        <span className="font-semibold">{factor.factorName}:</span> {factor.recommendation}
                      </span>
                    </li>
                  ))
                }
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ===== 5. STATISTICAL WEIGHT OPTIMIZATION & SIMULATION ===== */}
      <Card className="border-primary/20 shadow-lg">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-xl">
            <TrendingUp className="h-6 w-6 text-success" />
            Statistical Weight Optimization & Impact Simulation
          </CardTitle>
          <CardDescription>
            Regression-based analysis proposing optimized factor weights with expected variance reduction
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Overall Simulation Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-primary/10 to-primary/5 rounded-lg p-4 border border-primary/20">
              <div className="text-sm text-muted-foreground mb-1">Current Avg Variance</div>
              <div className="text-2xl font-bold text-primary">{weightOptimization.currentOverallVariance.toFixed(2)}%</div>
            </div>
            <div className="bg-gradient-to-br from-success/10 to-success/5 rounded-lg p-4 border border-success/20">
              <div className="text-sm text-muted-foreground mb-1">Simulated Variance (Optimized)</div>
              <div className="text-2xl font-bold text-success">{weightOptimization.simulatedVariance.toFixed(2)}%</div>
            </div>
            <div className="bg-gradient-to-br from-warning/10 to-warning/5 rounded-lg p-4 border border-warning/20">
              <div className="text-sm text-muted-foreground mb-1">Expected Improvement</div>
              <div className="text-2xl font-bold text-warning flex items-center gap-1">
                <TrendingDown className="h-5 w-5" />
                {weightOptimization.expectedImprovement.toFixed(1)}%
              </div>
            </div>
          </div>

          {/* Optimization Insights */}
          <div className="bg-info/10 border border-info/20 rounded-lg p-4">
            <h4 className="font-semibold text-info mb-2 flex items-center gap-2">
              <Info className="h-4 w-4" />
              Optimization Analysis
            </h4>
            <p className="text-sm text-muted-foreground">
              {weightOptimization.totalNeedingOptimization === 0 
                ? "Current weights show weak correlation with variance. All factors are performing optimally."
                : `${weightOptimization.totalNeedingOptimization} factor${weightOptimization.totalNeedingOptimization > 1 ? 's show' : ' shows'} significant correlation with variance and can be optimized. Statistical regression suggests adjusting these weights could reduce variance by ${weightOptimization.expectedImprovement.toFixed(1)}%.`
              }
            </p>
          </div>

          {/* Causation Factor Optimization */}
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              Causation Factors - Proposed Weights
            </h3>
            <div className="space-y-3">
              {weightOptimization.causation.map((factor) => (
                <div key={factor.factorName} className={`border rounded-lg p-4 ${factor.needsOptimization ? 'border-warning/50 bg-warning/5' : 'border-border'}`}>
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h4 className="font-semibold text-sm">{factor.factorName}</h4>
                      <div className="text-xs text-muted-foreground mt-1">
                        Correlation: <span className={`font-semibold ${Math.abs(factor.correlation) > 0.5 ? 'text-destructive' : 'text-success'}`}>
                          {factor.correlation.toFixed(3)}
                        </span> ({factor.correlationStrength})
                      </div>
                    </div>
                    {factor.needsOptimization ? (
                      <Badge variant="warning" className="text-xs">
                        <TrendingUp className="h-3 w-3 mr-1" />
                        Optimize
                      </Badge>
                    ) : (
                      <Badge variant="success" className="text-xs">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        Optimal
                      </Badge>
                    )}
                  </div>
                  
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-border">
                          <th className="text-left py-2 text-muted-foreground">Current Weight</th>
                          <th className="text-right py-2 text-muted-foreground">Avg Variance</th>
                          <th className="text-right py-2 text-muted-foreground">Claims</th>
                          <th className="text-right py-2 text-success">Proposed Weight</th>
                          <th className="text-left py-2 px-2 text-muted-foreground">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {factor.proposedWeights.map((w, idx) => (
                          <tr key={idx} className="border-b border-border/50">
                            <td className="py-2">{w.currentWeight}</td>
                            <td className={`text-right py-2 ${w.avgVariance > 25 ? 'text-destructive font-semibold' : ''}`}>
                              {w.avgVariance.toFixed(1)}%
                            </td>
                            <td className="text-right py-2">{w.count}</td>
                            <td className="text-right py-2 font-semibold text-success">{w.proposedWeight}</td>
                            <td className="text-left py-2 px-2 text-xs text-muted-foreground italic">
                              {w.recommendation}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {factor.expectedVarianceReduction > 0 && (
                    <div className="mt-3 bg-success/10 border border-success/20 rounded p-2 text-xs">
                      <span className="font-semibold text-success">Expected Impact:</span> Reducing variance by ~{factor.expectedVarianceReduction.toFixed(1)}% for this factor
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Severity Factor Optimization */}
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Target className="h-5 w-5 text-primary" />
              Severity Factors - Proposed Weights
            </h3>
            <div className="space-y-3">
              {weightOptimization.severity.map((factor) => (
                <div key={factor.factorName} className={`border rounded-lg p-4 ${factor.needsOptimization ? 'border-warning/50 bg-warning/5' : 'border-border'}`}>
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h4 className="font-semibold text-sm">{factor.factorName}</h4>
                      <div className="text-xs text-muted-foreground mt-1">
                        Correlation: <span className={`font-semibold ${Math.abs(factor.correlation) > 0.5 ? 'text-destructive' : 'text-success'}`}>
                          {factor.correlation.toFixed(3)}
                        </span> ({factor.correlationStrength})
                      </div>
                    </div>
                    {factor.needsOptimization ? (
                      <Badge variant="warning" className="text-xs">
                        <TrendingUp className="h-3 w-3 mr-1" />
                        Optimize
                      </Badge>
                    ) : (
                      <Badge variant="success" className="text-xs">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        Optimal
                      </Badge>
                    )}
                  </div>
                  
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="border-b border-border">
                          <th className="text-left py-2 text-muted-foreground">Current Weight</th>
                          <th className="text-right py-2 text-muted-foreground">Avg Variance</th>
                          <th className="text-right py-2 text-muted-foreground">Claims</th>
                          <th className="text-right py-2 text-success">Proposed Weight</th>
                          <th className="text-left py-2 px-2 text-muted-foreground">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {factor.proposedWeights.map((w, idx) => (
                          <tr key={idx} className="border-b border-border/50">
                            <td className="py-2">{w.currentWeight}</td>
                            <td className={`text-right py-2 ${w.avgVariance > 25 ? 'text-destructive font-semibold' : ''}`}>
                              {w.avgVariance.toFixed(1)}%
                            </td>
                            <td className="text-right py-2">{w.count}</td>
                            <td className="text-right py-2 font-semibold text-success">{w.proposedWeight}</td>
                            <td className="text-left py-2 px-2 text-xs text-muted-foreground italic">
                              {w.recommendation}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {factor.expectedVarianceReduction > 0 && (
                    <div className="mt-3 bg-success/10 border border-success/20 rounded p-2 text-xs">
                      <span className="font-semibold text-success">Expected Impact:</span> Reducing variance by ~{factor.expectedVarianceReduction.toFixed(1)}% for this factor
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Implementation Notes */}
          <div className="bg-primary/10 border border-primary/20 rounded-lg p-4">
            <h4 className="font-semibold text-primary mb-3 flex items-center gap-2">
              <Info className="h-4 w-4" />
              Implementation Notes
            </h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="text-primary mt-0.5">•</span>
                <span>Proposed weights calculated using inverse variance methodology - weights with lower variance are prioritized</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary mt-0.5">•</span>
                <span>Correlation analysis identifies relationship between weight magnitude and claim variance</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary mt-0.5">•</span>
                <span>Simulation assumes linear relationship and independent factors (actual results may vary)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary mt-0.5">•</span>
                <span>Recommend A/B testing proposed weights on subset of claims before full deployment</span>
              </li>
            </ul>
          </div>
        </CardContent>
      </Card>

      {/* ===== 6. ADDITIONAL INSIGHTS ===== */}
      <Card>
        <CardHeader>
          <CardTitle>Temporal Variance Trends</CardTitle>
          <CardDescription>Track model performance consistency over time</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={temporalData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '0.5rem',
                }}
              />
              <Legend />
              <Line type="monotone" dataKey="avgVariance" name="Avg Variance (%)" stroke="hsl(var(--primary))" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
