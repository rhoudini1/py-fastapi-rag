import os
from typing import Optional, List
import google.generativeai as genai
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.embeddings import Embeddings
from langchain.agents.middleware import dynamic_prompt, ModelRequest

from app.domain.config import settings
from app.domain.entities import Document


class GoogleGenerativeAIEmbeddings(Embeddings):
    """Custom embeddings class using Google Generative AI SDK directly."""
    
    def __init__(self, model: str = "gemini-embedding-001"):
        self.model_name = model
        genai.configure(api_key=settings.google_api_key)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of documents."""
        embeddings = []
        # Process each text individually
        for text in texts:
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type="RETRIEVAL_DOCUMENT"
            )
            # The result is an EmbedContentResponse object, access the embedding attribute
            if hasattr(result, 'embedding'):
                embeddings.append(result.embedding)
            elif hasattr(result, 'embeddings'):
                embeddings.extend(result.embeddings)
            elif isinstance(result, dict):
                embeddings.append(result.get('embedding', result.get('embeddings', [result])[0]))
            else:
                embeddings.append(result)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a query string."""
        result = genai.embed_content(
            model=self.model_name,
            content=text,
            task_type="RETRIEVAL_QUERY"
        )
        # The result is an EmbedContentResponse object, access the embedding attribute
        if hasattr(result, 'embedding'):
            return result.embedding
        elif hasattr(result, 'embeddings') and len(result.embeddings) > 0:
            return result.embeddings[0]
        elif isinstance(result, dict):
            return result.get('embedding', result.get('embeddings', [result])[0])
        return result


class GeminiGateway:
    """Gateway for Google Gemini API integration with caching to reduce API calls."""
    
    CHROMA_DIR = "./chroma_docs"
    
    # Class-level cache for embeddings and vector store (reused across instances)
    _embeddings: Optional[GoogleGenerativeAIEmbeddings] = None
    _vector_store: Optional[Chroma] = None
    _genai_model: Optional[genai.GenerativeModel] = None
    
    def __init__(self):
        genai.configure(api_key=settings.google_api_key)
        
        if GeminiGateway._genai_model is None:
            GeminiGateway._genai_model = genai.GenerativeModel(
                'gemini-2.0-flash-lite'
            )
        
        if GeminiGateway._embeddings is None:
            GeminiGateway._embeddings = GoogleGenerativeAIEmbeddings(
                model="gemini-embedding-001"
                )
        
        # Initialize vector store (reused across all instances)
        if GeminiGateway._vector_store is None:
            GeminiGateway._vector_store = Chroma(
                collection_name="documents",
                embedding_function=GeminiGateway._embeddings,
                persist_directory=self.CHROMA_DIR
            )

    @property
    def model(self) -> genai.GenerativeModel:
        """Get the Gemini chat model instance."""
        return GeminiGateway._genai_model

    @property
    def embeddings(self) -> GoogleGenerativeAIEmbeddings:
        """Get the embeddings instance (cached)."""
        return GeminiGateway._embeddings

    @property
    def vector_store(self) -> Chroma:
        """Get the vector store instance (cached)."""
        return GeminiGateway._vector_store


    @dynamic_prompt
    def prompt_with_context(self, request: ModelRequest):
        """Inject retrieved context into the prompt BEFORE the user message."""

        last_user_msg = request.state["messages"][-1].text

        retrieved_docs = self.vector_store.similarity_search(last_user_msg, k=5)
        docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

        system_message = (
            "You are a helpful assistant. "
            "Use ONLY the following retrieved context to answer. "
            "If the context does not contain the answer, say you don't know.\n\n"
            f"CONTEXT:\n{docs_content}"
        )

        # Return a message the Gemini middleware can understand
        return [
            {"role": "system", "parts": [system_message]}
        ]


    def index_document(self, document: Document):
        try:
            loader = PyPDFLoader(f"./uploaded_files/{document.id}.pdf")
            documents = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=200
            )
            all_splits = text_splitter.split_documents(documents)

            # Add documents to vector store
            # This will make one API call per chunk for embeddings
            self.vector_store.add_documents(documents=all_splits)
            
        except Exception as e:
            # Log the error (you might want to use proper logging)
            error_msg = f"Failed to index document {document.id}: {str(e)}"
            raise RuntimeError(error_msg) from e

    async def generate_response(self, prompt: str) -> str:
        """Generate a response from the Gemini model with context."""
        try:
            # Retrieve context
            retrieved_docs = self.vector_store.similarity_search(prompt, k=5)
            docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

            # Build structured prompt
            final_prompt = f"""
            Use the following context to answer the question.
            If the context does not contain the answer, say you don't know.

            CONTEXT:
            {docs_content}

            QUESTION:
            {prompt}

            ANSWER:
            """.strip()

            response = await self.model.generate_content_async(
                contents=[final_prompt]
            )

            return response.text
        except Exception as e:
            error_msg = f"Failed to generate response: {str(e)}"
            raise RuntimeError(error_msg) from e
