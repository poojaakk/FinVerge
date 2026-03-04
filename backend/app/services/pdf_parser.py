"""
PDF Parser Service using PyPDF2 (Python equivalent to pdfjs-dist)

This module handles PDF text extraction similar to pdfjs-dist in JavaScript.
PyPDF2 provides robust PDF parsing capabilities for Python backend.

For frontend-based extraction, consider using pdf.js directly in the browser.
"""

import PyPDF2
from io import BytesIO
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_content: bytes) -> str:
    """
    Extract text content from PDF bytes using PyPDF2.
    
    This is the Python backend equivalent of pdfjs-dist text extraction.
    PyPDF2 uses similar PDF parsing techniques to PDF.js.
    
    Args:
        pdf_content: PDF file content as bytes
        
    Returns:
        Extracted text as string
    """
    try:
        pdf_file = BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        total_pages = len(pdf_reader.pages)
        
        logger.info(f"Extracting text from {total_pages} pages using PyPDF2 (pdfjs-dist equivalent)")
        
        for page_num, page in enumerate(pdf_reader.pages, 1):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                logger.debug(f"Extracted {len(page_text)} characters from page {page_num}")
            except Exception as e:
                logger.warning(f"Failed to extract text from page {page_num}: {e}")
                continue
        
        logger.info(f"Successfully extracted {len(text)} total characters")
        return text.strip()
    
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""


def parse_pdf_document(pdf_content: bytes) -> dict:
    """
    Parse PDF document and extract structured information.
    
    This function mimics the pdfjs-dist workflow:
    1. Load PDF document
    2. Extract text from all pages
    3. Return structured data
    
    Args:
        pdf_content: PDF file content as bytes
        
    Returns:
        Dictionary with extracted information including:
        - text: Extracted text content
        - page_count: Number of pages
        - extracted_successfully: Boolean indicating success
        - extraction_method: Method used for extraction
    """
    try:
        # Get page count
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_content))
        page_count = len(pdf_reader.pages)
        
        # Extract text (similar to pdfjs-dist getTextContent)
        text = extract_text_from_pdf(pdf_content)
        
        return {
            "text": text,
            "page_count": page_count,
            "extracted_successfully": bool(text),
            "extraction_method": "PyPDF2 (pdfjs-dist equivalent)",
            "metadata": {
                "pages": page_count,
                "text_length": len(text),
                "has_content": bool(text)
            }
        }
    except Exception as e:
        logger.error(f"Failed to parse PDF document: {e}")
        return {
            "text": "",
            "page_count": 0,
            "extracted_successfully": False,
            "extraction_method": "PyPDF2 (pdfjs-dist equivalent)",
            "error": str(e)
        }