import pandas as pd
from sqlalchemy import create_engine
from langgraph_structure.utils import set_conn_str

engine = create_engine(set_conn_str())
# CSV 파일 읽기
df = pd.read_csv("./Data/hospital_full_info.csv")

# DB에 넣기 (테이블이 없으면 자동 생성)
df.to_sql("hospital_table", engine, if_exists="append", index=False)

print("✅ CSV → PostgreSQL 삽입 완료")
