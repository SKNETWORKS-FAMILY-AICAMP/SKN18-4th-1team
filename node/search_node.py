#####################################
# 환경변수 설정
#####################################
import os
from dotenv import load_dotenv

load_dotenv()

#####################################
# 랭체인 라이브러리 다운로드
#####################################
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_openai import ChatOpenAI

#########################
#  Loader 라이브러리
#########################
import pandas as pd

#####################################
# 사용자로부터
#####################################
user_input = []

def user_chat(user_input) -> str:
    '''사용자로부터 질문을 입력받음'''
    user_input = "왼쪽 무릎이 아파요."


file_path = "../data/disease_data/output_data_resume.csv"

df = pd.read_csv(file_path)

df.head()