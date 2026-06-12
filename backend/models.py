from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    bills = relationship("BillRecord", back_populates="owner", cascade="all, delete-orphan")


class BillRecord(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    total_amount = Column(Float)
    tip_percentage = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    owner = relationship("User", back_populates="bills")
    items = relationship("ItemRecord", back_populates="bill", cascade="all, delete-orphan")


class ItemRecord(Base):
    __tablename__ = "bill_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    consumers = Column(String, nullable=False)  # comma-separated names
    bill_id = Column(Integer, ForeignKey("bills.id", ondelete="CASCADE"), nullable=False)

    bill = relationship("BillRecord", back_populates="items")