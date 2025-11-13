import os
import hashlib

def generate_aes256_key(seed: str) -> str:
    return hashlib.sha256(seed.encode()).hexdigest()

# 개발 환경 기본 seed
seed = "Development"

# 운영환경이면 외부 환경변수 기반 Seed 사용
if os.getenv("ENV") == "Production":
    seed = os.getenv("SECRET_SEED", "your_prod_seed")

aes_key = generate_aes256_key(seed)

# 환경 변수 등록
os.environ["LANGGRAPH_AES_KEY"] = aes_key

print("AES-256 Key 생성 및 환경변수 등록 완료.")
print(aes_key) 


# 암호화 목적
# 건강정보, 금융 정보 등 민감한 데이터를 안전하게 저장하고 전송하기 위해 AES-256 암호화 알고리즘을 사용합니다.  
