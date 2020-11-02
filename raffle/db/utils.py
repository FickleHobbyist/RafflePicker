from raffle.db.orm import Sale, User, Winner, Drawing
from raffle.db import session_scope
from datetime import datetime, timedelta
from sqlalchemy.sql import func
from sqlalchemy import and_
import pytz
import tzlocal
import raffle.entries
import csv


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


def add_drawing():
    with session_scope() as session:
        cur_dwg = get_current_drawing(session)
        assert cur_dwg is None, f"An open drawing already exists with id={cur_dwg.id}."
        dwg = Drawing()
        session.add(dwg)
        session.flush()
        dwg_id = dwg.id

    print(f"Successfully created drawing id={dwg_id}>")
    return dwg_id


def add_sale(user_id: str, tickets_sold: int, drawing_id: int, prize_add: bool = False, session=None):

    def __add_sale(session_):
        if not user_exists(user_id, session_):
            add_user(user_id, session_)
        sale = Sale(user_name=user_id, num_tickets=tickets_sold, prize_addition=prize_add, drawing_id=drawing_id)
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


def add_winner(user_id: str, place: int, winnings: int):
    with session_scope() as session:
        winner = Winner(user_name=user_id, rank=place, winnings=winnings)
        session.add(winner)


def get_current_drawing(session):
    current_drawing = session.query(Drawing).filter(Drawing.date_drawn.is_(None)).first()
    return current_drawing


def close_drawing():
    with session_scope() as session:
        current_drawing = get_current_drawing(session)
        current_drawing.date_drawn = datetime.utcnow().date()


def get_drawing_sales_summary(current_drawing: Drawing = None):

    with session_scope() as session:
        if current_drawing is None:
            current_drawing = get_current_drawing(session)

        sales = session.query(Sale.user_name.label('user_id'), func.sum(Sale.num_tickets).label('total_tickets')) \
            .group_by(Sale.user_name) \
            .filter(and_(Sale.drawing_id == current_drawing.id, Sale.prize_addition.is_(False))) \
            .order_by(Sale.user_name).all()

        pr_adds = session.query(Sale.user_name.label('user_id'), func.sum(Sale.num_tickets).label('total_tickets')) \
            .group_by(Sale.user_name) \
            .filter(and_(Sale.drawing_id == current_drawing.id, Sale.prize_addition.is_(True))) \
            .order_by(Sale.user_name).all()

    sales.sort(key=lambda t: tuple(t[0].lower()))
    pr_adds.sort(key=lambda t: tuple(t[0].lower()))
    return sales, pr_adds


def load_from_gsheet():
    dwg_id = add_drawing()
    entries = raffle.entries.get_all_entrants()
    with session_scope() as session:
        for entry in entries:
            add_sale(user_id=entry['user_id'],
                     tickets_sold=int(entry['num_entries']),
                     prize_add=entry['add_to_prize_only'] == 'TRUE',
                     drawing_id=dwg_id,
                     session=session)


def load_sample_data():
    dwg_id = add_drawing()
    with session_scope() as session:
        with open('sample_sales.csv', newline='', mode='r') as csv_file:
            data = csv.DictReader(csv_file)
            for entry in data:
                add_sale(user_id=entry['user_name'],
                         tickets_sold=int(entry['num_tickets']),
                         prize_add=entry['prize_addition'] == '1',  # this is because bool cannot reliably convert
                                                                    # strings to boolean values. shenanigans.
                         drawing_id=dwg_id,
                         session=session)
                print(f"User: {entry['user_name']}, num_tickets: {entry['num_tickets']}, "
                      f"prize_addition: {entry['prize_addition']}")
