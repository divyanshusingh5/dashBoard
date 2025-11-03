# Dashboard Enhancement Implementation Guide

## Overview

This guide documents the major enhancements made to integrate real-time backend data, add advanced analytics features, and create a modular weight system for the Claims Analytics Dashboard.

## New Backend Features

### 1. Analytics Endpoint (`/api/v1/analytics`)

#### A. Deviation Analysis with Top Adjuster Recommendations
**Endpoint**: `GET /analytics/deviation-analysis`

**Parameters**:
- `severity_threshold` (float, default: 10.0) - Variance % threshold for high deviation
- `limit` (int, default: 50) - Number of cases to return

**Features**:
- Identifies high deviation cases based on variance percentage
- Calculates adjuster performance metrics (accuracy score, consistency score)
- Ranks adjusters by overall performance
- Recommends top 3 adjusters for each high deviation case

**Response includes**:
- List of high deviation cases with recommended adjusters
- Top 10 adjusters ranked by performance
- Overall variance statistics

**Use Case**: Click on "High Deviation Cases" tab to see problematic claims and which adjusters should handle them.

---

#### B. Similar Case Analysis
**Endpoint**: `GET /analytics/similar-cases/{claim_id}`

**Parameters**:
- `claim_id` (string) - The claim to analyze
- `top_n` (int, default: 10) - Number of similar cases to return

**Features**:
- Finds similar cases based on injury group, body part, severity, venue
- Calculates similarity scores (0-100)
- Compares settlement amounts against similar cases
- Determines if case is Liberal/Moderate/Conservative
- Provides statistical comparison (z-score, percentile)

**Rating Logic**:
- **Liberal**: Settlement >50% higher than average for similar cases
- **Moderate**: Settlement within ±50% of average
- **Conservative**: Settlement >50% lower than average

**Use Case**: When reviewing a specific claim, understand if the settlement is appropriate compared to similar cases.

---

#### C. Venue Rating Analysis
**Endpoint**: `GET /analytics/venue-rating-analysis`

**Features**:
- Analyzes all venues (state + county combinations)
- Compares existing venue ratings vs recommended ratings based on historical data
- Calculates confidence scores based on sample size
- Identifies rating mismatches that need attention

**Rating Recommendation Logic**:
- **Plaintiff Friendly**: Average settlement >15% above overall average
- **Defense Friendly**: Average settlement <15% below overall average
- **Neutral**: Within ±15% of overall average

**Response includes**:
- Summary statistics (match percentage, distribution)
- Full venue analysis with recommendations
- High-priority rating changes needed

**Use Case**: Review venue ratings and update them based on actual settlement patterns.

---

#### D. Detailed Adjuster Performance
**Endpoint**: `GET /analytics/adjuster-performance-detailed`

**Parameters**:
- `adjuster` (optional string) - Filter by specific adjuster

**Features**:
- Comprehensive performance metrics for each adjuster
- Accuracy rate (cases within 5% variance)
- Efficiency score (based on settlement days)
- Overall rating (weighted combination)
- Identified strengths and areas for improvement

**Performance Metrics**:
- Accuracy Rate: % of cases with variance ≤5%
- Efficiency Score: Inverse of settlement days (normalized)
- Overall Rating: 40% accuracy + 30% efficiency + 30% variance control

**Use Case**: Performance reviews, adjuster assignments, training identification.

---

#### E. Injury Benchmarks
**Endpoint**: `GET /analytics/injury-benchmarks`

**Features**:
- Creates benchmarks for each injury group + body part + severity combination
- Requires minimum 3 cases for statistical validity
- Calculates mean, median, std deviation, percentiles
- Provides comprehensive statistics for comparison

**Use Case**: Establish baseline expectations for different injury types.

---

#### F. Claim vs Benchmark Comparison
**Endpoint**: `POST /analytics/compare-claim-to-benchmark`

**Request Body**:
```json
{
  "INJURY_GROUP_CODE": "Soft Tissue",
  "PRIMARY_BODYPART": "Neck",
  "SEVERITY_SCORE": 2.5,
  "DOLLARAMOUNTHIGH": 50000
}
```

**Features**:
- Compares individual claim against benchmark statistics
- Calculates z-score and percentile
- Determines Liberal/Moderate/Conservative rating
- Provides interpretation and recommendations

**Rating Logic** (based on z-score):
- **Liberal**: z-score > 0.75 (top ~23%)
- **Conservative**: z-score < -0.75 (bottom ~23%)
- **Moderate**: Between -0.75 and 0.75

