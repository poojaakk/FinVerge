# FinVerge - AI-Powered Procurement Document Verification System

FinVerge is an intelligent document verification system that automates the matching and validation of procurement documents (Purchase Orders, Invoices, and Goods Receipts) using AI and RAG (Retrieval-Augmented Generation) technology.

## Features

- **2-Way Matching**: Verify Purchase Orders against Invoices
- **3-Way Matching**: Verify Purchase Orders, Invoices, and Goods Receipts together
- **AI-Powered Analysis**: Uses Google Gemini AI for intelligent discrepancy explanation
- **RAG System**: Context-aware validation using company policies and vendor contracts
- **PDF Processing**: Automatic text extraction and structured data parsing
- **Real-time Verification**: Instant feedback on document matching
- **Detailed Reports**: Comprehensive discrepancy analysis with recommendations

## Architecture

### Backend (Python/FastAPI)
- **FastAPI**: High-performance REST API
- **PyPDF2**: PDF text extraction
- **Scikit-learn**: Vector embeddings and similarity search
- **Google Gemini**: AI-powered explanation generation
- **Pydantic**: Data validation and serialization

### Frontend (HTML/CSS/JavaScript)
- Vanilla JavaScript for simplicity
- Drag-and-drop file upload
- Real-time processing visualization
- Responsive design

### RAG Pipeline
1. **Document Upload**: PDF files uploaded via REST API
2. **Text Extraction**: PyPDF2 extracts text from PDFs
3. **Structured Parsing**: Regex-based extraction of items, quantities, and prices
4. **Rule-Based Matching**: Fast comparison of document items
5. **RAG Validation**: Retrieves relevant policies for context
6. **AI Explanation**: Gemini generates human-readable explanations
7. **Final Verdict**: Approved, Needs Review, or Rejected

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Google Gemini API key (optional, for AI features)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd FinVerge
```

2. **Install backend dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

4. **Start the application**
```bash
# From the root directory
bash start_finverge.sh
```

Or manually:
```bash
# Terminal 1 - Backend
cd backend
python3 run.py

# Terminal 2 - Frontend
cd frontend
python3 -m http.server 3000
```

5. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Configuration

### Backend Configuration (`backend/app/config.py`)
```python
GEMINI_API_KEY = "your-api-key-here"
PRICE_TOLERANCE_PERCENT = 5.0  # 5% price variance allowed
QUANTITY_TOLERANCE_PERCENT = 2.0  # 2% quantity variance allowed
```

### Knowledge Base
Add your company policies and vendor contracts to:
- `knowledge-base/policies/` - Company procurement policies
- `knowledge-base/vendor_contracts/` - Vendor-specific agreements

## Usage

### 2-Way Matching (PO vs Invoice)

1. Select "2-Way Matching" from the homepage
2. Upload Purchase Order PDF
3. Upload Invoice PDF
4. Click "Verify Documents"
5. Review the verification results

### 3-Way Matching (PO vs Invoice vs GR)

1. Select "3-Way Matching" from the homepage
2. Upload Purchase Order PDF
3. Upload Invoice PDF
4. Upload Goods Receipt PDF
5. Click "Verify Documents"
6. Review the verification results

## Test Samples

The system includes 40 curated test samples:

### 2-Way Matching (20 samples)
- **Sample1-10**: Perfect matches
- **Sample11-20**: Various discrepancies (quantity mismatch, price mismatch, missing items, extra items)

### 3-Way Matching (20 samples)
- **Sample21-30**: Perfect matches
- **Sample31-40**: Various discrepancies (price mismatch, partial receipt, damaged goods)

Location: `datasets/test_samples/`

### Generate Additional Test Samples
```bash
# Generate 40 test samples
python3 generate_test_samples_extended.py

