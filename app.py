from dotenv import load_dotenv
import os
from openai import OpenAI
import streamlit as st
import time

load_dotenv()
API_KEY = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key = API_KEY)

# thread_id를 하나로 관리
# thread_id 저장소
# 없을 때만 저장 가능하니 하나만 저장 가능
if 'thread_id' not in st.session_state:
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id

#thread_id, assistant_id 설정
thread_id = st.session_state.thread_id
# thread_id = 'thread_NFNLsJy9ZB8JlTBb7mcO65uP' # 현진건2에서 직접 복사해옴
# 미리 만들어둔 assistant
assistant_id = 'asst_6a4Ke67NGPdvwAa9t91WVqs4'

# 메세지 모두 불러오기
thread_messages = client.beta.threads.messages.list(thread_id, order="asc") # order='asc'로 역순으로 설정, 안하면 답변과 질문 순서 바뀜.

# 페이지 제목
st.header('현진건 작가님과의 대화')

# 메제시 가져와서 UI에 뿌려주기
for msg in thread_messages.data:
    # 채팅 추가
    with st.chat_message(msg.role):
        st.write(msg.content[0].text.value) # text 뽑는 경로

# 입력창에 입력을 받아서 입력된 내용으로 메세지 생성
prompt = st.chat_input("물어보고 싶은 것을 입력하세요!")
if prompt:
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt # 입력 받은 내용을 prompt로
    )
    # 입력한 메세지에 UI 표시
    with st.chat_message(message.role): # 새로 만든 메시지의 롤
        st.write(message.content[0].text.value) # 새로 만든 메세지의 value

    # RUN을 돌리는 과정
    run = client.beta.threads.runs.create(
        thread_id= thread_id,
        assistant_id= assistant_id
        # ,instructions= '최근 5개의 대화 내용을 기반으로 답변을 해줘' # 비용이 부담될 경우? 참조 내용이 넓어질 수록 비용 증가 우려
    )
    # 질문과 답변 사이 버퍼링 표시
    with st.spinner('응답 기다리는 중...'):
        # run이 completed될 때까지 확인
        while run.status != "completed":
            time.sleep(1.0) # 1.0초마다 반복해서 상태 체크 (너무 간격 좁으면 오류 발생하는 경우 있다.)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id= run.id #run은 항상 있으니 바로 뽑아옴
                )
    # 위 while문 빠져나왔다는건 완료됐다는거니 답변 메세지 불러오기
    messages = client.beta.threads.messages.list(
            thread_id=thread_id
            )
    # 마지막 답변 메세지 UI에 추가하기
    with st.chat_message(messages.data[0].role):
        st.write(messages.data[0].content[0].text.value) 

    

