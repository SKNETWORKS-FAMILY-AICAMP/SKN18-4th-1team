
from dotenv import load_dotenv
load_dotenv()
from langgraph_structure.utils import set_embedding_model
from langgraph_structure.Rag.custom_ingest import VectorIngest 


def main():
    
    VectorIngest(
        embedding_fn = set_embedding_model(),
        file_path = ".\Data\merged_with_domain.csv",
        content_column = "content",
        metadata_columns = ["domain", "source_spec"]
    )()

if __name__ == "__main__":
    main()