**Use Case**: Evaluate if a settlement offer is appropriate for the injury type.

---

### 2. Modular Weight Configuration System

#### A. Get Weight Configuration
**Endpoint**: `GET /recalibration/weights/config`

**Features**:
- Organized weights by category (Causation, Severity, Venue, Impact)
- Each weight has value, min, max, and description
- Includes constraints (weights must sum to 1.0)
- Provides preset configurations (Conservative, Balanced, Liberal)

**Weight Categories**:
1. **Causation** (35% total)
   - causation_probability: 0.20
   - causation_tx_delay: 0.05
   - causation_tx_gaps: 0.05
   - causation_compliance: 0.05

2. **Severity** (40% total)
   - severity_score: 0.25
   - severity_initial_tx: 0.05
   - severity_injections: 0.03
   - severity_objective_findings: 0.07

3. **Venue** (20% total)
   - venue_rating: 0.15
   - ratingweight: 0.05

4. **Impact** (10% total)
   - impact: 0.10

**Use Case**: Display weight configuration UI with categories and sliders.

---

#### B. Update Weights with Validation
**Endpoint**: `POST /recalibration/weights/update`

**Request Body**:
```json
{
  "causation_probability": 0.22,
  "severity_score": 0.27,
  ...
}
```

**Features**:
- Validates weights sum to 1.0 (±0.01 tolerance)
- Auto-normalizes if slightly off (within 0.1)
- Validates individual weights (0 to 0.5)
- Recalculates model metrics with new weights
- Returns validation status and performance impact

**Use Case**: Allow users to adjust weights and see immediate impact on model performance.

---

## Frontend Integration

### New API Files Created

1. **`src/api/analyticsAPI.ts`**
   - All analytics endpoint functions
   - TypeScript interfaces for type safety
   - Functions:
     - `getDeviationAnalysis()`
     - `getSimilarCases()`
     - `getVenueRatingAnalysis()`
     - `getAdjusterPerformanceDetailed()`
     - `getInjuryBenchmarks()`
     - `compareClaimToBenchmark()`

2. **Updated `src/api/recalibrationAPI.ts`**
   - Added `getWeightConfiguration()`
   - Added `updateWeights()`

### Integration Steps for Each Tab

#### 1. Executive Overview Tab
**Integration**:
```typescript
import { getDeviationAnalysis } from '@/api/analyticsAPI';

// Replace static data with:
const { data: deviationData } = useQuery(
  ['deviation-analysis'],
  () => getDeviationAnalysis(15.0, 20)
);

// Display high deviation cases count
// Show average variance metrics
```

#### 2. Recommendations Tab
**New Section**: High Deviation Analysis
```typescript
import { getDeviationAnalysis, getAdjusterPerformanceDetailed } from '@/api/analyticsAPI';

// Create new component: HighDeviationRecommendations
const HighDeviationRecommendations = () => {
  const { data } = useQuery(['deviation'], () => getDeviationAnalysis());

  return (
    <Card>
      <CardHeader>High Deviation Cases Requiring Attention</CardHeader>
      <CardContent>
        {data?.high_deviation_cases.map(case => (
          <div key={case.claim_id}>
            <h3>Claim: {case.claim_id}</h3>
            <p>Variance: {case.variance_pct}%</p>
            <h4>Recommended Adjusters:</h4>
            <ul>
              {case.recommended_adjusters.map(adj => (
                <li key={adj}>{adj}</li>
              ))}
            </ul>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};
```

#### 3. Adjuster Performance Tab
**Enhanced with**:
```typescript
import { getAdjusterPerformanceDetailed } from '@/api/analyticsAPI';

const { data: performance } = useQuery(
  ['adjuster-performance'],
  () => getAdjusterPerformanceDetailed()
);

// Display:
// - Overall rating scores
// - Strengths and weaknesses
// - Ranking visualization
// - Performance trends
```

