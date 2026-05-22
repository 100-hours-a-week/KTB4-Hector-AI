from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
#DB 접속 주소
DATABASE_URL = "mysql+pymysql://root:hojune0701!@localhost:3306/community_app?charset=utf8mb4"
#DB연결 객체 생성
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)
#세션 생성기
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

#요청이 들어오면 세션을 열고 API에 전달
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
