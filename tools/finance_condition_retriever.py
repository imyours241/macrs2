from langchain.tools import BaseTool
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from typing import Optional
import os
from dotenv import load_dotenv

class FinanceConditionRetriever(BaseTool):
    name: str = "finance_condition_retriever"
    description: str = "차량 구매 시 적용 가능한 금융 조건을 검색하는 도구입니다. 할부금리, 보증금, 월임대료 등에 대한 정보를 제공합니다."
    embeddings: Optional[OpenAIEmbeddings] = None
    db: Optional[Chroma] = None
    
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.embeddings = OpenAIEmbeddings()
        
        # Get database path from environment variable or use default
        db_path = os.getenv("CHROMA_DB_PATH", "./database")
        
        # Ensure database directory exists
        os.makedirs(db_path, exist_ok=True)
        
        # Initialize ChromaDB with basic settings
        self.db = Chroma(
            collection_name="finance_conditions",
            embedding_function=self.embeddings,
            persist_directory=db_path
        )
        
        # Initialize with empty collection if no documents exist
        if len(self.db.get()) == 0:
            self.db.add_texts(
                texts=["샘플 금융 조건 데이터입니다. 실제 데이터를 추가해주세요."],
                metadatas=[{"source": "sample"}]
            )
    
    def _run(self, query: str) -> str:
        """금융 조건을 검색합니다."""
        try:
            results = self.db.similarity_search(query)
            if not results:
                return "해당하는 금융 조건을 찾을 수 없습니다."
            return results[0].page_content
        except Exception as e:
            return f"금융 조건 검색 중 오류가 발생했습니다: {str(e)}" 