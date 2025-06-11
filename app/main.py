from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
invoice_analyzer = InvoiceAnalyzer()
conversation_manager = ConversationManager()

@app.on_event("startup")
async def startup_event():
    logger.info("Invoice Reimbursement System starting...")
    os.makedirs("./chroma_db", exist_ok=True)
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
    try:
        logger.info(f"Analysis request for: {employee_name}")
        
        # Validate files
        if not policy_file.filename.lower().endswith('.pdf'):
            raise HTTPException(400, "Policy file must be PDF")
        
        if not invoices_zip.filename.lower().endswith('.zip'):
            raise HTTPException(400, "Invoices must be ZIP file")
        
        # Read files
        policy_content = await policy_file.read()
        invoices_content = await invoices_zip.read()
        
        # Process
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
    try:
        response = conversation_manager.process_query(request)
        return response
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise HTTPException(500, f"Chat failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "vector_store": "operational",
            "llm_service": "operational",
            "pdf_processor": "operational"
        }
    }