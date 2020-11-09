from sqlalchemy import create_engine, Column, Integer, ForeignKey, String, DateTime, Sequence, Boolean
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import relationship, validates, reconstructor
from sqlalchemy.sql import func
from raffle.db import Session
import pytz
import tzlocal


# engine = create_engine('sqlite:///raffle.db', echo=True)
engine = create_engine('sqlite:///:memory:', echo=True)
Session.configure(bind=engine)


name_length_limit = 25  # ESO specifies names can be up to 25 chars long


@as_declarative()
class Base:

    def asdict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(name_length_limit), nullable=False, unique=True)
    sales = relationship("Sale")
    wins = relationship("Winner")

    @validates('name')
    def validate_name(self, key, name_):
        assert name_.startswith('@')
        return name_

    def __repr__(self):
        n_sales = len(self.sales) if self.sales is not None else 0
        n_wins = len(self.wins) if self.wins is not None else 0
        return f"<User(name={self.name}, {n_sales} sale(s), {n_wins} win(s))>"


class Drawing(Base):
    __tablename__ = 'drawings'
    id = Column(Integer, Sequence('drawing_id_seq'), primary_key=True)
    date_started = Column(DateTime(timezone=True), nullable=False, server_default=func.now(pytz.utc))
    date_drawn = Column(DateTime(timezone=True), nullable=True, default=None)
    sales = relationship("Sale")
    winners = relationship("Winner")

    def __repr__(self):
        n_sales = len(self.sales) if self.sales is not None else 0
        n_winners = len(self.winners) if self.winners is not None else 0
        return f"<Drawing(id={self.id}, date_started={self.date_started}, date_drawn={self.date_drawn}, " \
               f"{n_sales} sale(s), {n_winners} winner(s)"

    @reconstructor
    def init_on_load(self):
        self.date_started = self.date_started.replace(tzinfo=pytz.utc).astimezone(tzlocal.get_localzone())
        if self.date_drawn is not None:
            self.date_drawn = self.date_drawn.replace(tzinfo=pytz.utc).astimezone(tzlocal.get_localzone())


class Winner(Base):
    __tablename__ = 'winners'
    id = Column(Integer, Sequence('winner_id_seq'), primary_key=True)
    drawing_id = Column(Integer, ForeignKey('drawings.id'), nullable=False)
    user_name = Column(String(name_length_limit), ForeignKey('users.name'), nullable=False)
    rank = Column(Integer, nullable=False)
    winnings = Column(Integer, nullable=False)
    drawing = relationship("Drawing", back_populates="winners")
    user = relationship("User", back_populates="wins")

    def __repr__(self):
        return f"<Winner(id={self.id}, drawing_id={self.drawing_id}, user_name={self.user_name}," \
               f" rank={self.rank}, winnings={self.winnings}"


class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, Sequence('sale_id_seq'), primary_key=True)
    user_name = Column(String(name_length_limit), ForeignKey('users.name'), nullable=False)
    num_tickets = Column(Integer, nullable=False)
    prize_addition = Column(Boolean, nullable=False, default=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now(pytz.utc))
    drawing_id = Column(Integer, ForeignKey('drawings.id'), nullable=False)

    drawing = relationship("Drawing", back_populates="sales")
    user = relationship("User", back_populates="sales")

    @reconstructor
    def init_on_load(self):
        self.time_created = self.time_created.replace(tzinfo=pytz.utc).astimezone(tzlocal.get_localzone())

    def __repr__(self):
        return f"<Sale(id={self.id}, user_name={self.user_name}, num_tickets={self.num_tickets}, " \
               f"time={self.time_created})>"


Base.metadata.create_all(engine)
