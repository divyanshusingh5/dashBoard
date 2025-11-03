# Technical Architecture: Modular & Maintainable Codebase

## 🏗️ Architecture Philosophy

**SOLID Principles + Clean Architecture + Domain-Driven Design**

---

## 📐 Current Architecture Issues

### **Problems Identified:**

1. **❌ Tight Coupling**
   - Components directly fetch from API
   - Business logic mixed with UI
   - Hard to test, hard to change

2. **❌ Code Duplication**
   - Same aggregation logic in multiple files
   - Repeated type definitions
   - Copy-paste error handling

3. **❌ No Separation of Concerns**
   - Data fetching + transformation + rendering in one component
   - Backend has fat endpoints (300+ lines)
   - No service layer

4. **❌ Poor Error Handling**
   - Generic try-catch blocks
   - No error types/classes
   - No centralized error logging

5. **❌ No Testing Strategy**
   - Zero unit tests
   - No integration tests
   - Manual QA only

---

## 🎯 Target Architecture

### **Layered Architecture:**

```
┌─────────────────────────────────────────────────┐
│  PRESENTATION LAYER (React Components)          │
│  ├─ Pages (routing, layout)                     │
│  ├─ Components (UI only, no logic)              │
│  └─ Hooks (state management)                    │
├─────────────────────────────────────────────────┤
│  APPLICATION LAYER (Business Logic)             │
│  ├─ Services (API calls, data transformation)   │
│  ├─ State Management (Context/Zustand)          │
│  └─ Use Cases (complex workflows)               │
├─────────────────────────────────────────────────┤
│  DOMAIN LAYER (Core Business Rules)             │
│  ├─ Models (TypeScript interfaces)              │
│  ├─ Validators (data validation)                │
│  └─ Calculations (variance, statistics)         │
├─────────────────────────────────────────────────┤
│  INFRASTRUCTURE LAYER (External Dependencies)   │
│  ├─ API Client (Axios/Fetch wrapper)            │
│  ├─ Storage (LocalStorage, Cache)               │
│  └─ Utilities (formatting, dates)               │
└─────────────────────────────────────────────────┘
```

---

## 📁 New Folder Structure

### **Frontend:**

```
frontend/
├── src/
│   ├── app/                          # App-level config
│   │   ├── App.tsx
│   │   ├── Router.tsx
│   │   └── providers/                # Context providers
│   │       ├── ThemeProvider.tsx
│   │       ├── AuthProvider.tsx
│   │       └── QueryProvider.tsx
│   │
│   ├── features/                     # Feature-based modules
│   │   ├── claims/
│   │   │   ├── api/                  # API calls
│   │   │   │   ├── getAggregatedClaims.ts
│   │   │   │   └── getClaim ById.ts
│   │   │   ├── components/           # Feature components
│   │   │   │   ├── ClaimCard.tsx
│   │   │   │   └── ClaimTable.tsx
│   │   │   ├── hooks/                # Feature hooks
│   │   │   │   ├── useClaims.ts
│   │   │   │   └── useClaimFilters.ts
│   │   │   ├── models/               # Types & interfaces
│   │   │   │   └── claim.types.ts
│   │   │   ├── services/             # Business logic
│   │   │   │   └── claimService.ts
│   │   │   └── utils/                # Feature utilities
│   │   │       └── calculateVariance.ts
│   │   │
│   │   ├── venue-analysis/
│   │   │   ├── api/
│   │   │   │   └── getVenueShiftRecommendations.ts
│   │   │   ├── components/
│   │   │   │   ├── VenueShiftCard.tsx
│   │   │   │   └── VenueComparisonChart.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useVenueAnalysis.ts
│   │   │   ├── models/
│   │   │   │   └── venue.types.ts
│   │   │   └── services/
│   │   │       └── venueService.ts
│   │   │
│   │   ├── adjuster-performance/
│   │   │   ├── api/
│   │   │   ├── components/
│   │   │   ├── hooks/
│   │   │   └── services/
│   │   │
│   │   └── weight-recalibration/
│   │       ├── api/
│   │       ├── components/
│   │       ├── hooks/
│   │       └── services/
│   │
│   ├── shared/                       # Shared across features
│   │   ├── api/                      # Generic API client
│   │   │   ├── apiClient.ts          # Axios instance
│   │   │   ├── errorHandler.ts
│   │   │   └── interceptors.ts
│   │   ├── components/               # Reusable UI components
│   │   │   ├── MetricCard.tsx
│   │   │   ├── DataTable.tsx
│   │   │   └── FilterPanel.tsx
│   │   ├── hooks/                    # Generic hooks
│   │   │   ├── useDebounce.ts
│   │   │   └── useLocalStorage.ts
│   │   ├── types/                    # Shared types
│   │   │   └── common.types.ts
│   │   └── utils/                    # Shared utilities
│   │       ├── formatters.ts
│   │       ├── validators.ts
│   │       └── constants.ts
│   │
│   ├── pages/                        # Route pages
│   │   ├── Dashboard/
│   │   │   └── DashboardPage.tsx
│   │   ├── Recommendations/
│   │   │   └── RecommendationsPage.tsx
│   │   └── NotFound/
│   │       └── NotFoundPage.tsx
│   │
│   └── tests/                        # Test files
│       ├── unit/
│       ├── integration/
│       └── e2e/
```

