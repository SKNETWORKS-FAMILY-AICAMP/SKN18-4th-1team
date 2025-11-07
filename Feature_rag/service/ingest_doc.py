
from dotenv import load_dotenv
import os
from Langgraph.utils import set_embedding_model
from Langgraph.Rag.custom_ingest import VectorIngest 

def main():
    load_dotenv()
    VectorIngest(
        conn_str = os.getenv("CONNECTION_STRING"),
        embedding_fn = set_embedding_model(),
        file_path = "./Data/output_data_resume.csv",
        content_column = "content",
        metadata_columns = ["disease_name", "domain"]
    )()

if __name__ == "__main__":
    main()