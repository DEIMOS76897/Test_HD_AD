from datetime import date,time
from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Date, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


class User(Base):
    __tablename__='users'
    id:Mapped[int]=mapped_column(primary_key=True)
    tg_id:Mapped[int]=mapped_column(BigInteger,unique=True)
    user_name:Mapped[str]=mapped_column(String(100))
    role:Mapped[str]=mapped_column(String(20),default='user')

    records: Mapped[list["Record"]] = relationship(back_populates="user")

class Lesson(Base):
    __tablename__='lessons'
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(100),unique=True)

    records:Mapped[list["Record"]]=relationship(back_populates="lesson")

class Record(Base):
    __tablename__='records'
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey('users.id'))
    lesson_id:Mapped[int]=mapped_column(ForeignKey('lessons.id'))
    date:Mapped[date]=mapped_column(Date)
    time:Mapped[time]=mapped_column(Time)
    user:Mapped[User]=relationship(back_populates="records")
    lesson:Mapped[Lesson]=relationship(back_populates="records")
    __table_args__=(UniqueConstraint("lesson_id","date","time",name="uq_lesson_date_time"),)