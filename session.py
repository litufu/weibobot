from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from database import Base

engine = create_engine('sqlite:///weibo.sqlite?check_same_thread=False')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
Session = scoped_session(DBSession)
session = Session()
