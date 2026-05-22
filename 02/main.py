from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from routers.user_router import router as user_router
from routers.post_router import router as post_router

app = FastAPI(
    title="Simple Community API",
    version="0.3.0",
    summary="MySQL 연동 커뮤니티 서버",
)

#서버 확인
@app.get("/")
def root():
    return {"message": "FastAPI server is running"}

#DB연결 체크
@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).scalar()
    return {"db_connected": result == 1}

#라우터 등록
app.include_router(user_router)
app.include_router(post_router)
