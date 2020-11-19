from raffle.db import session_scope
from raffle.db.orm import User


def add_user(user_name: str, session=None):
    def __add_user(session_):
        if user_exists(user_name, session_):
            print(f"User {user_name} already exists in table 'users'.")
        else:
            usr = User(name=user_name) # noqa
            session_.add(usr)
            # session.commit()
            print(f"Successfully added {user_name} to table 'users'.")

    if session is None:
        with session_scope() as session:
            __add_user(session)
    else:
        # assert isinstance(session, Session)
        __add_user(session)


def get_all_users():
    user_dicts = []
    with session_scope() as session:
        users = session.query(User).order_by(User.name.asc()).all()
        for user in users:
            user_dicts.append(user.asdict())

    user_dicts.sort(key=lambda u: u['name'].lower())
    return user_dicts


def user_exists(user_name: str, session) -> bool:
    # assert isinstance(session, Session)
    # find if user exists in users table
    user_query = session.query(User).filter_by(name=user_name).first()
    if user_query is None:
        tf = False
    else:
        tf = True
    return tf