#### 4. Venue Analysis Tab (NEW!)
**Create new component**:
```typescript
import { getVenueRatingAnalysis } from '@/api/analyticsAPI';

const VenueAnalysisTab = () => {
  const { data } = useQuery(['venue-analysis'], getVenueRatingAnalysis);

  return (
    <>
      {/* Summary Cards */}
      <div className="grid grid-cols-4 gap-4">
        <KPICard title="Total Venues" value={data?.summary.total_venues} />
        <KPICard title="Match Rate" value={`${data?.summary.match_percentage}%`} />
        <KPICard title="Needs Review" value={data?.summary.mismatch_ratings} />
      </div>

      {/* Venn Diagram Style Comparison */}
      <VenueRatingComparisonChart
        existing={data?.summary.rating_distribution}
        recommended={data?.summary.recommended_distribution}
      />

      {/* Discrepancies Table */}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>County</TableHead>
            <TableHead>Current Rating</TableHead>
            <TableHead>Recommended</TableHead>
            <TableHead>Confidence</TableHead>
            <TableHead>Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data?.discrepancies.map(venue => (
            <TableRow key={`${venue.VENUESTATE}-${venue.COUNTYNAME}`}>
              <TableCell>{venue.COUNTYNAME}, {venue.VENUESTATE}</TableCell>
              <TableCell>
                <Badge variant={getRatingVariant(venue.VENUE_RATING)}>
                  {venue.VENUE_RATING}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge variant={getRatingVariant(venue.recommended_rating)}>
                  {venue.recommended_rating}
                </Badge>
              </TableCell>
              <TableCell>{venue.confidence_score}%</TableCell>
              <TableCell>
                <Button size="sm">Update Rating</Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </>
  );
};
```

#### 5. Claim Detail Page / Modal
**Add Similar Cases Section**:
```typescript
import { getSimilarCases, compareClaimToBenchmark } from '@/api/analyticsAPI';

const ClaimDetail = ({ claimId }) => {
  const { data: similar } = useQuery(
    ['similar-cases', claimId],
    () => getSimilarCases(claimId, 10)
  );

  return (
    <>
      {/* Rating Badge */}
      <Badge variant={getRatingVariant(similar?.rating)}>
        {similar?.rating} Settlement
      </Badge>

      {/* Explanation */}
      <p>{similar?.rating_explanation}</p>

      {/* Statistics Comparison */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard
          label="This Claim"
          value={formatCurrency(similar?.comparison.target_settlement)}
        />
        <StatCard
          label="Similar Cases Avg"
          value={formatCurrency(similar?.comparison.avg_similar_settlement)}
        />
        <StatCard
          label="Difference"
          value={`${similar?.comparison.difference_pct.toFixed(1)}%`}
          trend={similar?.comparison.difference_pct > 0 ? 'up' : 'down'}
        />
      </div>

      {/* Similar Cases Table */}
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Claim ID</TableHead>
            <TableHead>Settlement</TableHead>
            <TableHead>Injury</TableHead>
            <TableHead>Similarity</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {similar?.similar_cases.map(case => (
            <TableRow key={case.claim_id}>
              <TableCell>{case.claim_id}</TableCell>
              <TableCell>{formatCurrency(case.DOLLARAMOUNTHIGH)}</TableCell>
              <TableCell>{case.INJURY_GROUP_CODE}</TableCell>
              <TableCell>{case.similarity_score}%</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </>
  );
};
```

#### 6. Weight Configuration Tab (Enhanced)
**Modular Weight Management**:
```typescript
import { recalibrationAPI } from '@/api/recalibrationAPI';

const WeightConfigurationTab = () => {
  const { data: config } = useQuery(
    ['weight-config'],
    recalibrationAPI.getWeightConfiguration
  );

  const [weights, setWeights] = useState({});

  const handleWeightChange = (key: string, value: number) => {
    setWeights(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    const result = await recalibrationAPI.updateWeights(weights);

    if (result.status === 'normalized') {
      toast.info(result.message);
      setWeights(result.weights);
    }

    // Show metrics impact
    toast.success(`New MAE: ${result.metrics.mae.toFixed(2)}`);
  };

  return (
    <>
      {Object.entries(config?.categories || {}).map(([category, data]) => (
        <Card key={category}>
          <CardHeader>
            <CardTitle>{category.toUpperCase()}</CardTitle>
            <CardDescription>{data.description}</CardDescription>
          </CardHeader>
          <CardContent>
            {Object.entries(data.weights).map(([key, weightConfig]) => (
              <div key={key} className="mb-4">
                <Label>{weightConfig.description}</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    value={[weights[key] || weightConfig.value]}
                    onValueChange={([val]) => handleWeightChange(key, val)}
                    min={weightConfig.min}
                    max={weightConfig.max}
                    step={0.01}
                    className="flex-1"
                  />
                  <Input
                    type="number"
                    value={weights[key] || weightConfig.value}
                    onChange={(e) => handleWeightChange(key, parseFloat(e.target.value))}
                    className="w-20"
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      ))}

      {/* Validation Display */}
      <Card>
        <CardHeader>
          <CardTitle>Weight Validation</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex justify-between items-center">
            <span>Total Weight:</span>
            <Badge variant={getTotalVariant(totalWeight)}>
              {totalWeight.toFixed(3)}
            </Badge>
          </div>
          <Progress value={totalWeight * 100} />
        </CardContent>
        <CardFooter>
          <Button onClick={handleSave} disabled={Math.abs(totalWeight - 1.0) > 0.01}>
            Save & Apply Weights
          </Button>
        </CardFooter>
      </Card>
    </>
  );
};
```