# Generate large datasets (500+ samples)
python3 generate_pdf_datasets.py
```

## API Endpoints

### Document Upload
```
POST /upload/po
POST /upload/invoice
POST /upload/gr
```
Upload PDF documents and extract structured data.

### Verification
```
POST /verify/2way
POST /verify/3way
```
Verify documents and get detailed analysis.

### Health Check
```
GET /health
```
Check API status.

## Project Structure

```
FinVerge/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── models/              # Pydantic models
│   │   ├── routes/              # API endpoints
│   │   └── services/            # Business logic
│   │       ├── pdf_parser.py    # PDF text extraction
│   │       ├── extractor.py     # Item extraction
│   │       ├── matcher.py       # Document matching
│   │       ├── rag_service.py   # RAG pipeline
│   │       └── llm.py           # AI integration
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── index.html               # Main UI
│   └── app/                     # Additional pages
├── knowledge-base/
│   ├── policies/                # Company policies
│   └── vendor_contracts/        # Vendor agreements
├── datasets/
│   ├── test_samples/            # 40 test samples
│   ├── 2way_matching/           # Large 2-way dataset
│   └── 3way_matching/           # Large 3-way dataset
├── generate_test_samples_extended.py
├── generate_pdf_datasets.py
├── start_finverge.sh
└── README.md
```

## Discrepancy Types

### 2-Way Matching
- **Quantity Mismatch**: Ordered quantity differs from invoiced quantity
- **Price Mismatch**: Unit price differs beyond tolerance threshold
- **Missing from Invoice**: Item in PO but not in invoice
- **Extra in Invoice**: Item in invoice but not in PO

### 3-Way Matching
- **PO vs Invoice**: Same as 2-way matching
- **Invoice vs GR**: Invoiced quantity differs from received quantity
- **Partial Receipt**: Not all ordered items were received
- **Damaged Goods**: Received quantity less than invoiced

## Verification Results

### Status Types
- **APPROVED**: All items match or discrepancies are within acceptable limits
- **NEEDS_REVIEW**: Minor discrepancies requiring manual review
- **REJECTED**: Significant discrepancies violating procurement policies

### Result Components
- **Summary**: Overall recommendation and item counts
- **Item Details**: Per-item discrepancy analysis
- **AI Explanation**: Context-aware explanation of each discrepancy
- **Recommendations**: Actionable next steps
- **Supporting Documents**: Relevant policies used in analysis

## Testing

### Run Backend Tests
```bash
cd backend
python3 test_backend.py
```

### Test PDF Upload
```bash
python3 test_pdf_upload.py
```

### Test Matching Logic
```bash
python3 test_matching.py
```

### Debug Extraction
```bash
python3 test_extraction_debug.py
```

## Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify Python dependencies are installed
- Check `.env` file exists with valid configuration

### PDF extraction fails
- Ensure PDFs are not password-protected
- Verify PDFs contain extractable text (not scanned images)
- Check PDF file size (large files may take longer)

### AI explanations not working
- Verify GEMINI_API_KEY is set in `.env`
- Check API key has sufficient quota
- System falls back to rule-based explanations if AI fails

### Matching not accurate
- Review price/quantity tolerance settings in `config.py`
- Check if PDF text extraction is working correctly
- Verify item names are consistent across documents

## Performance

- **PDF Processing**: ~1-2 seconds per document
- **2-Way Verification**: ~2-3 seconds
- **3-Way Verification**: ~3-5 seconds
- **Concurrent Requests**: Supports multiple simultaneous verifications

## Security Considerations

- All file uploads are processed in memory
- No permanent storage of uploaded documents
- API endpoints should be protected with authentication in production
- Sensitive data should be encrypted in transit (use HTTPS)

## Future Enhancements

- [ ] OCR support for scanned PDFs
- [ ] Multi-language support
- [ ] Batch processing
- [ ] Email notifications
- [ ] Audit trail and logging
- [ ] User authentication and authorization
- [ ] Database integration for historical data
- [ ] Advanced analytics and reporting
- [ ] Mobile app support

## System Status

- Backend API: Fully functional
- PDF Processing: Working
- 2-Way Verification: Working
- 3-Way Verification: Working
- RAG System: Working (sklearn-based)
- Web Interface: Complete
- AI Analysis: Requires Gemini API key

## License

[Your License Here]

## Support

For issues, questions, or contributions, please contact [your-email@example.com]

## Acknowledgments

- Google Gemini for AI capabilities
- FastAPI for the excellent web framework
- PyPDF2 for PDF processing
- Scikit-learn for vector embeddings
