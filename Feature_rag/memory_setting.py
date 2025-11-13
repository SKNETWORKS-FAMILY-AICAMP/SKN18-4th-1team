from langgraph.checkpoint.serde.encrypted import EncryptedSerializer
import psycopg2

# LANGGRAPH_AES_KEY를 이용해서 암호화 직렬 객체 생성 
serde = EncryptedSerializer.from_pycryptodome_aes()  # 암호화 직렬화기