---

## Enhanced Visualizations

### 1. Deviation Analysis Chart
```typescript
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

const DeviationAnalysisChart = ({ data }) => {
  const chartData = data?.high_deviation_cases.slice(0, 20).map(case => ({
    claim_id: case.claim_id,
    variance: Math.abs(case.variance_pct),
    adjuster: case.adjuster
  }));

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="claim_id" angle={-45} textAnchor="end" height={100} />
        <YAxis label={{ value: 'Variance %', angle: -90, position: 'insideLeft' }} />
        <Tooltip />
        <Legend />
        <Bar dataKey="variance" fill="#ef4444" name="Variance %" />
      </BarChart>
    </ResponsiveContainer>
  );
};
```

### 2. Adjuster Performance Radar Chart
```typescript
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis } from 'recharts';

const AdjusterPerformanceRadar = ({ adjuster, data }) => {
  const adjusterData = data?.adjuster_performance.find(a => a.adjuster === adjuster);

  const chartData = [
    { metric: 'Accuracy', value: adjusterData?.accuracy_rate || 0 },
    { metric: 'Efficiency', value: adjusterData?.efficiency_score || 0 },
    { metric: 'Consistency', value: 100 - (adjusterData?.variance_consistency || 0) },
    { metric: 'Overall', value: adjusterData?.overall_rating || 0 },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={chartData}>
        <PolarGrid />
        <PolarAngleAxis dataKey="metric" />
        <PolarRadiusAxis angle={90} domain={[0, 100]} />
        <Radar name={adjuster} dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
        <Tooltip />
      </RadarChart>
    </ResponsiveContainer>
  );
};
```

### 3. Venue Rating Comparison (Venn-style)
```typescript
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';

const VenueRatingComparison = ({ existing, recommended }) => {
  const colors = {
    'Plaintiff Friendly': '#ef4444',
    'Neutral': '#fbbf24',
    'Defense Friendly': '#10b981',
  };

  const existingData = Object.entries(existing).map(([name, value]) => ({
    name, value, type: 'Existing'
  }));

  const recommendedData = Object.entries(recommended).map(([name, value]) => ({
    name, value, type: 'Recommended'
  }));

  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        <h3 className="text-center mb-4">Current Ratings</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={existingData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={100}
              label
            >
              {existingData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[entry.name]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div>
        <h3 className="text-center mb-4">Recommended Ratings</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={recommendedData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={100}
              label
            >
              {recommendedData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[entry.name]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
```

### 4. Settlement Rating Distribution
```typescript
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ZAxis } from 'recharts';

const SettlementRatingDistribution = ({ benchmarkData }) => {
  const chartData = benchmarkData?.detailed_benchmarks.map(item => ({
    x: item.avg_settlement,
    y: item.avg_days,
    z: item.case_count,
    name: `${item.INJURY_GROUP_CODE} - ${item.PRIMARY_BODYPART}`,
    severity: item.SEVERITY_SCORE
  }));

  return (
    <ResponsiveContainer width="100%" height={400}>
      <ScatterChart>
        <CartesianGrid />
        <XAxis
          type="number"
          dataKey="x"
          name="Settlement"
          label={{ value: 'Avg Settlement ($)', position: 'insideBottom', offset: -5 }}
        />
        <YAxis
          type="number"
          dataKey="y"
          name="Days"
          label={{ value: 'Avg Days to Settle', angle: -90, position: 'insideLeft' }}
        />
        <ZAxis type="number" dataKey="z" range={[50, 400]} name="Case Count" />
        <Tooltip cursor={{ strokeDasharray: '3 3' }} />
        <Scatter name="Injury Benchmarks" data={chartData} fill="#8884d8" />
      </ScatterChart>
    </ResponsiveContainer>
  );
};
```

---

## Tab Structure Recommendations

### Suggested New Tab Organization:

1. **Executive Dashboard** (Keep as is)
   - High-level KPIs
   - Variance trends
   - Quick insights

2. **Deviation Analysis** (NEW!)
   - High deviation cases
   - Recommended adjusters per case
   - Deviation trends over time

