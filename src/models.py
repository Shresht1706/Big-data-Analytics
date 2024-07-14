from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from settings import settings

Base = declarative_base()
ENGINE = create_engine(settings.PG_DSN)


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PostInfoModel(Base):
    __tablename__: str = "post_info_model"
    id: Mapped[int] = mapped_column(  # type: ignore
        primary_key=True,
        unique=True,
        autoincrement=True,
    )
    content: Mapped[str] = mapped_column()
    author_nickname: Mapped[str] = mapped_column()
    author_name: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    views: Mapped[int] = mapped_column()
    likes: Mapped[int] = mapped_column()
    reposts: Mapped[int] = mapped_column()
    comments: Mapped[int] = mapped_column()


class PostInfoModelComp(Base):
    __tablename__: str = "post_info_model_comp"
    id: Mapped[int] = mapped_column(  # type: ignore
        primary_key=True,
        unique=True,
        autoincrement=True,
    )
    content: Mapped[str] = mapped_column()
    author_nickname: Mapped[str] = mapped_column()
    author_name: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    views: Mapped[int] = mapped_column()
    likes: Mapped[int] = mapped_column()
    reposts: Mapped[int] = mapped_column()
    comments: Mapped[int] = mapped_column()


class PostInfoModelComp1(Base):
    __tablename__: str = "post_info_model_comp1"
    id: Mapped[int] = mapped_column(  # type: ignore
        primary_key=True,
        unique=True,
        autoincrement=True,
    )
    content: Mapped[str] = mapped_column()
    author_nickname: Mapped[str] = mapped_column()
    author_name: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    views: Mapped[int] = mapped_column()
    likes: Mapped[int] = mapped_column()
    reposts: Mapped[int] = mapped_column()
    comments: Mapped[int] = mapped_column()
