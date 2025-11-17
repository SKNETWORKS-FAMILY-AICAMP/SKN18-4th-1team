from dotenv import load_dotenv
from mediscope.langgraph_structure.graph import create_graph_flow
from mediscope.langgraph_structure.utils import pool
load_dotenv()
def summarize_survey_result(result):
    if result['gender'] == 0:
        gender = "남자"
    else:
        gender = "여자"
        
    if result['is_prgnand']==0:
        is_prgnand = '임신을 하지 않음'
    else:
        is_prgnand= '임신 하고 있음'

    survey_surmmarize = f'''
        나이는 {result['age']}세이고, {gender}이고, BMI는 {result['bmi_category']},
        {is_prgnand}이며, 기저질환은 {result['prexisting_conditions']} 입니다.
    '''   
    
    return survey_surmmarize 

def survey_preprocessing(user_id,question):
    conn = pool.getconn()
    user = user_id

    try:
        with conn.cursor() as cur:
            sql = f'''SELECT age, gender, is_prgnand, prexisting_conditions, address, bmi, bmi_category 
                FROM survey_response
                WHERE user_id = %s;
                '''
            cur.execute(sql, (user,))
            survey_result = cur.fetchone()
            survey_surmmarize, region = summarize_survey_result(survey_result) 
            if survey_surmmarize:
                app = create_graph_flow()
                answer = app.invoke({
                    'question': question,
                    'region': region,
                    'survey_result': survey_surmmarize   
                    })
                # print(answer.get("final_answer", ""))
                # print(answer.get("surmmarizer", ""))
                # 결과 django에서 사용...
            else:
                raise ValueError(f"[ERROR] 사용자의 설문 데이터가 존재하지 않습니다.")
                
    except Exception as e:
        print(f"❌ survey 정보 가져오기 실패: {e}")

    finally:
        pool.putconn(conn)

'''
1. 증상 안내
눈이 뻑뻑하고 침침해요.
사용자는 35세 여자이며, 임신 중이 아니며, BMI 정상, 기저질환 없음.

2. 병원 추천
귀에서 삐— 소리가 계속 들려요. 어느 병원 가야하나요?
사용자는 40세 여자이며, BMI 정상, 기저질환 없음.

3. survey 가 반영되어 증상에 대한 안내가 나오는 문구
- 예시 문장
question : 배 아래쪽이 아프고 뭔가 묵직해요.
survey_result : 사용자는 34세이고, 여자이고, 임신중이며, 기저질환은 없습니다.
------
question : 발이 자주 저리고 따끔거려요.
survey_result : 사용자는 56세 남자이며, BMI 비만이며, 당뇨가 있습니다.

4. 제공되는 서비스가 아닌 것
- 오늘 날씨 왜 이렇게 덥지?

'''