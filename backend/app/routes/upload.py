from fastapi import APIRouter, UploadFile, File, HTTPException
from ..services.pdf_parser import parse_pdf_document
from ..services.extractor import extract_items
from pydantic import BaseModel
from typing import List

class ExtractedItem(BaseModel):
    name: str
    quantity: int
    unit_price: float
    total_price: float

class UploadResponse(BaseModel):
    success: bool
    message: str
    document_info: dict
    extracted_items: List[ExtractedItem]
    processing_notes: List[str]

router = APIRouter()

@router.post("/", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload and process PDF document.
    
    Processing Pipeline:
    1. Validate PDF file
    2. Extract text using PyPDF2 (pdfjs-dist equivalent)
    3. Parse structured data (items, quantities, prices)
    4. Return extracted information
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Please upload a PDF file")
    
    try:
        content = await file.read()
        processing_notes = []
        
        # Validate file size
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
        
        # Step 2: Text Extraction (pdfjs-dist equivalent using PyPDF2)
        processing_notes.append("✓ Text extraction using PyPDF2 (pdfjs-dist equivalent)")
        
        try:
            pdf_data = parse_pdf_document(content)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse PDF: {str(e)}. The PDF might be corrupted or password-protected."
            )
        
        if not pdf_data["extracted_successfully"]:
            processing_notes.append("⚠ Warning: Text extraction may be incomplete")
        else:
            processing_notes.append(f"✓ Extracted text from {pdf_data['page_count']} pages")
        
        if not pdf_data["text"] or len(pdf_data["text"].strip()) < 10:
            processing_notes.append("⚠ Warning: Very little text extracted. Document might be image-based.")
        
        # Step 3: Structured Parsing (items, qty, price)
        processing_notes.append("✓ Parsing structured data (items, quantities, prices)")
        
        try:
            raw_items = extract_items(pdf_data["text"])
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract items: {str(e)}"
            )
        
        # Convert to user-friendly format
        extracted_items = []
        for item in raw_items:
            try:
                extracted_items.append(ExtractedItem(
                    name=item["item"],
                    quantity=item["qty"],
                    unit_price=item["price"],
                    total_price=item["qty"] * item["price"]
                ))
            except KeyError as e:
                processing_notes.append(f"⚠ Skipped malformed item (missing {str(e)})")
                continue
        
        # Add processing notes
        if extracted_items:
            processing_notes.append(f"✓ Successfully extracted {len(extracted_items)} items")
        else:
            processing_notes.append("⚠ No items found - document may need manual review")
            processing_notes.append("💡 Tip: Ensure PDF contains a table with Item, Quantity, and Price columns")
        
        return UploadResponse(
            success=True,
            message=f"Successfully processed {file.filename}",
            document_info={
                "filename": file.filename,
                "file_size_mb": round(len(content) / (1024 * 1024), 2),
                "page_count": pdf_data["page_count"],
                "text_extracted": pdf_data["extracted_successfully"],
                "extraction_method": pdf_data.get("extraction_method", "PyPDF2")
            },
            extracted_items=extracted_items,
            processing_notes=processing_notes
        )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Failed to process document: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)  # Log to console
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process document: {str(e)}"
        )
