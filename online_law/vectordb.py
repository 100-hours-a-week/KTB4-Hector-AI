import os
import hashlib
import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, UnstructuredHTMLLoader

load_dotenv()
DOCS_DIR=os.getenv("DOCS_DIR", "./data")
CHROMA_PERSIST_DIR=os.getenv("CHROMA_PERSIST_DIR", "./chroma_persist")
MANIFEST_PATH=os.getenv("MANIFEST_PATH","./chroma_persist_manifest.json")

def file_hash(path: Path)->str:
    """파일 내용 기반 해시. 파일이 바뀌었는지 감지하는 용도."""
    h=hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()

def load_manifest() -> dict:
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_manifest(manifest: dict)->None:
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def load_pdf_docs(path: Path, doc_type:str) -> list[Document]:
    loader=PyPDFLoader(str(path))
    pages=loader.load()
    for page in pages:
        page.metadata["source"]=str(path)
        page.metadata["doc_type"]=doc_type
    return pages

def load_html_docs(path: Path, doc_type:str) -> list[Document]:
    loader=UnstructuredHTMLLoader(str(path))
    loaded=loader.load()
    for doc in loaded:
        doc.metadata["source"]=str(path)
        doc.metadata["doc_type"]=doc_type
    return loaded

def collect_files(docs_dir: str)->list[tuple[Path, str]]:
    """(파일 경로, doc_type) 튜플 리스트를 변환."""
    files=[]
    for doc_type, sub in[("law","law"),("case","case")]:
        sub_dir=Path(docs_dir)/sub
        if not sub_dir.is_dir():
            continue
        files+=[(p,doc_type) for p in sub_dir.rglob("*.pdf")]
        files+=[(p, doc_type) for p in sub_dir.rglob("*.html")]
    return files

def build_embeddings():
    return HuggingFaceEmbeddings(
        model_name="jhgan/ko-sroberta-multitask"
    )

def build_vectorstore(docs_dir:str=DOCS_DIR, persist_directory: str=CHROMA_PERSIST_DIR):
    embeddings=build_embeddings()
    vectorstore=Chroma(
        embedding_function=embeddings,
        persist_directory=persist_directory,
    )
    manifest=load_manifest()
    current_files=collect_files(docs_dir)
    splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

    new_or_changed=[]
    for path, doc_type in current_files:
        h=file_hash(path)
        key=str(path)
        if manifest.get(key)!=h:
            new_or_changed.append((path,doc_type,h))
    if not new_or_changed:
        print("변경된 파일 없음. 기존 Chroma DB 사용")
        return vectorstore
    print(f"신규/변경 파일 {len(new_or_changed)}개 감지, 증분 인덱싱 시작")
    for path, doc_type, h in new_or_changed:
        vectorstore.delete(where={"source": str(path)})
        if path.suffix==".pdf":
            docs=load_pdf_docs(path, doc_type)
        else:
            docs=load_html_docs(path, doc_type)
        split_docs=splitter.split_documents(docs)
        if split_docs:
            vectorstore.add_documents(split_docs)
        print(f"  - {path.name}: {len(split_docs)} chunk 추가 완료")
        manifest[str(path)]=h
    save_manifest(manifest)
    print("Chroma DB 증분 업데이트 완료")
    return vectorstore
if __name__=="__main__":
    build_vectorstore()