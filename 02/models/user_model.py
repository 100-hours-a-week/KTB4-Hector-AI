from sqlalchemy import BigInteger, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

#user테이블 매핑
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    created_at: Mapped[str] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
