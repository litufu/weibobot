from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func,Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()
engine = create_engine('sqlite:///weibo.sqlite?check_same_thread=False')


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    uid = Column(String)
    send = Column(Boolean)


Base.metadata.create_all(engine)