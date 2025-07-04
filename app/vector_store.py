import os
from typing import List
from langchain.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

class VectorStoreManager:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.legal_knowledge_store = None
        self.case_data_store = {}

    def add_legal_knowledge(self, texts: List[str]):
        self.legal_knowledge_store = FAISS.from_texts(texts, self.embeddings)

    def add_case_data(self, texts: List[str], case_id: str):
        self.case_data_store[case_id] = FAISS.from_texts(texts, self.embeddings)

    def search_legal_knowledge(self, query: str, k: int = 3) -> List[str]:
        if not self.legal_knowledge_store:
            return []
        docs = self.legal_knowledge_store.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]

    def search_case_data(self, query: str, k: int = 5, case_id: str = None) -> List[str]:
        if not case_id or case_id not in self.case_data_store:
            return []
        docs = self.case_data_store[case_id].similarity_search(query, k=k)
        return [doc.page_content for doc in docs] 