### **Backend:**

```
backend/
├── app/
│   ├── api/                          # API layer
│   │   ├── dependencies.py           # Dependency injection
│   │   ├── routes/                   # Route definitions
│   │   │   ├── __init__.py
│   │   │   ├── claims.py
│   │   │   ├── venue.py
│   │   │   └── adjuster.py
│   │   └── middleware/
│   │       ├── cors.py
│   │       ├── rate_limit.py
│   │       └── logging.py
│   │
│   ├── core/                         # Core config
│   │   ├── config.py                 # Settings
│   │   ├── security.py               # Auth
│   │   └── database.py               # DB connection
│   │
│   ├── domain/                       # Business logic layer
│   │   ├── models/                   # Pydantic models
│   │   │   ├── claim.py
│   │   │   ├── venue.py
│   │   │   └── adjuster.py
│   │   ├── services/                 # Business services
│   │   │   ├── claim_service.py
│   │   │   ├── venue_service.py
│   │   │   └── analysis_service.py
│   │   └── repositories/             # Data access
│   │       ├── base_repository.py
│   │       ├── claim_repository.py
│   │       └── cache_repository.py
│   │
│   ├── infrastructure/               # External dependencies
│   │   ├── database/
│   │   │   ├── schema.py
│   │   │   ├── migrations/
│   │   │   └── session.py
│   │   ├── cache/
│   │   │   └── redis_cache.py
│   │   └── external/
│   │       └── mitchell_api.py
│   │
│   └── utils/                        # Utilities
│       ├── logging.py
│       ├── validators.py
│       └── decorators.py
│
├── tests/                            # Test files
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
└── scripts/                          # Utility scripts
    ├── migrate_data.py
    ├── create_indexes.py
    └── seed_test_data.py
```

---

## 🔧 Refactoring Plan

### **Phase 1: Extract Services (Week 1)**

#### **Before (Tight Coupling):**
```tsx
// ❌ Component doing too much
export function RecommendationsTab({ data }: Props) {
  const [venueData, setVenueData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/aggregation/venue-shift-analysis')
      .then(res => res.json())
      .then(data => {
        // Complex transformation logic here
        const transformed = data.recommendations.map(r => ({
          ...r,
          improvement: r.potential_variance_reduction / r.current_avg_variance
        }));
        setVenueData(transformed);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return <div>{/* Render */}</div>;
}
```

#### **After (Separated Concerns):**

