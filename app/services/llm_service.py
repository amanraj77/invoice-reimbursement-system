import google.generativeai as genai
import json
import re
from typing import Dict, Any, List
from app.config import Config
from app.utils.exceptions import LLMServiceError
from app.utils.logger import logger

class LLMService:
    def __init__(self):
        self.logger = logger
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(Config.LLM_MODEL)
            self.logger.info("LLM Service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM service: {str(e)}")
            raise LLMServiceError(f"LLM initialization failed: {str(e)}")
    
    def analyze_invoice(self, invoice_text: str, filename: str, employee_name: str) -> Dict[str, Any]:
        prompt = f"""
        Analyze this invoice text for IAI Solution company against their reimbursement policy.

        COMPANY POLICY:
        - Food & Beverages: ₹200 per meal (NO ALCOHOL - automatic decline)
        - Travel: ₹2,000 per trip + ₹150 daily office cabs
        - Accommodation: ₹50 per night
        - Submit within 30 days with receipts

        INVOICE TEXT:
        {invoice_text}

        EMPLOYEE: {employee_name}
        FILENAME: {filename}

        Return ONLY valid JSON with this exact structure:
        {{
            "invoice_id": "receipt_number_or_filename",
            "employee_name": "{employee_name}",
            "vendor_name": "restaurant_name",
            "date": "YYYY-MM-DD",
            "amount": 0.0,
            "category": "food",
            "items": [{{"description": "item", "quantity": 1, "unit_price": 0.0, "amount": 0.0}}],
            "status": "approved",
            "reimbursable_amount": 0.0,
            "policy_violations": [],
            "reasoning": "explanation",
            "contains_alcohol": false,
            "submission_date_valid": true
        }}

        ANALYSIS RULES:
        1. ANY alcohol (wine, whisky, beer, vodka, rum, spirits) → status="declined", reimbursable_amount=0
        2. Food > ₹200 → status="partial_approved", reimbursable_amount=200
        3. Travel > ₹2000 → status="partial_approved", reimbursable_amount=2000
        4. Daily transport > ₹150 → status="partial_approved", reimbursable_amount=150
        5. Detect alcohol keywords carefully in item descriptions
        """
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Clean JSON response
            if result_text.startswith('```json'):
                result_text = result_text[7:-3]
            elif result_text.startswith('```'):
                result_text = result_text[3:-3]
            
            # Remove any extra text before/after JSON
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group()
            
            result = json.loads(result_text)
            
            # Validate and fix result
            result = self._validate_analysis_result(result, filename, employee_name)
            
            self.logger.info(f"Successfully analyzed: {filename}")
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error for {filename}: {str(e)}")
            return self._create_fallback_analysis(filename, employee_name, f"JSON parsing error: {str(e)}")
        except Exception as e:
            self.logger.error(f"LLM analysis failed for {filename}: {str(e)}")
            return self._create_fallback_analysis(filename, employee_name, str(e))
    
    def _validate_analysis_result(self, result: Dict[str, Any], filename: str, employee_name: str) -> Dict[str, Any]:
        """Validate and fix analysis result"""
        # Ensure required fields exist
        result.setdefault("invoice_id", filename)
        result.setdefault("employee_name", employee_name)
        result.setdefault("vendor_name", "Unknown")
        result.setdefault("date", None)
        result.setdefault("amount", 0.0)
        result.setdefault("category", "food")
        result.setdefault("items", [])
        result.setdefault("status", "pending_review")
        result.setdefault("reimbursable_amount", 0.0)
        result.setdefault("policy_violations", [])
        result.setdefault("reasoning", "Analysis completed")
        result.setdefault("contains_alcohol", False)
        result.setdefault("submission_date_valid", True)
        
        # Ensure numeric fields are numeric
        try:
            result["amount"] = float(result["amount"])
            result["reimbursable_amount"] = float(result["reimbursable_amount"])
        except (ValueError, TypeError):
            result["amount"] = 0.0
            result["reimbursable_amount"] = 0.0
        
        return result
    
    def _create_fallback_analysis(self, filename: str, employee_name: str, error: str) -> Dict[str, Any]:
        return {
            "invoice_id": filename,
            "employee_name": employee_name,
            "vendor_name": "Unknown",
            "date": None,
            "amount": 0.0,
            "category": "food",
            "items": [],
            "status": "pending_review",
            "reimbursable_amount": 0.0,
            "policy_violations": [f"Processing error: {error}"],
            "reasoning": f"Could not analyze due to error: {error}. Manual review required.",
            "contains_alcohol": False,
            "submission_date_valid": True
        }
    
    def generate_chat_response(self, query: str, context_docs: List[str]) -> str:
        context_text = "\n\n".join(context_docs[:5]) if context_docs else "No relevant documents found."
        
        prompt = f"""
        You are an assistant for IAI Solution Invoice Reimbursement System.
        
        CONTEXT FROM DATABASE:
        {context_text}
        
        USER QUERY: {query}
        
        COMPANY POLICY:
        - Food: ₹200 per meal (no alcohol)
        - Travel: ₹2,000 per trip + ₹150 daily cabs
        - Accommodation: ₹50 per night
        - 30-day submission deadline
        
        Provide a helpful response in markdown format based on the context.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            self.logger.error(f"Chat response failed: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"