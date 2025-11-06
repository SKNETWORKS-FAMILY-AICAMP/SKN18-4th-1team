from pathlib import Path
import sys
from dotenv import load_dotenv
sys.path.append(str(Path(__file__).resolve().parents[1]))
from Langgraph.graph import create_graph_flow


def main():
    question="나 배가 콕콕 누가 찌르는 느낌이 나"

    app = create_graph_flow()
    
    answer = app.invoke({"question": question})

    print(answer.get("final_answer", ""))

if __name__ == "__main__":
    load_dotenv()
    main()