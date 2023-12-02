##### Openai Assistants API를 파이썬 코드로 활용하는 방법 복습
2023년 12월 2일 유튜버 [조코딩](https://youtube.com/@jocoding?si=a-vUWSv1NkJZFxS7) 채널에서 진행한 과정입니다.\
\
[Open AI assistants](https://platform.openai.com/assistants)의 Playground에서 사용 가능한 챗봇을 API로 다른 환경에서도 구현할 수 있습니다.

0. load_dotenv을 활용하여 .env에 저장되어 있는 **OPENAI_API_KEY**을 불러와서 client에 저장한다.

```python
# .env 파일
# OPENAI_API_KEY = ''
```

```python
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()
API_KEY = os.environ['OPENAI_API_KEY']

client = OpenAI(api_key = API_KEY)
```

1. assistant 생성
- Name 설정
- Instruction 설정
- tools 설정(code_interpreter: 코드해석 기능, Retrival: 파일첨부 기능),
- Model 설정\
\
을 저장해준다.

```python
assistant = client.beta.assistants.create(
    name="Math Tutor2",
    instructions="You are a personal math tutor. Write and run code to answer math questions.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4-1106-preview"
)
print(assistant)
```

```
Assistant(id='asst_uX1OdfuUfR3x2FqewdKBQkLi', created_at=1701530972, description=None, file_ids=[], instructions='You are a personal math tutor. Write and run code to answer math questions.', metadata={}, model='gpt-4-1106-preview', name='Math Tutor2', object='assistant', tools=[ToolCodeInterpreter(type='code_interpreter')])

```

위 output처럼 과정 마다 각 과정의 id가 생성되는데 이를 저장해뒀다가 계속 활용해야 한다.

```python
assistant_id='asst_uX1OdfuUfR3x2FqewdKBQkLi'
```

2. thread 생성

```python
thread = client.beta.threads.create()
print(thread)
```

```
Thread(id='thread_P6bPb2wCNnVr3lBwi5lFG7Xx', created_at=1701531126, metadata={}, object='thread')

```

```python
thread_id='thread_P6bPb2wCNnVr3lBwi5lFG7Xx'
```

3. Message 생성
   
   - thread_id 입력
   - role 설정 (현재 beta 버전은 user밖에 못쓴다.)
   - content 입력 (assistant에 건낼 질문)

```python
message = client.beta.threads.messages.create(
    thread_id= 'thread_TmnqD8JmqMZgxeHVMxKRib4l',
    role="user", 
    content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
)
print(message)
```

```
ThreadMessage(id='msg_WyyE7tIW7FcjBhj2z1gOej5L', assistant_id=None, content=[MessageContentText(text=Text(annotations=[], value='I need to solve the equation `3x + 11 = 14`. Can you help me?'), type='text')], created_at=1701531246, file_ids=[], metadata={}, object='thread.message', role='user', run_id=None, thread_id='thread_TmnqD8JmqMZgxeHVMxKRib4l')

```

```python
ThreadMessage_id='msg_WyyE7tIW7FcjBhj2z1gOej5L'
```

4. Run 실행 : 질문에 대한 답변을 주는 과정

- client.beta.threads.runs.create
  
  - thread_id 설정
  - assistant_id 설정
  - instructions 설정 (그냥 추가 설정...)

```python
run = client.beta.threads.runs.create(
  thread_id= thread_id,
  assistant_id= assistant_id,
  instructions="Please address the user as Jane Doe. The user has a premium account."
)
print(run) # status='queued' 에서 status='completed' 되야 완료
```

```
Run(id='run_CRiKmmQkQF1AYFbzvb3gNA3F', assistant_id='asst_uX1OdfuUfR3x2FqewdKBQkLi', cancelled_at=None, completed_at=None, created_at=1701531485, expires_at=1701532085, failed_at=None, file_ids=[], instructions='Please address the user as Jane Doe. The user has a premium account.', last_error=None, metadata={}, model='gpt-4-1106-preview', object='thread.run', required_action=None, started_at=None, status='queued', thread_id='thread_P6bPb2wCNnVr3lBwi5lFG7Xx', tools=[ToolAssistantToolsCode(type='code_interpreter')])

```

```python
run_id = 'run_CRiKmmQkQF1AYFbzvb3gNA3F'
```

5. Run 재실행

- 위 output을 보면 **status='queued'** 임을 알 수 있다. 이는 run이 아직 완료되지 않았다는 것이다.

- run을 재확인하여 **status='completed'** 가 됨을 확인하고 다음 단계로 넘어가야 한다.

- client.beta.threads.runs.retrieve
  
  - thread_id 설정
  - run_id 설정

```python
run = client.beta.threads.runs.retrieve(
  thread_id= thread_id,
  run_id= run_id
)
print(run)
```

```
Run(id='run_CRiKmmQkQF1AYFbzvb3gNA3F', assistant_id='asst_uX1OdfuUfR3x2FqewdKBQkLi', cancelled_at=None, completed_at=1701531487, created_at=1701531485, expires_at=None, failed_at=None, file_ids=[], instructions='Please address the user as Jane Doe. The user has a premium account.', last_error=None, metadata={}, model='gpt-4-1106-preview', object='thread.run', required_action=None, started_at=1701531485, status='completed', thread_id='thread_P6bPb2wCNnVr3lBwi5lFG7Xx', tools=[ToolAssistantToolsCode(type='code_interpreter')])

```

위 output 결과 **status='completed'** 로 변했음을 확인할 수 있다.

6. 답변 확인

- 이제 질문에 대답을 듣기 위한 마지막 메세지가 출력되도록 해준다.

- messages의 구성요소 안에서 실제 대답 데이터인 value값의 경로를 찾아준다.

- client.beta.threads.messages.list
  - thread_id 설정

```python
messages = client.beta.threads.messages.list(
  thread_id= thread_id
)
print(messages.data[0].content[0].text.value)
```

```
Hello Jane Doe! How can I assist you today? If you have any questions or need help with something, feel free to let me know.

```

run에서 설정한 instructions 때문에 처음 대답이 위와 같이 나왔다. 이제 다시 수학 질문을 재질문하면 풀이 답변을 받을 수 있다.

이제 해당 과정을 이용하여 저작권 완료 소설을 이용하고, tools의 Retrival을 이용하여 소설 기반 챗봇 api를 생성할 수 있습니다.