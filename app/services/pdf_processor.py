import io
import zipfile
import pdfplumber
import pypdf
from typing import Dict
from app.utils.exceptions import PDFExtractionError
from app.utils.logger import logger

class PDFProcessor:
    def __init__(self):
        self.logger = logger
    
    def extract_text_from_pdf(self, pdf_content: bytes, filename: str = "") -> str:
        try:
            # Method 1: pdfplumber
            text = self._extract_with_pdfplumber(pdf_content)
            if text and len(text.strip()) > 20:
                self.logger.info(f"Extracted text with pdfplumber: {filename}")
                return text
                
            # Method 2: pypdf fallback
            text = self._extract_with_pypdf(pdf_content)
            if text and len(text.strip()) > 20:
                self.logger.info(f"Extracted text with pypdf: {filename}")
                return text
                
            # If still no good text, return what we have
            return text or "No readable text found"
            
        except Exception as e:
            self.logger.error(f"PDF extraction failed for {filename}: {str(e)}")
            return f"Failed to extract text from {filename}"
    
    def _extract_with_pdfplumber(self, pdf_content: bytes) -> str:
        try:
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                return "\n".join(text_parts)
        except Exception:
            return ""
    
    def _extract_with_pypdf(self, pdf_content: bytes) -> str:
        try:
            reader = pypdf.PdfReader(io.BytesIO(pdf_content))
            text_parts = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            return "\n".join(text_parts)
        except Exception:
            return ""
    
    def process_zip_file(self, zip_content: bytes) -> Dict[str, str]:
        extracted_texts = {}
        
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
                for filename in zip_file.namelist():
                    if filename.lower().endswith('.pdf') and not filename.startswith('__MACOSX'):
                        try:
                            pdf_content = zip_file.read(filename)
                            text = self.extract_text_from_pdf(pdf_content, filename)
                            extracted_texts[filename] = text
                            self.logger.info(f"Processed: {filename}")
                        except Exception as e:
                            self.logger.error(f"Failed to process {filename}: {str(e)}")
                            extracted_texts[filename] = f"Error processing {filename}: {str(e)}"
                            
        except Exception as e:
            raise PDFExtractionError(f"Failed to process ZIP file: {str(e)}")
            
        if not extracted_texts:
            raise PDFExtractionError("No valid PDFs found in ZIP file")
            
        return extracted_texts