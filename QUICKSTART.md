# FinVerge Quick Start Guide

Get FinVerge up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation Steps

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure API Key (Optional)

For AI-powered explanations, add your Google Gemini API key:

```bash
cd backend
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your-key-here
```

Without an API key, the system will still work with rule-based explanations.

### 3. Start the Application

**Option A: Using the startup script (Recommended)**
```bash
bash start_finverge.sh
```

**Option B: Manual startup**
```bash
# Terminal 1 - Start Backend
cd backend
python3 run.py

# Terminal 2 - Start Frontend
cd frontend
python3 -m http.server 3000
```

### 4. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## First Test

### Test 2-Way Matching

1. Go to http://localhost:3000
2. Click "2-Way Matching"
3. Upload test files:
   - PO: `datasets/test_samples/Sample1_PO_MATCH.pdf`
   - Invoice: `datasets/test_samples/Sample1_INV_MATCH.pdf`
4. Click "Verify Documents"
5. See the result: "APPROVED - Documents match perfectly"

### Test 3-Way Matching

1. Click "3-Way Matching"
2. Upload test files:
   - PO: `datasets/test_samples/Sample21_PO_MATCH.pdf`
   - Invoice: `datasets/test_samples/Sample21_INV_MATCH.pdf`
   - GR: `datasets/test_samples/Sample21_GR_MATCH.pdf`
3. Click "Verify Documents"
4. See the result: "APPROVED - All documents match perfectly"

### Test Mismatch Detection

1. Click "2-Way Matching"
2. Upload test files:
   - PO: `datasets/test_samples/Sample11_PO_MISMATCH.pdf`
   - Invoice: `datasets/test_samples/Sample11_INV_MISMATCH.pdf`
3. Click "Verify Documents"
4. See discrepancies detected with detailed explanations

## Available Test Samples

The system includes 40 pre-generated test samples:

- **Sample1-10**: 2-Way Perfect Matches
- **Sample11-20**: 2-Way Mismatches
- **Sample21-30**: 3-Way Perfect Matches
- **Sample31-40**: 3-Way Mismatches

All samples are in `datasets/test_samples/`

## Generate More Test Data

```bash
# Generate 40 diverse test samples
python3 generate_test_samples_extended.py

# Generate large datasets (500+ samples)
python3 generate_pdf_datasets.py
```

## Common Commands

### Check Backend Status
```bash
curl http://localhost:8000/health
```

### Run Tests
```bash
# Test backend functionality
python3 backend/test_backend.py

# Test PDF upload
python3 test_pdf_upload.py

# Test matching logic
python3 test_matching.py
```

### Stop the Application

Press `Ctrl+C` in the terminal where the servers are running.

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Dependencies Not Installing
```bash
# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -r backend/requirements.txt -v
```

### PDF Not Extracting
- Ensure PDF contains text (not scanned images)
- Check PDF is not password-protected
- Try with provided test samples first

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore the API at http://localhost:8000/docs
3. Add your company policies to `knowledge-base/policies/`
4. Customize tolerance settings in `backend/app/config.py`
5. Test with your own procurement documents

## Need Help?

- Check the [README.md](README.md) for detailed documentation
- Review API documentation at http://localhost:8000/docs
- Run debug scripts in the root directory

## System Requirements

- **OS**: macOS, Linux, or Windows
- **Python**: 3.8+
- **RAM**: 2GB minimum
- **Disk**: 500MB for application + test data

Enjoy using FinVerge!
