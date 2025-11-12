-- pgvector 확장 활성화
CREATE EXTENSION IF NOT EXISTS vector;

-- 의료 문서 테이블 생성
CREATE TABLE IF NOT EXISTS medical_table (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,              -- 의료 지식
    embedding VECTOR(3072),              -- 임베딩 모델의 차원
    metadata JSONB NOT NULL,            --  메타데이터 (category)
    created_at TIMESTAMP DEFAULT NOW()  -- 생성 시간
);

-- 회원 테이블 생성
CREATE TABLE IF NOT EXISTS user_table (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()  -- 생성 시간
);

-- 회원 생성 시 기본 설문 테이블
-- 지병/성별/임신/흡연/비만
CREATE TABLE IF NOT EXISTS survey_table (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,           -- 회원 ID
    chronic_disease BOOLEAN,
    gender VARCHAR(10),
    pregnancy BOOLEAN,
    smoking BOOLEAN,
    height_cm INTEGER,
    weight_kg FLOAT,
    obesity BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()  -- 생성 시간
);