from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

# 인덱싱
print("문서 로딩 및 인덱싱 시작...")
from glob import glob

md_paths = sorted(glob(r"C:\Users\hojun\OneDrive\바탕 화면\07\notes\*.md"))
md_docs = []
for p in md_paths:
    md_docs.extend(TextLoader(p, encoding="utf-8").load())

docs = md_docs
print(f"로딩된 Document 수: {len(docs)}")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)
split_docs = splitter.split_documents(docs)
print(f"분할된 chunk 수: {len(split_docs)}")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)
vectorstore = Chroma.from_documents(split_docs, embeddings)

print("인덱싱 완료")
print("RAG 파이프라인 시작...")
retriever=vectorstore.as_retriever(search_kwargs={"k":3})
prompt=ChatPromptTemplate.from_messages([
    ("system",
     "다음 문서를 근거로 사용자 질문에 답하세요. "
     "근거가 부족하면 '주어진 자료에서는 확인할 수 없습니다.'라고 답하세요.\n\n"
     "{context}"),
    ("human", "{question}"),
])
def build_llm():
    provider=os.getenv("LLM_PROVIDER", "google").lower()
    print(f"LLM Provider: {provider}")
    if provider=="ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "gemma3:4b"),
            base_url=os.getenv("OLLAMA_BASE_URL","http://localhost:11434"),
        )
    return ChatGoogleGenerativeAI(
        model=os.getenv("GOOGLE_MODEL", "gemini-2.5-flash"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
llm=build_llm()
def format_docs(ds):
    return "\n\n".join(d.page_content for d in ds)
rag=(
    {"context": retriever | format_docs, "question":RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
print(rag.invoke("손흥민은 어떤 선수야?"))
print("RAG 파이프 라인 완료")
from langsmith.evaluation import evaluate
from langsmith import Client
DATASET_NAME="rag-eval-soccer"
client=Client()
EVAL_QUESTIONS=[
    {
        "question": "월드컵 초대 우승 국가는?",
        "answer":   "우르과이입니다.",
    },
    {
        "question": "손흥민은 어느 나라 사람이야?",
        "answer":   "손흥민은 대한민국 사람입니다.",
    },
    {
        "question": "메시는 발롱도르 몇번 받았어?",
        "answer":   "메시는 발롱도르를 8번 수상했습니다.",
    },
    {
        "question": "바르셀로나 최다 득점자는 누구야?",
        "answer":   "메시입니다.",
    },
    {
        "question": "한국의 월드컵 최고 성적은?",
        "answer":   "2002년 한국 월드컵에서 최고 성적 4강을 달성했습니다.",
    },
]
print(f"검증 질문 수: {len(EVAL_QUESTIONS)}")
existing=[d for d in client.list_datasets(dataset_name=DATASET_NAME)]
inputs=[{"question":ex["question"]} for ex in EVAL_QUESTIONS]
outputs=[{"answer": ex["answer"]}for ex in EVAL_QUESTIONS]
if existing:
    dataset=existing[0]
    print(f"기존 Dataset 사용:{dataset.id}")
else:
    dataset=client.create_dataset(
        dataset_name=DATASET_NAME,
        description="어댑터즈 RAG 답변 품질 평가용",
    )
    print(f"새 Dataset 생성: {dataset.id}")
    client.create_examples(
        dataset_id=dataset.id,
        inputs=inputs,
        outputs=outputs,
    )
    print(f"Example {len(EVAL_QUESTIONS)} 건 추가 완료")
loaded=client.read_dataset(dataset_name=DATASET_NAME)
examples=list(client.list_examples(dataset_id=loaded.id))
print(f"총 Example 수:{len(examples)}")
for ex in examples[:3]:
    print("Q:", ex.inputs["question"])
    print("A:", ex.outputs["answer"] if ex.outputs else "(없음)")
    print()
def target(inputs):
    return {"answer": rag.invoke(inputs["question"])}
def contains_expected_keyword(run, example):
    pred=run.outputs.get("answer","")
    expected=example.outputs.get("answer","")
    keywords=[w for w in expected.split() if len(w)>=2][:2]
    hit=all(k in pred for k in keywords)
    return {
        "key": "contains_expected_keyword",
        "score": 1 if hit else 0,
        "comment":f"필수 키워드 {keywords} 포함 여부",
    }
JUDGE_PROMPT=ChatPromptTemplate.from_messages([
    ("system",
     "당신은 답변 품질을 평가하는 채점자입니다.\n"
     "아래 기대 답변(reference)과 모델 답변(prediction)을 비교하고,\n"
     "의미가 일치하면 1, 부분적으로만 일치하면 0.5, 무관하면 0을 점수로 매기세요.\n"
     "응답은 반드시 첫 줄에 0/0.5/1 중 하나의 숫자만, 둘째 줄부터 짧은 이유를 적으세요."),
    ("human",
     "질문: {question}\n\n"
     "기대 답변: {reference}\n\n"
     "모델 답변: {prediction}"),
])
judge_chain=JUDGE_PROMPT | llm | StrOutputParser()
def llm_judge(run, example):
    reply=judge_chain.invoke({
        "question":example.inputs["question"],
        "reference":example.outputs["answer"],
        "prediction":run.outputs["answer"]
    })
    first_line=reply.strip().splitlines()[0].strip()
    try:
        score=float(first_line)
    except ValueError:
        score=0
    return {
        "key":"llm_judge_semantic_match",
        "score":score,
        "comment": reply,
    }
result=evaluate(
    target,
    data=DATASET_NAME,
    evaluators=[contains_expected_keyword, llm_judge],
    experiment_prefix="v1-baseline",
)
print(result)