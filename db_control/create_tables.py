from .mymodels import Base  # User, Comment
from .connect import engine

import platform

def init_db():
    print(platform.uname())
    print("Creating tables >>> ")
    Base.metadata.create_all(bind=engine)
