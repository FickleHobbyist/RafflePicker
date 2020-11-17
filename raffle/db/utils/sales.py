from sqlalchemy import and_
from sqlalchemy.sql import func
from raffle.db.orm import Sale, Drawing
from raffle.db import session_scope
import raffle.db.utils as rdbu


def add_sale(user_name: str, tickets_sold: int, prize_add: bool = False, session=None):

    def __add_sale(session_):
        if not rdbu.users.user_exists(user_name, session_):
            rdbu.users.add_user(user_name, session_)
        cur_dwg = rdbu.drawings.get_current_drawing(session_)
        if cur_dwg is None:
            drawing_id = rdbu.drawings.add_drawing()
        else:
            drawing_id = cur_dwg.id

        sale = Sale(user_name=user_name, num_tickets=tickets_sold, prize_addition=prize_add, drawing_id=drawing_id) # noqa
        session_.add(sale)
        session_.flush()
        sale_id_ = sale.id
        print(f"Successfully added sale of {tickets_sold} {'tickets' if tickets_sold > 1 else 'ticket'}"
              f" to user '{user_name}'.")
        return sale_id_

    if session is None:
        with session_scope() as session:
            sale_id = __add_sale(session)
    else:
        # assert isinstance(session, Session)
        sale_id = __add_sale(session)

    return sale_id


def edit_sale(sale_id: int, user_name: str = None, tickets_sold: int = None, prize_add: bool = None):
    with session_scope() as session:
        sale = session.query(Sale).filter(Sale.id == sale_id).first()
        assert sale is not None, f"Could not find sale with id={sale_id}."
        if user_name is not None:
            sale.user_name = user_name
        if tickets_sold is not None:
            sale.num_tickets = tickets_sold
        if prize_add is not None:
            sale.prize_addition = prize_add


def get_sale(sale_id: int) -> dict:
    with session_scope() as session:
        sale = session.query(Sale).filter(Sale.id == sale_id).first()
        sale_dict = sale.asdict() if sale is not None else None
    return sale_dict


def get_last_sales(n: int = 5) -> list:
    sale_dicts = []
    with session_scope() as session:
        sales = session.query(Sale).order_by(Sale.id.desc()).limit(n)
        sales = sales[::-1]
        for sale in sales:
            sale_dicts.append(sale.asdict())

    return sale_dicts


def get_all_sales() -> list:
    sale_dicts = []
    with session_scope() as session:
        sales = session.query(Sale).all()
        for sale in sales:
            sale_dicts.append(sale.asdict())
    return sale_dicts


def get_drawing_sales_summary(current_drawing: Drawing = None):
    with session_scope() as session:
        if current_drawing is None:
            current_drawing = rdbu.drawings.get_current_drawing(session)

        sales = session.query(Sale.user_name.label('user_name'), func.sum(Sale.num_tickets).label('total_tickets')) \
            .group_by(Sale.user_name) \
            .filter(and_(Sale.drawing_id == current_drawing.id, Sale.prize_addition.is_(False))) \
            .order_by(Sale.user_name).all()

        pr_adds = session.query(Sale.user_name.label('user_name'), func.sum(Sale.num_tickets).label('total_tickets')) \
            .group_by(Sale.user_name) \
            .filter(and_(Sale.drawing_id == current_drawing.id, Sale.prize_addition.is_(True))) \
            .order_by(Sale.user_name).all()

    sales.sort(key=lambda t: tuple(t[0].lower()))
    pr_adds.sort(key=lambda t: tuple(t[0].lower()))
    return sales, pr_adds
