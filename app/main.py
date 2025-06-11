from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import time

from app.models.invoice import ChatRequest
from app.services.invoice_analyzer import InvoiceAnalyzer
from app.services.conversation_manager import ConversationManager
from app.utils.logger import logger

# Initialize FastAPI app
app = FastAPI(
    title="IAI Solution Invoice Reimbursement System",
    description="AI-powered invoice analysis and RAG chatbot",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "https://*.streamlit.app",
        "https://invoice-system.streamlit.app"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize services
try:
    invoice_analyzer = InvoiceAnalyzer()
    conversation_manager = ConversationManager()
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    invoice_analyzer = None
    conversation_manager = None

@app.on_event("startup")
async def startup_event():
    logger.info("Invoice Reimbursement System starting...")
    # No directory creation needed - use in-memory storage
    logger.info("System ready!")

@app.get("/")
async def root():
    return {
        "message": "IAI Solution Invoice Reimbursement System",
        "status": "running",
        "version": "1.0.0"
    }

@app.post("/analyze-invoices")
async def analyze_invoices(
    policy_file: UploadFile = File(...),
    invoices_zip: UploadFile = File(...),
    employee_name: str = Form(...)
):
    if not invoice_analyzer:
        raise HTTPException(500, "Service not available")
        
    try:
        logger.info(f"Analysis request for: {employee_name}")
        
        # Validate files
        if not policy_file.filename.lower().endswith('.pdf'):
            raise HTTPException(400, "Policy file must be PDF")
        
        if not invoices_zip.filename.lower().endswith('.zip'):
            raise HTTPException(400, "Invoices must be ZIP file")
        
        # Check file sizes
        policy_content = await policy_file.read()
        invoices_content = await invoices_zip.read()
        
        if len(policy_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(400, "Policy file too large (max 10MB)")
            
        if len(invoices_content) > 25 * 1024 * 1024:  # 25MB
            raise HTTPException(400, "Invoice ZIP too large (max 25MB)")
        
        # Process invoices
        result = invoice_analyzer.analyze_invoice_batch(
            policy_content=policy_content.decode('utf-8', errors='ignore'),
            invoices_content=invoices_content,
            employee_name=employee_name
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(500, f"Analysis failed: {str(e)}")

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not conversation_manager:
        raise HTTPException(500, "Service not available")
        
    try:
        response = conversation_manager.process_query(request)
        return response
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise HTTPException(500, f"Chat failed: {str(e)}")

@app.get("/health")
async def health_check():
    services_status = {
        "vector_store": "operational" if conversation_manager else "unavailable",
        "llm_service": "operational" if invoice_analyzer else "unavailable",
        "pdf_processor": "operational"
    }
    
    overall_status = "healthy" if all(s == "operational" for s in services_status.values()) else "degraded"
    
    return {
        "status": overall_status,
        "services": services_status,
        "version": "1.0.0"
    }

@app.get("/ping")
async def ping():
    return {"status": "ok"}
