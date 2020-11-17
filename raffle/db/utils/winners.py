from raffle.db import session_scope
from raffle.db.orm import Winner
import raffle.db.utils as rdbu


def add_winner(user_name: str, place: int, winnings: int):
    with session_scope() as session:
        cur_dwg = rdbu.drawings.get_current_drawing(session)
        winner = Winner(user_name=user_name, rank=place, winnings=winnings, drawing_id=cur_dwg.id) # noqa
        session.add(winner)