from dotenv import load_dotenv
from pathlib import Path
from langgraph_structure.graph import create_graph_flow


def main():
    question="나 배가 콕콕 누가 찌르는 느낌이 나"

    app = create_graph_flow()
    
    answer = app.invoke({"question": question})

    print(answer.get("final_answer", ""))

if __name__ == "__main__":
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
    main()