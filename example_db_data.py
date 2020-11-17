import raffle.db.utils as rdbu
from raffle.db import session_scope, sample_users
import raffle.entries
import raffle.prize2 as rp2
import csv
import os
import random


def load_from_gsheet():
    rdbu.drawings.add_drawing()
    entries = raffle.entries.get_all_entrants()
    with session_scope() as session:
        for entry in entries:
            rdbu.sales.add_sale(user_name=entry['user_name'],
                                tickets_sold=int(entry['num_entries']),
                                prize_add=entry['add_to_prize_only'] == 'TRUE',
                                session=session)


def load_sample_data():
    rdbu.drawings.add_drawing()
    f = os.path.join(os.path.dirname(__file__), 'raffle/db/sample_sales.csv')
    with session_scope() as session:
        with open(f, newline='', mode='r') as csv_file:
            data = csv.DictReader(csv_file)
            for entry in data:
                rdbu.sales.add_sale(user_name=entry['user_name'],
                                    tickets_sold=int(entry['num_tickets']),
                                    prize_add=entry['prize_addition'] == '1',
                                    # this is because bool cannot reliably convert
                                    # strings to boolean values. shenanigans.
                                    session=session)
                print(f"User: {entry['user_name']}, num_tickets: {entry['num_tickets']}, "
                      f"prize_addition: {entry['prize_addition']}")


def create_random_data():
    # create 4 drawings
    for i in range(4):
        rdbu.drawings.add_drawing()
        # in each drawing, add random number of sales to random users, with random number of tickets per sale
        n_sales = random.randint(30, 100)
        with session_scope() as session:
            rdbu.sales.add_sale(user_name='GreymoorRavagersBank', tickets_sold=50, prize_add=True, session=session)
            for _ in range(n_sales):
                n_tickets = random.randint(1, 50)
                rdbu.sales.add_sale(user_name=random.choice(sample_users),
                                    tickets_sold=n_tickets,
                                    prize_add=False,
                                    session=session)

        # pick winners and close drawing for all but last drawing
        if i < 3:
            winners = rp2.get_winners()
            for winner_name, place, winnings in winners:
                # add winners to table
                rdbu.winners.add_winner(user_name=winner_name,
                                        place=place,
                                        winnings=winnings)
            # close drawing
            rdbu.drawings.close_drawing()


if __name__ == 'main':
    create_random_data()
