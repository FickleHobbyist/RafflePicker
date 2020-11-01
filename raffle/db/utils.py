from raffle.db.orm import Sale, User, Winner, Drawing
from raffle.db import session_scope
from datetime import datetime, timedelta
from sqlalchemy.sql import func
from sqlalchemy import and_
import pytz
import tzlocal
import raffle.entries


def user_exists(user_id: str, session) -> bool:
    # assert isinstance(session, Session)
    # find if user exists in users table
    user_query = session.query(User).filter_by(name=user_id).first()
    if user_query is None:
        tf = False
    else:
        tf = True
    return tf


def add_user(user_id: str, session=None):

    def __add_user(session_):
        if user_exists(user_id, session_):
            print(f"User {user_id} already exists in table 'users'.")
        else:
            usr = User(name=user_id)
            session_.add(usr)
            # session.commit()
            print(f"Successfully added {user_id} to table 'users'.")

    if session is None:
        with session_scope() as session:
            __add_user(session)
    else:
        # assert isinstance(session, Session)
        __add_user(session)


def add_sale(user_id: str, tickets_sold: int, prize_add=False, session=None):

    def __add_sale(session_):
        if not user_exists(user_id, session_):
            add_user(user_id, session_)
        sale = Sale(user_name=user_id, num_tickets=tickets_sold, prize_addition=prize_add)
        session_.add(sale)
        # session.commit()
        print(f"Successfully added sale of {tickets_sold} {'tickets' if tickets_sold > 1 else 'ticket'}"
              f" to user '{user_id}'.")

    if session is None:
        with session_scope() as session:
            __add_sale(session)
    else:
        # assert isinstance(session, Session)
        __add_sale(session)


def add_drawing():
    with session_scope() as session:
        dwg = Drawing(draw_date=datetime.utcnow().date())
        session.add(dwg)
    print(f"Successfully created drawing for date=<{dwg.draw_date}>")


def get_raffle_start(local=True):
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
    if local:
        raffle_start = raffle_start.astimezone(tzlocal.get_localzone())

    return raffle_start


def get_raffle_week_sales():
    rs = get_raffle_start(local=False)
    with session_scope() as session:
        sales = session.query(Sale.user_name.label('user_id'), func.sum(Sale.num_tickets).label('total_tickets')) \
            .group_by(Sale.user_name).filter(and_(Sale.time_created > rs, Sale.draw_date.is_(None))) \
            .order_by(Sale.user_name).all()

    sales.sort(key=lambda t: tuple(t[0].lower()))
    return sales


def load_from_gsheet():
    entries = raffle.entries.get_participating_entries()
    with session_scope() as session:
        for entry in entries:
            add_sale(entry['user_id'], int(entry['num_entries']), session)
