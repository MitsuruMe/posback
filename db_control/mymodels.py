from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.mysql import CHAR, VARCHAR, INTEGER, TIMESTAMP
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = 'product_master'

    prd_id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(CHAR(13), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    price: Mapped[int] = mapped_column(INTEGER, nullable=False)

class Transaction(Base):
    __tablename__ = 'transaction'

    trd_id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    datetime: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    emp_cd: Mapped[str] = mapped_column(CHAR(10), nullable=False)
    store_cd: Mapped[str] = mapped_column(CHAR(5), nullable=False, default='30')
    pos_no: Mapped[str] = mapped_column(CHAR(3), nullable=False, default='90')
    total_amt: Mapped[int] = mapped_column(INTEGER, nullable=False)

    __table_args__ = (
        CheckConstraint("store_cd = '30'", name='chk_store_cd_fixed'),
        CheckConstraint("pos_no = '90'", name='chk_pos_no_fixed'),
    )

class TransactionDetail(Base):
    __tablename__ = 'transaction_detail'

    trd_id: Mapped[int] = mapped_column(INTEGER, ForeignKey('transaction.trd_id'), primary_key=True)
    dtl_id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    prd_id: Mapped[int] = mapped_column(INTEGER, ForeignKey('product_master.prd_id'), nullable=False)
    prd_code: Mapped[str] = mapped_column(CHAR(13), nullable=False)
    prd_name: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    prd_price: Mapped[int] = mapped_column(INTEGER, nullable=False)

    __table_args__ = (
        UniqueConstraint('trd_id', 'dtl_id', name='pk_transaction_detail'),
    )
