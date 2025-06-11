class InvoiceProcessingError(Exception):
    """Base exception for invoice processing"""
    pass

class PDFExtractionError(InvoiceProcessingError):
    """PDF cannot be processed"""
    pass

class LLMServiceError(InvoiceProcessingError):
    """LLM API call failed"""
    pass
class VectorStoreError(InvoiceProcessingError):
    pass