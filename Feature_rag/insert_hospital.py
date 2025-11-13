import pandas as pd
from dotenv import load_dotenv
load_dotenv()
import os
from sqlalchemy import create_engine


engine = create_engine(os.getenv("CONNECTION_STRING"))
#CSV 파일 읽기
df = pd.read_csv("./Data/hospital_full_info.csv")

#DB에 넣기 (테이블이 없으면 자동 생성)
df.to_sql("hospital_table", engine, if_exists="append", index=False)

print("✅ CSV → PostgreSQL 삽입 완료")
