# Troubleshoot Empty Dashboard

## Problem: Dashboard Shows Nothing

Your dashboard is blank with no graphs or filter options. Follow these steps:

## Step 1: Check if Backend is Running

Look at your backend terminal. You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

If NOT showing this, backend is NOT running.

**Fix: Start backend**
```bash
cd d:/Repositories/dashBoard/backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

## Step 2: Test Backend API

Open browser (NEW tab): http://localhost:8000/docs

**Expected:** API documentation page
**If connection refused:** Backend not running

Open: http://localhost:8000/api/v1/aggregated?use_fast=false

**Expected:** JSON data with yearSeverity, countyYear, etc.
**If "Not Found":** Endpoint missing

## Step 3: Check Browser Console

In dashboard, press F12, click Console tab.

**Look for red errors like:**
- "Failed to fetch" → Backend not running
- "CORS policy" → Backend CORS issue  
- "404" → Wrong endpoint
- "500" → Backend crashed

## Step 4: Check Network Tab

Press F12, click Network tab, refresh page.

Look for request to `/aggregated`:
- Status 200 (green) = Good
- Status 404/500 (red) = Error
- Failed = Backend not reachable

## Quick Fixes

**1. Backend Not Running:**
```bash
cd backend
./venv/Scripts/python.exe -m uvicorn app.main:app --reload
```

**2. Database Missing:**
```bash
cd backend
./venv/Scripts/python.exe load_csv_to_database.py
```

**3. Wrong Port:**
Check if backend shows different port, update frontend .env

**4. Hard Refresh Browser:**
Press Ctrl + Shift + R

