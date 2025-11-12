import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from dotenv import load_dotenv
load_dotenv()
from langgraph_structure.utils import set_embedding_model,close_pool
from langgraph_structure.Rag.custom_ingest import VectorIngest 


def main():
    
    VectorIngest(
        embedding_fn = set_embedding_model(),
        file_path = "./Data/disease.csv",
        content_column = "content",
        metadata_columns = ["disease_name", "domain", "source_spec"]
    )()

if __name__ == "__main__":
    try:
        main()
    except:
        close_pool()