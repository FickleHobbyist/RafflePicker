from sqlalchemy import create_engine, Column, Integer, ForeignKey, String, Date, DateTime, Sequence, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, validates, reconstructor
from sqlalchemy.sql import func
from raffle.db import Session
import pytz
import tzlocal


# engine = create_engine('sqlite:///raffle.db', echo=True)
engine = create_engine('sqlite:///:memory:', echo=True)
Session.configure(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    name = Column(String, primary_key=True)
    user_sales = relationship("Sale")

    @validates('name')
    def validate_name(self, key, name_):
        assert name_.startswith('@')
        return name_

    def __repr__(self):
        return f"<User(name={self.name}, user_sales={self.user_sales})>"


class Drawing(Base):
    __tablename__ = 'drawings'
    id = Column(Integer, Sequence('drawing_id_seq'), primary_key=True)
    date_drawn = Column(Date, nullable=True, default=None)
    sales = relationship("Sale")
    winners = relationship("Winner")

    def __repr__(self):
        return f"<Drawing(id={self.id}, date_drawn={self.date_drawn}, sales={self.sales}, winners={self.winners}"


class Winner(Base):
    __tablename__ = 'winners'
    id = Column(Integer, Sequence('winner_id_seq'), primary_key=True)
    drawing_id = Column(Date, ForeignKey('drawings.id'), nullable=False)
    user_name = Column(String, ForeignKey('users.name'), nullable=False)
    rank = Column(Integer, nullable=False)
    winnings = Column(Integer, nullable=False)
    dwg = relationship("Drawing", back_populates="winners")

    def __repr__(self):
        return f"<Winner(id={self.id}, date_drawn={self.date_drawn}, user_name={self.user_name}, winnings={self.winnings}"


class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, Sequence('sale_id_seq'), primary_key=True)
    user_name = Column(String, ForeignKey('users.name'))
    num_tickets = Column(Integer, nullable=False)
    prize_addition = Column(Boolean, nullable=False, default=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now(pytz.utc))
    drawing_id = Column(Integer, ForeignKey('drawings.id'), nullable=False)

    drawing = relationship("Drawing", back_populates="sales")
    user = relationship("User", back_populates="user_sales")

    @reconstructor
    def init_on_load(self):
        self.time_created = self.time_created.replace(tzinfo=pytz.utc).astimezone(tzlocal.get_localzone())

    def __repr__(self):
        return f"<Sale(id={self.id}, user_name={self.user_name}, num_tickets={self.num_tickets}, " \
               f"time={self.time_created})>"


Base.metadata.create_all(engine)
