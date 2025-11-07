-- pgvector 확장 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 법률 판례 문서 테이블 생성
CREATE TABLE IF NOT EXISTS medical_table (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,              -- 의료 지식
    embedding VECTOR(3072),              -- 임베딩 모델의 차원
    metadata JSONB NOT NULL,            --  메타데이터 (category)
    created_at TIMESTAMP DEFAULT NOW()  -- 생성 시간
);
