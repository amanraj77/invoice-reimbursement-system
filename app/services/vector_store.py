import json
from typing import List, Dict, Any
from app.utils.logger import logger

class VectorStoreService:
    """Simple in-memory storage for demo purposes"""
    
    def __init__(self):
        self.logger = logger
        self.documents = []  # Simple list storage
        self.logger.info("Simple vector store initialized")
    
    def store_invoice_analysis(self, analysis_result: Dict[str, Any], invoice_text: str):
        """Store invoice analysis in memory"""
        try:
            document = {
                "id": analysis_result.get('invoice_id', ''),
                "employee_name": analysis_result.get('employee_name', ''),
                "status": analysis_result.get('status', ''),
                "amount": float(analysis_result.get('amount', 0)),
                "contains_alcohol": bool(analysis_result.get('contains_alcohol', False)),
                "reasoning": analysis_result.get('reasoning', ''),
                "full_text": invoice_text,
                "analysis": analysis_result
            }
            
            self.documents.append(document)
            self.logger.info(f"Stored analysis: {analysis_result.get('invoice_id', 'unknown')}")
            
        except Exception as e:
            self.logger.error(f"Failed to store analysis: {str(e)}")
    
    def search_similar_documents(self, query: str, n_results: int = 5) -> List[str]:
        """Simple keyword-based search"""
        try:
            query_lower = query.lower()
            results = []
            
            for doc in self.documents[-20:]:  # Last 20 documents only
                # Simple keyword matching
                text = f"{doc['reasoning']} {doc['employee_name']} {doc['status']} {doc['full_text']}".lower()
                
                if any(word in text for word in query_lower.split()):
                    result_text = f"""
                    Invoice: {doc['id']}
                    Employee: {doc['employee_name']}
                    Status: {doc['status']}
                    Amount: ₹{doc['amount']}
                    Reasoning: {doc['reasoning']}
                    """
                    results.append(result_text)
                
                if len(results) >= n_results:
                    break
            
            self.logger.info(f"Found {len(results)} documents for query")
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            return []
