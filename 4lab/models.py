from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)

    products = relationship("Product", back_populates="store", cascade="all, delete")

    __table_args__ = (
        UniqueConstraint('name', 'address', name='_store_name_address_uc'),
    )

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"))

    store = relationship("Store", back_populates="products")