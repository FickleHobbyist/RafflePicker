from raffle.db.orm import Drawing
from raffle.db import session_scope
from datetime import datetime


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


def get_current_drawing(session):
    current_drawing = session.query(Drawing).filter(Drawing.date_drawn.is_(None)).first()
    return current_drawing


def close_drawing():
    with session_scope() as session:
        current_drawing = get_current_drawing(session)
        current_drawing.date_drawn = datetime.utcnow().date()
