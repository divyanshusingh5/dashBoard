// Utility to extend CSV data with new clinical factors
// This generates weighted random values based on real-world distributions

const valueDistributions = {
  Advanced_Pain_Treatment: { 'No': 26930, 'Yes': 1011 },
  Causation_Compliance: { 'Compliant': 1338076, 'Non-Compliant': 41882 },
  Clinical_Findings: { 'No': 497354, 'Yes': 461477, 'Mild': 414, 'Moderate': 258 },
  Cognitive_Symptoms: { 'Yes - Alleged': 26079, 'Yes - Diagnosed': 13837 },
  Complete_Disability_Duration: {
    'Less than 1 week': 4861, 'Less than 2 Weeks': 3740, '1 -3 weeks': 3330,
    '2-4 Weeks': 2975, 'More than 8 Weeks': 2755, '2-6 Weeks': 2367
  },
  Concussion_Diagnosis: { 'Yes': 617, 'No': 389 },
  Consciousness_Impact: {
    'Temp Unconsciousness-Subjective': 13502,
    'Temp Unconsciousness-Objective': 4369,
    'Altered': 3507
  },
  Consistent_Mechanism: { 'Consistent': 1242983, 'Questionable': 146313, 'Highly Unlikely': 31060 },
  Dental_Procedure: { 'No': 2510, 'Yes': 574 },
  Dental_Treatment: { 'Repair': 1355, 'Replace': 995 },
  Dental_Visibility: { 'Yes': 2360, 'No': 724 },
  Emergency_Treatment: {
    'Yes - Treated & Released': 78571, 'Yes - Treated & Admitted': 5027,
    'Yes - treated & released': 636, 'Yes - treated & admitted': 200
  },
  Fixation_Method: {
    'Open': 4789, 'ORIF w/o Hdw Removal': 4211, 'Open/Internal': 3651,
    'Brace': 3231, 'Sling/Brace': 2270, 'Immobilization': 2139
  },
  Head_Trauma: { 'No': 80342, 'Yes': 38824 },
  Immobilization_Used: { 'No': 282243, 'Yes': 25403, 'Brace/Sling': 8461, 'Cast': 322, 'Brace/Boot': 243 },
  Injury_Count: {
    'Multi Level': 47305, 'Single Level': 21831, 'Single': 21769,
    'Multiple': 15533, 'Two levels': 10419, 'Three or more levels': 10075
  },
  Injury_Extent: { 'Mild': 104894, 'Moderate': 80346, 'Severe': 21062 },
  Injury_Laterality: { 'Yes': 144207, 'No': 118398, 'Unilateral': 9295, 'Bilateral': 2942 },
  Injury_Location: {
    'Cervical/Thoracic/Lumbar': 252457, 'Cervical/Lumbar': 60615, 'Cervical': 53882,
    'Cervical/Thoracic': 46865, 'Lumbar': 31871, 'Thoracic/Lumbar': 30051, 'Thoracic': 20897
  },
  Injury_Type: {
    'Contusion Only': 86711, 'Herniation': 79257, 'Non-Displaced': 29599,
    'Abrasion Only': 23649, 'Bruise/Hematoma w/Abrasion': 19382,
    'Herniation/Protrusion/Extrusion': 17626, 'Bruise/Hematoma Only': 17219
  },
  Mobility_Assistance: {
    'Crutches/Cane/Walker': 8339, 'Scooter/Wheelchair': 829,
    'Crutches/Cane/Walker/Scooter': 639, 'Wheelchair': 52
  },
  Movement_Restriction: {
    'Partial Restriction': 535617, 'No Restriction': 330541,
    'Full Restriction': 15682, 'Partial ROM Restriction': 10490
  },
  Nerve_Involvement: { 'Yes': 111854, 'No': 56658 },
  Pain_Management: {
    'RX': 439812, 'OTC': 210252, 'Rx': 176987, 'Single Injection': 36986,
    'Multiple Injections': 31240, 'Single Epidural': 14986
  },
  Partial_Disability_Duration: {
    'Less than 1 Week': 9622, '1 - 3 weeks': 5389, 'More than 4 weeks': 4064,
    'Less than 2 Weeks': 3755, '2-4 Weeks': 3694, 'More than 8 Weeks': 2953
  },
  Physical_Symptoms: { 'No': 107239, 'Yes': 69585, 'Yes - Alleged': 64104, 'Yes - Treated': 48200 },
  Physical_Therapy: { 'Yes - Outpatient': 16807, 'Yes': 12456, 'No': 11027, 'Yes - Inpatient': 5364 },
  Prior_Treatment: {
    'No': 720909, 'No/Non-Factor': 164453, 'Yes - Tx More than 1 Yr': 73427,
    'No/Resolved': 48447, 'Yes - No Tx': 35031
  },
  Recovery_Duration: {
    'Less than 2 weeks': 67422, '2 - 4 weeks': 50768, '5 - 12 weeks': 18851,
    '2-4 weeks': 10807, 'More than 4 weeks': 7715
  },
  Repair_Type: { 'Implant': 834, 'Bridge': 361, 'Crown': 56, 'Filling/Bonding': 1 },
  Respiratory_Issues: { 'No': 8849, 'Yes': 3399 },
  Soft_Tissue_Damage: {
    'Partial Tear w/o Cart Damage': 27324, 'Partial Tear w/ Cart Damage': 7298,
    'Full Tear w/o Cart Damage': 7249, 'Full Tear w/ Cart Damage': 3836, 'Cartilage only': 3098
  },
  Special_Treatment: { 'No': 1791, 'Series': 327, 'Single': 191, 'Yes': 143, 'Partial': 28 },
  Surgical_Intervention: {
    'No': 16220, 'Yes - Arthroscopic': 15007, 'Recommended Not Performed': 9474,
    'Yes': 2595, 'Fusion': 2437, 'Yes - Open': 1723
  },
  Symptom_Timeline: {
    'Immediate/ER': 453447, 'First 48 Hours': 156232, '3 - 7 Days': 91201,
    'More Than 7 Days': 85721, 'Immediate/Within 24 Hours': 63926
  },
  Treatment_Compliance: { '': 1 }, // Empty, will use empty string
  Treatment_Course: { 'Active': 503949, 'Passive': 380651, 'Eval Only': 109996, 'None/Ice/Rest': 53354 },
  Treatment_Delays: {
    'None/Explained': 1094677, 'Delay Only': 163681, 'Gaps Only': 93899, 'Delay and Gaps': 68099
  },
  Treatment_Level: {
    'Non-Invasive': 99863, 'Yes': 92629, 'No': 21673, 'Clean & Dress': 15622, 'Stitches/Staples': 8563
  },
  Treatment_Period_Considered: {
    'Less than 6 weeks': 270844, '7 - 12 weeks': 219172, '3 - 6 months': 210671,
    'More than 6 months': 106250, 'Less than 6 months': 104155
  },
  Vehicle_Impact: { 'Moderate': 509269, 'Heavy': 343651, 'Minimal': 276613 }
};

