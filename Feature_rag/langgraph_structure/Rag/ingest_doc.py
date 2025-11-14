from dotenv import load_dotenv
import os

# 스크립트 실행 위치 기준 두 단계 상위 폴더
root_path = os.path.abspath(os.path.join(os.getcwd(), "..", ".."))
load_dotenv(os.path.join(root_path, ".env"))


from langgraph_structure.utils import set_embedding_model
from langgraph_structure.Rag.custom_ingest import VectorIngest 


def main():
    
    VectorIngest(
        embedding_fn = set_embedding_model(),
        file_path = ".\Data\disease.csv",
        content_column = "content",
        metadata_columns = ["disease_name", "domain", "source_spec"]
    )()

if __name__ == "__main__":
    main()
