from typing import Any, Dict, List, Optional, Tuple
import json

from psycopg2.extras import Json
import psycopg2

from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document

class Singleton(type(VectorStore)):
    _instances: Dict[type, VectorStore] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class CustomPGVector(VectorStore, metaclass=Singleton):
    def __init__(self, conn_str, embedding_fn, table: str = "medical_table"):
        self.conn_str = conn_str
        self.conn = psycopg2.connect(self.conn_str)
        self.embedding_fn = embedding_fn
        self.table = table

    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding_fn,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        conn_str: str = None,
        table: str = "medical_db",
        **kwargs,
    ):
        store = cls(conn_str=conn_str, embedding_fn=embedding_fn, table=table)
        store.add_texts(texts, metadatas=metadatas)
        return store

    def add_texts(self,texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None,) -> None:
        metadatas = metadatas or [{} for _ in texts]
        embeddings = self.embedding_fn.embed_documents(texts)

        with self.conn.cursor() as cur:
            for text, emb, meta in zip(texts, embeddings, metadatas):
                cur.execute(
                    f"""
                    INSERT INTO {self.table} (content, embedding, metadata)
                    VALUES (%s, %s, %s)
                    """,
                    (text, emb, Json(meta)),
                )
        self.conn.commit()

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        query_emb = self.embedding_fn.embed_query(query)
        params: List[Any] = []

        sql_query_template = f"""
            SELECT content, metadata
            FROM {self.table}
        """

        where_clauses: List[str] = []
        if filter:
            filter_json = json.dumps(filter)
            where_clauses.append("metadata @> %s::jsonb")
            params.append(filter_json)

        if where_clauses:
            sql_query_template += " WHERE " + " AND ".join(where_clauses)

        sql_query_template += """
            ORDER BY embedding <#> %s::vector
            LIMIT %s
        """
        params.append(query_emb)
        params.append(k)

        with self.conn.cursor() as cur:
            cur.execute(sql_query_template, tuple(params))
            rows = self.__get_unique_documents(cur.fetchall())

        return [Document(page_content=row[0], metadata=row[1]) for row in rows]

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Document, float]]:
        """
        주어진 query를 임베딩 후 유사도 검색 수행.
        filter가 주어지면 metadata JSONB 조건(@>)을 SQL에 추가.
        """
        query_emb = self.embedding_fn.embed_query(query)

        # 기본 SQL
        base_sql = f"""
            SELECT content, metadata, (1-(embedding <#> %s::vector)) AS score
            FROM {self.table}
        """

        # 필터가 있으면 WHERE 절 추가
        params = [query_emb]
        where_clauses = []
        if filter:
            for key, val in filter.items():
                where_clauses.append(f"metadata @> %s::jsonb")
                params.append(json.dumps({key: val}))

        if where_clauses:
            base_sql += " WHERE " + " AND ".join(where_clauses)

        base_sql += " ORDER BY score DESC LIMIT %s"
        params.append(k)

        with self.conn.cursor() as cur:
            cur.execute(base_sql, tuple(params))
            rows = self.__get_unique_documents(cur.fetchall())

        return [
            (Document(page_content=row[0], metadata=row[1]), float(row[2]))
            for row in rows
        ]


    @staticmethod
    def __get_unique_documents(rows: List[Tuple[Any, ...]]) -> List[Tuple[Any, ...]]:
        unique_contents = set()
        unique_documents = []

        for row in rows:
            content = row[0]
            if content not in unique_contents:
                unique_contents.add(content)
                unique_documents.append(row)

        return unique_documents
