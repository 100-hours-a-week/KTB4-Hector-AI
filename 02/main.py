from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from routers.user_router import router as user_router
from routers.post_router import router as post_router
from routers.comment_router import router as comment_router
from routers.ai_router import router as ai_router

app = FastAPI(
    title="Simple Community API",
    version="0.4.0",
    summary="MySQL + Ollama(gemma2) 연동 커뮤니티 서버",
)


@app.get("/")
def root():
    return {"message": "FastAPI server is running"}


@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).scalar()
    return {"db_connected": result == 1}


app.include_router(user_router)
app.include_router(post_router)
app.include_router(comment_router)
app.include_router(ai_router)