// Weighted random selection
function weightedRandom(distribution: Record<string, number>): string {
  const entries = Object.entries(distribution);
  const totalWeight = entries.reduce((sum, [_, weight]) => sum + weight, 0);
  let random = Math.random() * totalWeight;
  
  for (const [value, weight] of entries) {
    random -= weight;
    if (random <= 0) return value;
  }
  
  return entries[0][0]; // fallback
}

export function generateExtendedRow(existingRow: any): any {
  const extended = { ...existingRow };
  
  // Add all new columns with weighted random values
  for (const [column, distribution] of Object.entries(valueDistributions)) {
    extended[column] = weightedRandom(distribution);
  }
  
  return extended;
}

// Helper to convert object to CSV row
export function objectToCSV(obj: Record<string, any>): string {
  return Object.values(obj)
    .map(val => {
      const str = String(val ?? '');
      // Escape commas and quotes
      if (str.includes(',') || str.includes('"') || str.includes('\n')) {
        return `"${str.replace(/"/g, '""')}"`;
      }
      return str;
    })
    .join(',');
}

// Main function to extend CSV
export async function extendCSV(csvText: string): Promise<string> {
  const lines = csvText.trim().split('\n');
  const header = lines[0];
  
  // Add new column names to header
  const newColumns = Object.keys(valueDistributions);
  const extendedHeader = header + ',' + newColumns.join(',');
  
  // Process data rows
  const extendedRows: string[] = [extendedHeader];
  
  for (let i = 1; i < lines.length; i++) {
    const row = lines[i];
    if (!row.trim()) continue;
    
    // Parse CSV row (basic parser)
    const values = row.split(',');
    const headerCols = header.split(',');
    
    const rowObj: Record<string, string> = {};
    headerCols.forEach((col, idx) => {
      rowObj[col] = values[idx] || '';
    });
    
    // Generate extended row
    const extendedRow = generateExtendedRow(rowObj);
    
    // Convert back to CSV
    const csvRow = objectToCSV(extendedRow);
    extendedRows.push(csvRow);
  }
  
  return extendedRows.join('\n');
}
