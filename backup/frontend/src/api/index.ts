export * from './client';
export * from './claimsAPI';
export * from './recalibrationAPI';

import { claimsAPI } from './claimsAPI';
import { recalibrationAPI } from './recalibrationAPI';

export const API = {
  claims: claimsAPI,
  recalibration: recalibrationAPI,
};

export default API;
