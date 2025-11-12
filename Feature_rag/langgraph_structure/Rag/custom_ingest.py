
from langgraph_structure.Rag.custom_pgvector import CustomPGVector
from langgraph_structure.Rag.custom_loader import CustomCSVLoader
from typing import List


class VectorIngest():
    def __init__(self, embedding_fn, 
                file_path, content_column:str, metadata_columns:List[str], batch_size:int=500):
        self.embedding_fn = embedding_fn
        self.file_path= file_path
        self.content_column = content_column
        self.metadata_columns = metadata_columns
        self.batch_size = batch_size
        self.documents = None
        self.vectorstore = None
    
    def __call__(self):
        self._load()
        self._create_pgvector_store()
        self._add_documents_to_pgvector()
        
    def _load(self) -> None:
        documents = CustomCSVLoader(
            file_path= self.file_path, 
            content_column=self.content_column, 
            metadata_columns=self.metadata_columns)
        self.documents  = documents.load()
        
    def _create_pgvector_store(self) -> None:
        """PGVector 스토어 생성"""
        self.vectorstore = CustomPGVector( 
                            embedding_fn=self.embedding_fn)
        return self.vectorstore

    def _add_documents_to_pgvector(self) -> None:
        """문서를 PGVector에 추가"""
        # add_documents 메서드로 문서 추가
        total_doc = len(self.documents)
        for i in range(0, total_doc, self.batch_size):
            batch = self.documents[i:i + self.batch_size]
            self.vectorstore.add_documents(batch)
        print(f'{total_doc}개 적재 완료')