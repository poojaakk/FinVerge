from pydantic import BaseModel
from typing import Optional, List

class DocumentBase(BaseModel):
    text: str
    source: str

class Document(DocumentBase):
    id: Optional[int] = None

class DocumentCreate(DocumentBase):
    pass

class POItem(BaseModel):
    item: str
    qty: int
    price: float

class InvoiceItem(BaseModel):
    item: str
    qty: int
    price: float

class GRItem(BaseModel):
    item: str
    qty: int
    price: float

class VerificationRequest(BaseModel):
    po_items: List[POItem]
    invoice_items: List[InvoiceItem]
    gr_items: List[GRItem] = []  # Optional for 2-way matching