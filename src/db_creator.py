from models import (ENGINE, Base, PostInfoModel, PostInfoModelComp,
                    PostInfoModelComp1)


def create_db():
    Base.metadata.create_all(ENGINE)
