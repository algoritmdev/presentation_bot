from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)

class Presentation(Base):
    __tablename__ = "presentations"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    channel_msg_id = Column(Integer, nullable=False)

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    presentation_id = Column(Integer, ForeignKey("presentations.id"))
    status = Column(String, default="pending")
    used = Column(Boolean, default=False)
    payment_proof = Column(String, nullable=True)

    user = relationship("User")
    presentation = relationship("Presentation")