```tsx
// ✅ Feature: venue-analysis/api/getVenueShiftRecommendations.ts
import { apiClient } from '@/shared/api/apiClient';
import type { VenueShiftResponse } from '../models/venue.types';

export async function getVenueShiftRecommendations(
  months: number = 6
): Promise<VenueShiftResponse> {
  const { data } = await apiClient.get(
    '/api/v1/aggregation/venue-shift-analysis',
    { params: { months } }
  );
  return data;
}

// ✅ Feature: venue-analysis/services/venueService.ts
import { getVenueShiftRecommendations } from '../api/getVenueShiftRecommendations';
import type { VenueRecommendation, EnrichedVenueRecommendation } from '../models/venue.types';

export class VenueService {
  static calculateImprovement(rec: VenueRecommendation): number {
    if (rec.current_avg_variance === 0) return 0;
    return (rec.potential_variance_reduction / rec.current_avg_variance) * 100;
  }

  static async getEnrichedRecommendations(
    months: number
  ): Promise<EnrichedVenueRecommendation[]> {
    const response = await getVenueShiftRecommendations(months);

    return response.recommendations.map(rec => ({
      ...rec,
      improvementPct: this.calculateImprovement(rec),
      riskLevel: this.calculateRiskLevel(rec),
      priority: this.calculatePriority(rec)
    }));
  }

  private static calculateRiskLevel(rec: VenueRecommendation): 'low' | 'medium' | 'high' {
    if (rec.current_avg_variance > 20) return 'high';
    if (rec.current_avg_variance > 10) return 'medium';
    return 'low';
  }

  private static calculatePriority(rec: VenueRecommendation): number {
    // Business logic: higher variance + more claims = higher priority
    return rec.current_avg_variance * Math.log(rec.current_claim_count + 1);
  }
}

// ✅ Feature: venue-analysis/hooks/useVenueAnalysis.ts
import { useQuery } from '@tanstack/react-query';
import { VenueService } from '../services/venueService';

export function useVenueAnalysis(months: number = 6) {
  return useQuery({
    queryKey: ['venue-analysis', months],
    queryFn: () => VenueService.getEnrichedRecommendations(months),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
}

// ✅ Component: venue-analysis/components/VenueShiftCard.tsx
import { useVenueAnalysis } from '../hooks/useVenueAnalysis';

export function VenueShiftCard() {
  const { data, isLoading, error } = useVenueAnalysis(6);

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorAlert error={error} />;

  return (
    <Card>
      {data?.map(recommendation => (
        <VenueRecommendationItem key={recommendation.county} {...recommendation} />
      ))}
    </Card>
  );
}
```

**Benefits:**
- ✅ Single Responsibility Principle
- ✅ Easy to test each layer independently
- ✅ Reusable business logic
- ✅ Centralized API calls
- ✅ Type-safe data flow

---

### **Phase 2: Implement Repository Pattern (Week 2)**

#### **Backend Refactor:**

