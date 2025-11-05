##############################
# 환경변수 세팅
##############################
import os
from dotenv import load_dotenv

load_dotenv()

##############################
# 라이브러리 세팅
##############################
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

##############################
# LLM
##############################
llm = ChatOpenAI(
    model="gpt-5-mini",
    temperature=1 # mini 모델은 온도값 1만 지원
)

##############################
# prompt
##############################
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="""
    당신은 환자가 말하는 증상을 듣고 어느 진료과에서 진료가 필요한지 판단해주는 전문적인 의사입니다.
    답변을 할때에는 길게 이야기하지 않고 해당 진료과만 알려줍니다. 가령 '내과', '외과' 이런 식으로 답변합니다.
    """),
    HumanMessagePromptTemplate.from_template("환자의 증상을 듣고 적절한 진료과를 말해주세요: {treatment}")
])

prompt.input_variables

##############################
# chain 제작
##############################
chain = prompt | llm | StrOutputParser()

##############################
# 결과 확인
##############################
result = chain.invoke({"treatment": "목구멍이 너무 따갑고 물을 마실때마다 목이 아프며, 열이 나는 것 같아요."})

print(result)