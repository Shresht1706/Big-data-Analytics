from models import (
    PostInfoModel,
    Base,
    ENGINE,
)


def create_db():
    Base.metadata.create_all(ENGINE)
