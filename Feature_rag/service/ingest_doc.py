
from dotenv import load_dotenv
from langgraph_structure.utils import set_conn_str, set_embedding_model
from langgraph_structure.Rag.custom_ingest import VectorIngest 
def main():
    load_dotenv()
    VectorIngest(
        conn_str = set_conn_str(),
        embedding_fn = set_embedding_model(),
        file_path = "./Data/output_data_resume.csv",
        content_column = "content",
        metadata_columns = ["disease_name", "domain"]
    )()

if __name__ == "__main__":
    main()