```python
# ✅ domain/repositories/base_repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from sqlalchemy.orm import Session

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository with common CRUD operations"""

    def __init__(self, session: Session, model: type[T]):
        self.session = session
        self.model = model

    def get_by_id(self, id: int) -> Optional[T]:
        return self.session.query(self.model).filter(
            self.model.id == id
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def create(self, entity: T) -> T:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def update(self, entity: T) -> T:
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def delete(self, id: int) -> bool:
        entity = self.get_by_id(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False


# ✅ domain/repositories/claim_repository.py
from typing import List, Dict, Any
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app.infrastructure.database.schema import Claim
from .base_repository import BaseRepository

class ClaimRepository(BaseRepository[Claim]):
    """Repository for Claim entity with specialized queries"""

    def __init__(self, session):
        super().__init__(session, Claim)

    def get_aggregated_by_county(
        self,
        cutoff_date: str,
        county: str,
        venue_rating: str,
        control_injury: Optional[str] = None,
        control_severity: Optional[str] = None,
        control_impact: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get isolated variance analysis for a county"""

        query = self.session.query(
            func.avg(func.abs(Claim.variance_pct)).label('avg_variance'),
            func.count(Claim.id).label('count')
        ).filter(
            Claim.claim_date >= cutoff_date,
            Claim.COUNTYNAME == county,
            Claim.VENUE_RATING == venue_rating
        )

        # Apply controls if provided
        if control_injury:
            query = query.filter(Claim.INJURY_GROUP_CODE == control_injury)
        if control_severity:
            query = query.filter(Claim.CAUTION_LEVEL == control_severity)
        if control_impact:
            query = query.filter(Claim.IMPACT == control_impact)

        result = query.first()

        return {
            'avg_variance': float(result[0]) if result[0] else 0,
            'claim_count': result[1] if result else 0
        }

    def get_most_common_factors(self, cutoff_date: str) -> Dict[str, Any]:
        """Get mode values for control variables"""

        injury = self.session.query(
            Claim.INJURY_GROUP_CODE,
            func.count(Claim.id).label('count')
        ).filter(
            Claim.claim_date >= cutoff_date,
            Claim.INJURY_GROUP_CODE.isnot(None)
        ).group_by(Claim.INJURY_GROUP_CODE
        ).order_by(func.count(Claim.id).desc()).first()

        severity = self.session.query(
            Claim.CAUTION_LEVEL,
            func.count(Claim.id).label('count')
        ).filter(
            Claim.claim_date >= cutoff_date,
            Claim.CAUTION_LEVEL.isnot(None)
        ).group_by(Claim.CAUTION_LEVEL
        ).order_by(func.count(Claim.id).desc()).first()

        impact = self.session.query(
            Claim.IMPACT,
            func.count(Claim.id).label('count')
        ).filter(
            Claim.claim_date >= cutoff_date,
            Claim.IMPACT.isnot(None)
        ).group_by(Claim.IMPACT
        ).order_by(func.count(Claim.id).desc()).first()

        return {
            'injury': injury[0] if injury else None,
            'severity': severity[0] if severity else None,
            'impact': impact[0] if impact else None
        }


# ✅ domain/services/venue_service.py
from typing import List
from datetime import datetime, timedelta
from app.domain.repositories.claim_repository import ClaimRepository
from app.domain.models.venue import VenueRecommendation

class VenueAnalysisService:
    """Business logic for venue shift analysis"""

    def __init__(self, claim_repo: ClaimRepository):
        self.claim_repo = claim_repo

    def analyze_venue_shifts(
        self,
        months: int = 6
    ) -> List[VenueRecommendation]:
        """
        Perform isolated venue shift analysis
        Returns recommendations for venue rating changes
        """
        cutoff_date = (datetime.now() - timedelta(days=months * 30)).strftime('%Y-%m-%d')

        # Get control variables (database-level)
        controls = self.claim_repo.get_most_common_factors(cutoff_date)

        # Get unique counties
        counties = self.claim_repo.get_distinct_counties(cutoff_date)

        recommendations = []

        for county, state in counties:
            # Analyze this county with isolation
            rec = self._analyze_county(
                county,
                state,
                cutoff_date,
                controls
            )
            if rec:
                recommendations.append(rec)

        return sorted(
            recommendations,
            key=lambda x: x.potential_variance_reduction,
            reverse=True
        )

    def _analyze_county(
        self,
        county: str,
        state: str,
        cutoff_date: str,
        controls: Dict[str, Any]
    ) -> Optional[VenueRecommendation]:
        """Analyze a single county (isolated)"""

        # Get current venue rating
        current_venue = self.claim_repo.get_mode_venue_for_county(
            county,
            cutoff_date
        )

        if not current_venue:
            return None

        # Get current performance with controls
        current_perf = self.claim_repo.get_aggregated_by_county(
            cutoff_date,
            county,
            current_venue,
            control_injury=controls['injury'],
            control_severity=controls['severity'],
            control_impact=controls['impact']
        )

        # Check alternatives
        alternatives = self._check_alternative_venues(
            cutoff_date,
            current_venue,
            controls
        )

        # Determine recommendation
        recommendation = self._determine_recommendation(
            current_perf,
            alternatives
        )

        return VenueRecommendation(
            county=county,
            state=state,
            current_venue_rating=current_venue,
            current_avg_variance=current_perf['avg_variance'],
            current_claim_count=current_perf['claim_count'],
            recommended_venue_rating=recommendation['venue'] if recommendation else None,
            potential_variance_reduction=recommendation['improvement'] if recommendation else 0,
            confidence=self._calculate_confidence(current_perf, recommendation),
            isolation_quality=self._calculate_isolation_quality(current_perf)
        )


# ✅ api/routes/venue.py (Thin controller)
from fastapi import APIRouter, Depends
from app.api.dependencies import get_claim_repository
from app.domain.services.venue_service import VenueAnalysisService

router = APIRouter(prefix="/venue", tags=["venue"])

@router.get("/shift-analysis")
async def get_venue_shift_analysis(
    months: int = 6,
    claim_repo: ClaimRepository = Depends(get_claim_repository)
):
    """
    Get venue shift recommendations
    Endpoint is thin - all logic in service layer
    """
    service = VenueAnalysisService(claim_repo)
    recommendations = service.analyze_venue_shifts(months)

    return {
        "recommendations": [rec.dict() for rec in recommendations],
        "summary": {
            "total": len(recommendations),
            "with_recommendations": len([r for r in recommendations if r.recommended_venue_rating])
        }
    }
```