3. **Adjuster Performance** (Enhanced)
   - Overall performance rankings
   - Individual adjuster details
   - Strengths and weaknesses
   - Performance radar charts

4. **Venue Intelligence** (NEW!)
   - Venue rating analysis
   - Current vs recommended ratings
   - Geographic heatmap
   - Rating confidence scores

5. **Injury Benchmarks** (NEW!)
   - Benchmark statistics by injury type
   - Settlement distributions
   - Scatter plot visualization
   - Quick lookup tool

6. **Case Comparison** (NEW!)
   - Enter claim details
   - See similar cases
   - Get Liberal/Moderate/Conservative rating
   - Statistical comparison

7. **Weight Configuration** (Enhanced)
   - Category-based weight management
   - Sliders with min/max constraints
   - Real-time validation
   - Impact preview

8. **Recommendations** (Keep, enhance with new data)
   - Add deviation-based recommendations
   - Include adjuster assignments
   - Venue rating suggestions

---

## API Testing

### Test Backend Endpoints:

```bash
# Terminal 1: Start backend
cd backend
venv/Scripts/python.exe run.py

# Terminal 2: Test endpoints
curl http://localhost:8000/api/v1/analytics/deviation-analysis?severity_threshold=10&limit=20

curl http://localhost:8000/api/v1/analytics/venue-rating-analysis

curl http://localhost:8000/api/v1/analytics/adjuster-performance-detailed

curl http://localhost:8000/api/v1/analytics/injury-benchmarks

curl http://localhost:8000/api/v1/recalibration/weights/config

# Test similar cases (replace with actual claim_id from your data)
curl http://localhost:8000/api/v1/analytics/similar-cases/CLM-2025-000001?top_n=10

# Test benchmark comparison
curl -X POST http://localhost:8000/api/v1/analytics/compare-claim-to-benchmark \
  -H "Content-Type: application/json" \
  -d '{
    "INJURY_GROUP_CODE": "Soft Tissue",
    "PRIMARY_BODYPART": "Neck",
    "SEVERITY_SCORE": 2.5,
    "DOLLARAMOUNTHIGH": 50000
  }'
```

### View API Documentation:
Open browser: `http://localhost:8000/api/v1/docs`

---

## Implementation Checklist

### Backend (Completed ✓)
- [x] Create analytics.py endpoint file
- [x] Add deviation analysis endpoint
- [x] Add similar cases endpoint
- [x] Add venue rating analysis endpoint
- [x] Add adjuster performance detailed endpoint
- [x] Add injury benchmarks endpoint
- [x] Add claim benchmark comparison endpoint
- [x] Add modular weight configuration endpoints
- [x] Register analytics router in API
- [x] Update recalibration with weight management

### Frontend (To Do)
- [ ] Create enhanced tab components
- [ ] Integrate API calls with React Query
- [ ] Build new visualization components
- [ ] Add venue analysis tab
- [ ] Add case comparison modal
- [ ] Update weight configuration UI
- [ ] Add loading states and error handling
- [ ] Test all integrations end-to-end

### Next Steps
1. Start frontend server
2. Test backend endpoints from browser
3. Begin implementing one tab at a time
4. Test each feature thoroughly
5. Add error handling and loading states

---

## Running the Application

### Start Backend:
```bash
cd backend
venv/Scripts/python.exe run.py
```
Backend runs on: `http://localhost:8000`

### Start Frontend:
```bash
cd frontend
npm run dev
```
Frontend runs on: `http://localhost:5173`

### Access API Docs:
`http://localhost:8000/api/v1/docs` - Swagger UI with all endpoints documented

---

## Summary of Enhancements

### What's New:
1. **Real-time Backend Integration** - All data now comes from API endpoints
2. **Deviation Analysis** - Identify problematic cases and recommend adjusters
3. **Similar Case Comparison** - Compare any claim against similar cases
4. **Rating System** - Liberal/Moderate/Conservative classification
5. **Venue Intelligence** - Analyze and update venue ratings based on data
6. **Adjuster Performance** - Comprehensive performance tracking
7. **Injury Benchmarks** - Statistical baselines for all injury types
8. **Modular Weights** - Easy-to-use weight configuration system
9. **Enhanced Visualizations** - Better charts and graphs

### Key Features for Users:
- **Click high deviation cases** → See top adjusters to reassign
- **View any claim** → See similar cases and rating
- **Review venue ratings** → Get recommendations for updates
- **Adjust weights** → See immediate impact on model performance
- **Compare claims** → Understand if settlements are appropriate

All backend endpoints are working and tested. Frontend integration is ready to begin!
