#####################################
# 환경변수 설정
#####################################
import os
from dotenv import load_dotenv

load_dotenv()


#####################################
# 랭체인 라이브러리 다운로드
#####################################
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_openai import OpenAIEmbeddings
from tqdm import tqdm
from langchain_community.vectorstores import PGVector
import pandas as pd


#####################################
# 사용자로부터 질문 입력 받기
#####################################
def user_chat() -> str:
    '''사용자로부터 질문을 입력받음'''
    user_input = input("증상을 입력해주세요: ")
    return user_input


#####################################
# 질병 데이터셋 Load
#####################################
#file_path = "../data/disease_data/output_data_resume.csv"
file_path = '/Users/hwangmin-u/Desktop/minwoo_Hwang/Study/SK family AI Camp/Project/SKN18-4th-1team/Feature_rag/Data/output_data_resume.csv'
loader = CSVLoader(file_path, encoding="utf-8")
docs = loader.load()


#####################################
# Text Splitter로 청크 분할
#####################################
def text_split(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500, # 청크 크기 지정
        chunk_overlap=50, # 청크 간 중복되는 문자 수 설정
        length_function=len, # 문자열의 길이를 계산하는 함수 지정
        is_separator_regex=False, # 구분자로 정규식 사용여부 설정
        separators=[    #(옵션)한국어 문장 구분용 구분자 설정
            "\n\n",  # 문단
            "\n",
            r"(?<=[.?!])\s+",   # 영어 문장
            r"(?<=[다요죠음함임니다])[\.\?!]?\s+",   # 한국어 종결 표현
            " ",    # 단어
            "",     # 글자 단위로 나누기
        ]
    )
    docs_with_splitter = text_splitter.split_documents(docs)
    return docs_with_splitter


#####################################
# 임베딩 + PGVector 저장 통합 함수
#####################################
def embed_and_save_pgvector(docs_with_splitter):
    # DB 연결 정보
    CONNECTION_STRING = "postgresql+psycopg2://medical:medical1234@localhost:5432/medical_db"

    # 임베딩 모델
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

    # PGVector 초기화 (기존 collection에 계속 추가)
    vectorstore = PGVector(
        connection_string=CONNECTION_STRING,
        embedding_function=embeddings_model,
        collection_name="medical_vectors",
        pre_delete_collection=True  # 기존 medical_vectors 컬렉션 삭제 후 새로 생성
    )

    # 청크 저장
    saved_chunks = []

    # 진행률 표시하며 청크별 임베딩 + 저장
    for i, doc in tqdm(enumerate(docs_with_splitter), total=len(docs_with_splitter), desc="임베딩 및 DB 저장 중"):
        try:
            # 각 청크를 DB에 직접 추가 (자동으로 임베딩 수행)
            vectorstore.add_texts(
                texts=[doc.page_content],
                metadatas=[doc.metadata]
            )
            saved_chunks.append(doc.page_content)
        except Exception as e:
            print(f"{i}번째 청크 저장 실패: {e}")

    print(f"모든 청크 임베딩 및 PGVector 저장 완료! (총 {len(saved_chunks)}개 저장됨)")


#####################################
# 사용자 질문 임베딩
#####################################
def user_question_embedding():
    # 임베딩 모델 불러오기
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

    # 사용자 질문 입력
    user_query = user_chat()
    print("사용자 입력:", user_query)

    # 사용자 질문에 대한 임베딩 진행
    query_vector = embeddings_model.embed_query(user_query)
    print(f"{user_query} | 임베딩 완료, 차원: {len(query_vector)}")
    return user_query, query_vector


#####################################
# Pgvector에서 유사한 청크 검색(Top-k)
#####################################
def chunk_search(user_query: str, top_k: int = 5):
    '''PGVector DB에서 가장 유사한 청크 5개를 검색하는 함수'''
    
    # PostgreSQL 연결
    CONNECTION_STRING = "postgresql+psycopg2://medical:medical1234@localhost:5432/medical_db"

    # 임베딩 모델 설정
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

    # Pgvector 불러오기
    vectorstore = PGVector(
        connection_string=CONNECTION_STRING,
        embedding_function=embeddings_model,
        collection_name="medical_vectors"
    )

    # Pgvector에서 의미적으로 유사한 문서 검색
    similar_docs = vectorstore.similarity_search(
        query=user_query,
        k=top_k
    )

    return similar_docs


#####################################
# 전체 실행
#####################################
if __name__ == "__main__":
    # 청크 분할
    docs_with_splitter = text_split(docs)

    # 임베딩 & PGVector 저장 (최초 1회 실행 후 주석 처리)!!!!!!!!!
    # 최초 1회 실행 후 반드시!!!!!!!!!! 주석처리할 것
    # 주석 처리 안하고 재실행 시 데이터 임베딩부터 다시 시작함
    embed_and_save_pgvector(docs_with_splitter)

    # 사용자 질문 입력 및 임베딩
    user_query, _ = user_question_embedding()

    # Pgvector 검색
    results = chunk_search(user_query, top_k=5)

    # 검색 결과 출력
    print(f"\n '{user_query}' 에 대한 유사 청크 검색 결과\n")
    for i, doc in enumerate(results, start=1):
        print(f"--- [결과 {i}] ---")
        print(f"내용: {doc.page_content[:200]}...")
        print(f"메타데이터: {doc.metadata}\n")