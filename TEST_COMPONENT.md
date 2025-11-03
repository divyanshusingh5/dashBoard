# Testing Factor Weight Impact Analyzer

## Step-by-Step Troubleshooting

### 1. Check if Frontend is Running
Open terminal and run:
```bash
cd d:\Repositories\dashBoard\frontend
npm run dev
```

You should see output like:
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 2. Check Browser Console
1. Open the app in browser: http://localhost:5173 (or whatever port shown)
2. Press F12 to open DevTools
3. Go to Console tab
4. Look for errors (red text)

**Common errors and fixes:**

**Error: "Cannot find module"**
- Solution: Run `npm install` in frontend directory

**Error: "WEIGHT_FACTORS is not exported"**
- This means recalibrationEngine.ts doesn't export WEIGHT_FACTORS
- I can fix this

**Error: "claims is undefined"**
- The claims data isn't loading from backend
- Check if backend is running

### 3. Verify Tab Layout
After refreshing, you should see **7 tabs**:
1. **Factor Analyzer** ← NEW (this is what I added)
2. Adjust Weights
3. Factor Impact
4. Recommendations
5. Auto-Optimize
6. Before/After
7. Sensitivity

If you still only see 6 tabs, the frontend didn't recompile.

### 4. Check if Data is Loading
On the "Factor Analyzer" tab, you should see:
- A dropdown that says "Select Factor to Analyze"
- A slider (grayed out until you select a factor)
- Two buttons: "Recent (2024-2025)" and "All Data"
- Text showing "X claims analyzed"

If you see "0 claims analyzed":
- Backend isn't running
- Or backend isn't returning data
- Check: http://localhost:8000/api/claims (or whatever your backend port is)

### 5. Manual Test
Try this:
1. Click "Weight Recalibration" tab
2. You should see "Factor Analyzer" as the first sub-tab
3. Click on it
4. Select any factor from the dropdown (e.g., "Surgical_Intervention")
5. You should see charts and metrics appear

### 6. If Nothing Works - Quick Fix
If the tab is completely empty, try this simpler version:

Create this file: `d:\Repositories\dashBoard\frontend\src\components\recalibration\SimpleTest.tsx`

```typescript
export default function SimpleTest() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>TEST - Can you see this?</h1>
      <p>If you can read this, the component rendering works!</p>
    </div>
  );
}
```

Then temporarily edit RecalibrationTab.tsx:
- Import: `import SimpleTest from '../recalibration/SimpleTest';`
- Replace FactorWeightImpactAnalyzer with SimpleTest in the tab content

If you can see "TEST - Can you see this?", then the issue is with the FactorWeightImpactAnalyzer component itself.

---

## What's Most Likely Wrong?

Based on your screenshot showing a completely empty tab:

**Most Likely (90% chance):**
- Frontend hasn't recompiled yet after I added the new files
- **Fix:** Hard refresh browser (Ctrl+Shift+R) or restart frontend dev server

**Possible (8% chance):**
- TypeScript compilation error preventing the component from rendering
- **Fix:** Check terminal running `npm run dev` for errors

**Less Likely (2% chance):**
- Missing dependencies or import errors
- **Fix:** Run `npm install` in frontend directory

---

## Next Steps for You

1. **Try hard refresh first:** Ctrl+Shift+R in browser
2. **Check browser console:** F12 → Console tab → look for red errors
3. **Tell me what you see:**
   - How many tabs do you see under "Weight Recalibration"?
   - Is "Factor Analyzer" the first tab?
   - Any errors in console?
   - What does the terminal running `npm run dev` show?

I'll help you fix whatever issue you're seeing!
