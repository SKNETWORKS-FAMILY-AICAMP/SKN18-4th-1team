import pandas as pd
from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader

class CustomCSVLoader(BaseLoader):
    def __init__(self, file_path, content_column, metadata_columns, encoding="utf-8", na_fill=""):
        self.file_path = file_path
        self.content_column = content_column
        self.metadata_columns = metadata_columns
        self.encoding = encoding
        self.na_fill = na_fill

    def load(self) -> list[Document]:
        # pandas로 CSV 읽기
        df = pd.read_csv(self.file_path, encoding=self.encoding).fillna(self.na_fill)
        
        docs = []
        for _, row in df.iterrows():
            # page_content: 지정된 컬럼 문자열 생성 
            page_content = str(row[self.content_column])
            # metadata: 지정된 컬럼들만 선택
            metadata = {col: row[col] for col in self.metadata_columns if col in df.columns}
            docs.append(Document(page_content=page_content, metadata=metadata))

        return docs
    
    
