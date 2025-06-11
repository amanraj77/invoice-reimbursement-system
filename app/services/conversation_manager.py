import uuid
from typing import Dict, List
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService
from app.models.invoice import ChatRequest, ChatResponse
from app.utils.logger import logger

class ConversationManager:
    def __init__(self):
        self.logger = logger
        self.vector_store = VectorStoreService()
        self.llm_service = LLMService()
        self.conversations: Dict[str, List[str]] = {}
    
    def process_query(self, request: ChatRequest) -> ChatResponse:
        try:
            conversation_id = request.conversation_id or str(uuid.uuid4())
            
            # Search for relevant documents
            relevant_docs = self.vector_store.search_similar_documents(
                query=request.query,
                n_results=5
            )
            
            # Generate response
            response_text = self.llm_service.generate_chat_response(
                query=request.query,
                context_docs=relevant_docs
            )
            
            # Store conversation
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = []
            
            self.conversations[conversation_id].extend([
                f"User: {request.query}",
                f"Assistant: {response_text}"
            ])
            
            sources = [f"Document {i+1}" for i in range(len(relevant_docs))]
            
            return ChatResponse(
                response=response_text,
                sources=sources,
                conversation_id=conversation_id,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Chat processing failed: {str(e)}")
            return ChatResponse(
                response=f"I apologize, but I encountered an error: {str(e)}",
                sources=[],
                conversation_id=request.conversation_id or str(uuid.uuid4()),
                success=False
            )