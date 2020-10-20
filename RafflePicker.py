import gspread
import random
import numpy as np
from datetime import datetime


def main():
    entrants = get_entrants()
    get_winners(entrants)


def complete_entry(entry):
    complete = True
    for val in entry.values():
        if val == '':
            complete = False
    return complete


def get_iso_wk(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').isocalendar()[1]


def ordinal(n):
    ord_str = "%d%s" % (n, "tsnrhtdd"[(n//10 % 10 != 1)*(n % 10 < 4)*n % 10::4])
    return ord_str


def get_entrants():
    # connect to the service account
    gc = gspread.service_account(filename='greymoor-ravager-1590443909240-071a0e2dcf39.json')
    # open the workbook
    sh = gc.open_by_key('151kSSG2MDsASX4cP4d8-vG22I5xRYhW_RdCP4rYnhpc')
    # open the sheet
    ws = sh.worksheet("Raffle Entrants")
    # collect all data from the sheet
    # all_entrants = ws.get_all_records()  # returns list of dicts
    tmp_entrants = ws.get('A1:D')
    all_entrants = []
    for ent in tmp_entrants[1:]:
        all_entrants.append(dict(zip(tmp_entrants[0], ent)))
    current_wk_num = datetime.today().isocalendar()[1]
    entrants = list(filter(lambda e: complete_entry(e), all_entrants))
    # entrants = list(filter(lambda e: get_iso_wk(e['week_ending_sat']) == current_wk_num, all_entrants))
    return entrants


def get_prizes(entrants_):
    ticket_cost = 1000
    tier_increment = 500000

    participating_entries = list(filter(lambda e: e['not_participating'] == 'FALSE'
                                        and e['add_to_prize_only'] == 'FALSE', entrants_))
    prize_addition_entries = list(filter(lambda e: e['add_to_prize_only'] == 'TRUE', entrants_))
    tickets_sold = sum([int(e['num_entries']) for e in participating_entries])
    prize_additions = sum([int(e['num_entries']) for e in prize_addition_entries])
    prize_pool = (tickets_sold/2 + prize_additions) * ticket_cost
    num_winners_ = int(np.floor(prize_pool / tier_increment) + 1)
    tmp_dist = np.logspace(1, 0, num=2 + num_winners_, base=100)
    prize_dist_ = tmp_dist[1:-1] / np.sum(tmp_dist[1:-1])
    prizes = np.round(prize_dist_ * prize_pool)
    return prizes, prize_dist_, num_winners_


def get_winners(entrants):
    pick_list = []
    for entrant in entrants:
        # print(entrant)
        if entrant['not_participating'] == 'FALSE' or entrant['add_to_prize_only'] == 'FALSE':
            # user is participating, so add to the pick list with appropriate num entries
            pick_list.extend([entrant['user_id']] * int(entrant['num_entries']))

    prize_amounts, prize_dist, num_winners = get_prizes(entrants)

    winners = []
    # msg = []
    tz = datetime.now().astimezone().tzinfo
    print(f"The time is currently: {datetime.now()} ({tz})")
    total_prize_str = '{:,.0f}'.format(sum(prize_amounts))
    plural = True if num_winners > 1 else False
    winner_str = "winners" if plural else "winner"
    is_are_str = "are" if plural else "is"
    print(f"The total prize pool is {total_prize_str} gold. "
          f"There will be {num_winners} {winner_str}. The {winner_str} {is_are_str}:\n")
    for i in range(num_winners):
        winners.extend([random.choice(pick_list)])
        prize_str = "{:,.0f}".format(int(prize_amounts[i]))
        print(f"\t{ordinal(i+1) + ' Place:':>11} {winners[i]:<15} |"
              f"{prize_str:>10} gold ( {f'{100 * prize_dist[i]:.2f}% )':>9}")
        # remove all instances of this winner from the pickList
        pick_list = [usr for usr in pick_list if usr != winners[i]]

    print(f"\nCongratulations to the {winner_str}!")


if __name__ == "__main__":
    main()
