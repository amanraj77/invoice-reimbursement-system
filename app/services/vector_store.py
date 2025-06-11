import chromadb
from chromadb.utils import embedding_functions
import uuid
from typing import List, Dict, Any
from app.config import Config
from app.utils.logger import logger

class VectorStoreService:
    def __init__(self):
        self.logger = logger
        try:
            self.client = chromadb.PersistentClient(path=Config.CHROMA_PERSIST_DIRECTORY)
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self.collection = self._get_or_create_collection()
            self.logger.info("Vector store initialized successfully")
        except Exception as e:
            self.logger.error(f"Vector store initialization failed: {str(e)}")
            # Continue without vector store
            self.collection = None
    
    def _get_or_create_collection(self):
        try:
            return self.client.get_or_create_collection(
                name=Config.CHROMA_COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
        except Exception as e:
            self.logger.error(f"Failed to create collection: {str(e)}")
            return None
    
    def store_invoice_analysis(self, analysis_result: Dict[str, Any], invoice_text: str):
        if not self.collection:
            return
            
        try:
            doc_id = str(uuid.uuid4())
            
            document_text = f"""
            Invoice: {analysis_result.get('invoice_id', 'Unknown')}
            Employee: {analysis_result.get('employee_name', 'Unknown')}
            Vendor: {analysis_result.get('vendor_name', 'Unknown')}
            Amount: ₹{analysis_result.get('amount', 0)}
            Category: {analysis_result.get('category', 'Unknown')}
            Status: {analysis_result.get('status', 'Unknown')}
            Reimbursable: ₹{analysis_result.get('reimbursable_amount', 0)}
            Alcohol: {analysis_result.get('contains_alcohol', False)}
            Items: {', '.join([item.get('description', '') for item in analysis_result.get('items', [])])}
            Reasoning: {analysis_result.get('reasoning', '')}
            """
            
            metadata = {
                "invoice_id": analysis_result.get('invoice_id', ''),
                "employee_name": analysis_result.get('employee_name', ''),
                "category": analysis_result.get('category', ''),
                "status": analysis_result.get('status', ''),
                "amount": float(analysis_result.get('amount', 0)),
                "contains_alcohol": bool(analysis_result.get('contains_alcohol', False))
            }
            
            self.collection.add(
                documents=[document_text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            self.logger.info(f"Stored analysis: {analysis_result.get('invoice_id', doc_id)}")
            
        except Exception as e:
            self.logger.error(f"Failed to store analysis: {str(e)}")
    
    def search_similar_documents(self, query: str, n_results: int = 5) -> List[str]:
        if not self.collection:
            return []
            
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            documents = results.get('documents', [[]])[0]
            self.logger.info(f"Found {len(documents)} documents for query")
            return documents
            
        except Exception as e:
            self.logger.error(f"Vector search failed: {str(e)}")
            return []