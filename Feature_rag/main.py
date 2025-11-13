from dotenv import load_dotenv
from langgraph_structure.graph import create_graph_flow


def main():
    question="나 배가 콕콕 누가 찌르는 느낌이 나"
    region = "서울특별시 강남구"
    app = create_graph_flow()
    
    answer = app.invoke({"question": question, "region": region})

    print(answer.get("final_answer", ""))

if __name__ == "__main__":
    load_dotenv()
    main()