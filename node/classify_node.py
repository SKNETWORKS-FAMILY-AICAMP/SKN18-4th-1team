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
    당신은 사용자의 질문을 받아서 해당 입력이 의료질문인지 아닌지 판단해주는 전문가입니다.
    해당 질문이 의료질문이면 'Yes'라고 답변하고 그렇지 않으면 'No'라고 답변해주면 됩니다.
    """),
    HumanMessagePromptTemplate.from_template("사용자의 질문이 의료질문입니까?: {treatment}")
])

prompt.input_variables

##############################
# chain 제작
##############################
chain = prompt | llm | StrOutputParser()

##############################
# 결과 확인
##############################
result = chain.invoke({"treatment": "인생어렵다 정말."})

print(result)