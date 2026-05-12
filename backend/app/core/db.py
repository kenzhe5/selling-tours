from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from .config import settings

connect_args: dict = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.database_url, connect_args=connect_args, echo=False)


def init_db() -> None:
    from ..models import booking, tour  # noqa: F401  (register metadata)

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
