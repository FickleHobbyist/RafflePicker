from sqlalchemy import create_engine, Column, Integer, ForeignKey, String, Date, DateTime, Sequence, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, validates, relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import pytz
import raffle.entries

# engine = create_engine('sqlite:///raffle.db', echo=True)
engine = create_engine('sqlite:///:memory:', echo=True)
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
    draw_date = Column(Date, nullable=True, default=None)
    winners = relationship("Winner")

    def __repr__(self):
        return f"<Drawing(id={self.id}, draw_date={self.draw_date}, winners={self.winners}"


class Winner(Base):
    __tablename__ = 'winners'
    id = Column(Integer, Sequence('winner_id_seq'), primary_key=True)
    draw_date = Column(Date, ForeignKey('drawings.draw_date'), nullable=False)
    user_name = Column(String, ForeignKey('users.name'), nullable=False)
    winnings = Column(Integer, nullable=False)
    dwg = relationship("Drawing", back_populates="winners")

    def __repr__(self):
        return f"<Winner(id={self.id}, draw_date={self.draw_date}, user_name={self.user_name}, winnings={self.winnings}"


class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, Sequence('sale_id_seq'), primary_key=True)
    user_name = Column(String, ForeignKey('users.name'))
    num_tickets = Column(Integer, nullable=False)
    time_created = Column(DateTime(timezone=True), server_default=func.now(pytz.utc))
    draw_date = Column(Date, nullable=True, default=None)

    user = relationship("User", back_populates="user_sales")

    def __repr__(self):
        return f"<Sale(id={self.id}, user_name={self.user_name}, num_tickets={self.num_tickets}, " \
               f"time={self.time_created})>"


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

session = Session()


def user_exists(user_id: str) -> bool:
    # find if user exists in users table
    user_query = session.query(User).filter_by(name=user_id).first()
    if user_query is None:
        tf = False
    else:
        tf = True
    return tf


def add_user(user_id: str):
    if user_exists(user_id):
        print(f"User {user_id} already exists in table 'users'.")
    else:
        usr = User(name=user_id)
        session.add(usr)
        session.commit()
        print(f"Successfully added {user_id} to table 'users'.")


def add_sale(user_id: str, tickets_sold: int):
    if not user_exists(user_id):
        add_user(user_id)

    sale = Sale(user_name=user_id, num_tickets=tickets_sold)
    session.add(sale)
    session.commit()
    print(f"Successfully added sale of {tickets_sold} {'tickets' if tickets_sold > 1 else 'ticket'} to user '{user_id}'.")


def get_raffle_start():
    prev_sat = datetime.now(pytz.utc)
    # raffle occurs on Sunday at 1 AM UTC every week. This is equivalent to Saturday 6 pm PST.
    while prev_sat.weekday() != 6:  # 0 = Monday, Sunday = 6.
        prev_sat = prev_sat - timedelta(days=1)

    raffle_start = datetime(year=prev_sat.year,
                            month=prev_sat.month,
                            day=prev_sat.day,
                            hour=1,
                            minute=0,
                            second=0,
                            tzinfo=pytz.utc)

    return raffle_start


def get_raffle_week_sales():
    rs = get_raffle_start()

    sales = session.query(Sale.user_name.label('user_id'), func.sum(Sale.num_tickets).label('total_tickets')) \
        .group_by(Sale.user_name).filter(and_(Sale.time_created > rs, Sale.draw_date.is_(None))) \
        .order_by(Sale.user_name).all()

    return sales.sort(key=lambda t: tuple(t[0].lower()))


def load_from_gsheet():
    entries = raffle.entries.get_participating_entries()
    for entry in entries:
        add_sale(entry['user_id'], int(entry['num_entries']))
