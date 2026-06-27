### 실행 방법
```
uv sync
```
## baseline
```
uv run baseline.py
```
## main
```
uv run main.py
```
## 데이터

| 이름 | 내용 |
|---|---|
| son.md | 손흥민 내용 |
| messi.md | 메시 관련 내용 |
| worldcup.md | 월드컵 내용 |

## 구조
```
07/
├── .venv/
├── myenv/
├── notes/
│   ├── messi.md
│   ├── son.md
│   └── worldcup.md
├── .gitignore
├── baseline.py
├── main.py
├── pyproject.toml
└── uv.lock
```
### baseline
notes의 모든 .md 파일을 읽어 TextLoader로 로딩. RecursiveCharacterSplitter로 Chunk_size=500, overlap=50으로 쪼갬. 쪼갠 chunk들은 Gemini 임베딩으로 벡터화해서 Chroma 벡터 스토어에 저장
## LCEL 파이프 구조
```
rag = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt | llm | StrOutputParser()
)
```
입력 질문이 들어오면 retriever가 유사도 3개 chunk를 검색 -> RunnablePassthrough가 원본 질문을 그대로 question에 전달 -> 이 둘이 prompt에 들어가 llm이 답변 생성 -> StrOutputParser가 문자열 추출
## 평가
<img width="1677" height="235" alt="image" src="https://github.com/user-attachments/assets/2c66dbbc-3b8e-4e58-b887-193ba53e3cb5" />
<img width="1672" height="311" alt="image" src="https://github.com/user-attachments/assets/8c4f17db-e9f0-4430-9936-0c19e4a45e58" />
<img width="1677" height="308" alt="image" src="https://github.com/user-attachments/assets/4026f950-8305-4035-b148-785b00a0c0b0" />



