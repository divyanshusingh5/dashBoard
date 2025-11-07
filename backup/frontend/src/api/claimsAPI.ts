import { apiClient } from './client';

export interface ClaimData {
  [key: string]: any;
}

export interface PaginatedClaimsResponse {
  claims: ClaimData[];
  total: number;
  page: number;
  page_size: number;
}

export interface AggregatedDataResponse {
  adjuster: any[];
  injury: any[];
  state: any[];
  county: any[];
  year: any[];
  total_records: number;
}

export interface KPIData {
  total_claims: number;
  total_settlement: number;
  avg_settlement: number;
  avg_variance: number;
  avg_variance_pct: number;
  median_settlement: number;
  total_overestimated: number;
  total_underestimated: number;
}

export interface FilterOptions {
  injury_groups: string[];
  adjusters: string[];
  states: string[];
  counties: string[];
  years: number[];
}

export const claimsAPI = {
  // Get paginated claims
  getClaims: async (params?: {
    page?: number;
    page_size?: number;
    injury_group?: string[];
    adjuster?: string[];
    state?: string[];
    year?: number[];
  }): Promise<PaginatedClaimsResponse> => {
    const queryParams = new URLSearchParams();

    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params?.injury_group) params.injury_group.forEach(ig => queryParams.append('injury_group', ig));
    if (params?.adjuster) params.adjuster.forEach(a => queryParams.append('adjuster', a));
    if (params?.state) params.state.forEach(s => queryParams.append('state', s));
    if (params?.year) params.year.forEach(y => queryParams.append('year', y.toString()));

    const url = `/claims/claims${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    return apiClient.get<PaginatedClaimsResponse>(url);
  },

  // Get all claims (use with caution)
  getFullClaims: async (): Promise<{ claims: ClaimData[]; total: number }> => {
    return apiClient.get('/claims/claims/full');
  },

  // Get aggregated data
  getAggregatedData: async (): Promise<AggregatedDataResponse> => {
    return apiClient.get('/claims/claims/aggregated');
  },

  // Get KPIs
  getKPIs: async (): Promise<KPIData> => {
    return apiClient.get('/claims/claims/kpis');
  },

  // Get filter options
  getFilterOptions: async (): Promise<FilterOptions> => {
    return apiClient.get('/claims/claims/filters');
  },

  // Get claims statistics
  getClaimsStats: async () => {
    return apiClient.get('/claims/claims/stats');
  },
};

export default claimsAPI;
