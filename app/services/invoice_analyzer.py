import time
from typing import List, Dict, Any
from app.services.pdf_processor import PDFProcessor
from app.services.llm_service import LLMService
from app.services.vector_store import VectorStoreService
from app.models.invoice import InvoiceAnalysis, AnalysisResponse
from app.utils.logger import logger

class InvoiceAnalyzer:
    def __init__(self):
        self.logger = logger
        self.pdf_processor = PDFProcessor()
        self.llm_service = LLMService()
        self.vector_store = VectorStoreService()
    
    def analyze_invoice_batch(self, policy_content: str, invoices_content: bytes, 
                            employee_name: str) -> AnalysisResponse:
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting analysis for {employee_name}")
            
            # Extract texts from ZIP
            extracted_texts = self.pdf_processor.process_zip_file(invoices_content)
            
            analysis_results = []
            
            # Analyze each invoice
            for filename, invoice_text in extracted_texts.items():
                try:
                    # Get LLM analysis
                    llm_result = self.llm_service.analyze_invoice(
                        invoice_text, filename, employee_name
                    )
                    
                    # Create analysis object
                    analysis = InvoiceAnalysis(**llm_result)
                    analysis_results.append(analysis)
                    
                    # Store in vector database
                    self.vector_store.store_invoice_analysis(llm_result, invoice_text)
                    
                except Exception as e:
                    self.logger.error(f"Failed to analyze {filename}: {str(e)}")
                    # Create error analysis
                    error_analysis = InvoiceAnalysis(
                        invoice_id=filename,
                        employee_name=employee_name,
                        amount=0.0,
                        category="food",
                        status="pending_review",
                        reimbursable_amount=0.0,
                        policy_violations=[f"Processing error: {str(e)}"],
                        reasoning=f"Failed to process: {str(e)}"
                    )
                    analysis_results.append(error_analysis)
            
            # Calculate summary
            summary = self._calculate_summary(analysis_results)
            processing_time = time.time() - start_time
            
            self.logger.info(f"Analysis completed in {processing_time:.2f}s")
            
            return AnalysisResponse(
                analysis_results=analysis_results,
                summary=summary,
                processing_time=round(processing_time, 2),
                success=True,
                message=f"Successfully analyzed {len(analysis_results)} invoices"
            )
            
        except Exception as e:
            self.logger.error(f"Batch analysis failed: {str(e)}")
            return AnalysisResponse(
                analysis_results=[],
                summary={},
                processing_time=0.0,
                success=False,
                message=f"Analysis failed: {str(e)}"
            )
    
    def _calculate_summary(self, analyses: List[InvoiceAnalysis]) -> Dict[str, Any]:
        if not analyses:
            return {
                "total_invoices": 0,
                "approved": 0,
                "declined": 0,
                "partial_approved": 0,
                "total_amount": 0.0,
                "total_reimbursable": 0.0,
                "compliance_rate": 0.0
            }
        
        total_invoices = len(analyses)
        approved = sum(1 for a in analyses if a.status == "approved")
        declined = sum(1 for a in analyses if a.status == "declined")
        partial_approved = sum(1 for a in analyses if a.status == "partial_approved")
        
        total_amount = sum(a.amount for a in analyses)
        total_reimbursable = sum(a.reimbursable_amount for a in analyses)
        
        compliance_rate = (approved / total_invoices * 100) if total_invoices > 0 else 0
        
        return {
            "total_invoices": total_invoices,
            "approved": approved,
            "declined": declined,
            "partial_approved": partial_approved,
            "total_amount": round(total_amount, 2),
            "total_reimbursable": round(total_reimbursable, 2),
            "compliance_rate": round(compliance_rate, 1)
        }