**Benefits:**
- ✅ Testable business logic (mock repositories)
- ✅ Thin controllers (just routing)
- ✅ Database abstraction (easy to swap SQLite → PostgreSQL)
- ✅ Reusable queries

---

### **Phase 3: Add Error Handling (Week 3)**

```typescript
// ✅ shared/api/errors.ts
export class ApiError extends Error {
  constructor(
    public message: string,
    public status: number,
    public code: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class ValidationError extends ApiError {
  constructor(message: string, details?: any) {
    super(message, 400, 'VALIDATION_ERROR', details);
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends ApiError {
  constructor(resource: string) {
    super(`${resource} not found`, 404, 'NOT_FOUND');
    this.name = 'NotFoundError';
  }
}

export class ServerError extends ApiError {
  constructor(message: string) {
    super(message, 500, 'SERVER_ERROR');
    this.name = 'ServerError';
  }
}

// ✅ shared/api/apiClient.ts
import axios from 'axios';
import { ApiError, ValidationError, NotFoundError, ServerError } from './errors';

export const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
});

// Request interceptor (add auth tokens)
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (handle errors)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 400:
          throw new ValidationError(data.detail || 'Validation failed', data);
        case 404:
          throw new NotFoundError(data.detail || 'Resource');
        case 500:
          throw new ServerError(data.detail || 'Server error');
        default:
          throw new ApiError(
            data.detail || 'Unknown error',
            status,
            'API_ERROR',
            data
          );
      }
    }

    // Network error
    if (error.request) {
      throw new ApiError(
        'Network error - please check your connection',
        0,
        'NETWORK_ERROR'
      );
    }

    throw error;
  }
);

// ✅ shared/components/ErrorBoundary.tsx
import React from 'react';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error tracking service (Sentry, etc.)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-8">
          <Alert variant="destructive">
            <AlertTitle>Something went wrong</AlertTitle>
            <AlertDescription>
              {this.state.error?.message}
              <div className="mt-4">
                <Button onClick={() => window.location.reload()}>
                  Reload Page
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        </div>
      );
    }

    return this.props.children;
  }
}
```

---

## ✅ Code Quality Checklist

### **Modularity:**
- [ ] Each file has single responsibility
- [ ] Functions < 50 lines
- [ ] Classes < 300 lines
- [ ] No circular dependencies

### **Maintainability:**
- [ ] Consistent naming conventions
- [ ] Self-documenting code
- [ ] Comments only for complex logic
- [ ] No magic numbers/strings

### **Testability:**
- [ ] Pure functions where possible
- [ ] Dependency injection
- [ ] Mocked external dependencies
- [ ] 80%+ test coverage

### **Performance:**
- [ ] Database queries optimized
- [ ] N+1 query problems eliminated
- [ ] Caching strategy implemented
- [ ] Lazy loading for heavy components

---

**Next:** Code Reviewer will perform final review
