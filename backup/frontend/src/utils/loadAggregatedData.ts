import Papa from 'papaparse';

// Type definitions for aggregated data
export interface YearSeveritySummary {
  year: number;
  caution_level: string;
  claim_count: number;
  avg_settlement: number;
  avg_predicted: number;
  avg_days: number;
  total_settlement: number;
}

export interface CountyYearSummary {
  county: string;
  year: number;
  claim_count: number;
  total_settlement: number;
  avg_settlement: number;
  high_variance_pct: number;
}

export interface InjuryTypeSummary {
  injury_group: string;
  claim_count: number;
  avg_settlement: number;
  avg_days_to_settlement: number;
  total_settlement: number;
}

export interface TreatmentSummary {
  treatment_course: string;
  claim_count: number;
  avg_settlement: number;
  avg_severity_score: number;
  total_settlement: number;
}

// Generic CSV loader
async function loadCsvFile<T>(filename: string): Promise<T[]> {
  try {
    const response = await fetch(`/${filename}`);
    if (!response.ok) {
      throw new Error(`Failed to load ${filename}`);
    }

    const csvText = await response.text();

    return new Promise((resolve, reject) => {
      Papa.parse(csvText, {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
        complete: (results) => {
          resolve(results.data as T[]);
        },
        error: (error) => {
          reject(error);
        }
      });
    });
  } catch (error) {
    console.error(`Error loading ${filename}:`, error);
    throw error;
  }
}

// Load specific aggregated data files
export async function loadYearSeveritySummary(): Promise<YearSeveritySummary[]> {
  return loadCsvFile<YearSeveritySummary>('year_severity_summary.csv');
}

export async function loadCountyYearSummary(): Promise<CountyYearSummary[]> {
  return loadCsvFile<CountyYearSummary>('county_year_summary.csv');
}

export async function loadInjuryTypeSummary(): Promise<InjuryTypeSummary[]> {
  return loadCsvFile<InjuryTypeSummary>('injury_type_summary.csv');
}

export async function loadTreatmentSummary(): Promise<TreatmentSummary[]> {
  return loadCsvFile<TreatmentSummary>('treatment_summary.csv');
}

// Load all aggregated summaries at once
export async function loadAllAggregatedData() {
  const [yearSeverity, countyYear, injuryType, treatment] = await Promise.all([
    loadYearSeveritySummary(),
    loadCountyYearSummary(),
    loadInjuryTypeSummary(),
    loadTreatmentSummary(),
  ]);

  return {
    yearSeverity,
    countyYear,
    injuryType,
    treatment,
  };
}
