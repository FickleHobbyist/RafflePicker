import gspread
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

ticket_cost = 1000
prize_tier_increment = 500000


def main():
    entrants = get_all_entrants()
    get_winners(entrants)


def get_iso_wk(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d').isocalendar()[1]


def ordinal(n):
    ord_str = "%d%s" % (n, "tsnrhtdd"[(n//10 % 10 != 1)*(n % 10 < 4)*n % 10::4])
    return ord_str


def get_all_entrants():

    def complete_entry(entry):
        complete = True
        for val in entry.values():
            if val == '':
                complete = False
        return complete

    # connect to the service account
    gc = gspread.service_account(filename='greymoor-ravager-1590443909240-071a0e2dcf39.json')
    # open the workbook
    sh = gc.open_by_key('151kSSG2MDsASX4cP4d8-vG22I5xRYhW_RdCP4rYnhpc')
    # open the sheet
    ws = sh.worksheet("Raffle Entrants")
    # collect all data from the sheet
    tmp_entrants = ws.get('A1:D')
    all_entrants = []
    for ent in tmp_entrants[1:]:
        all_entrants.append(dict(zip(tmp_entrants[0], ent)))
    # Filter to complete entries
    entrants = list(filter(lambda e: complete_entry(e), all_entrants))
    return entrants


def get_participating_entries(entrants=None):
    if entrants is None:
        entrants = get_all_entrants()

    participating_entries = list(filter(lambda e: e['not_participating'] == 'FALSE'
                                        and e['add_to_prize_only'] == 'FALSE', entrants))
    return participating_entries


def get_prizes(entrants=None):
    if entrants is None:
        entrants = get_all_entrants()

    participating_entries = get_participating_entries(entrants)
    prize_addition_entries = list(filter(lambda e: e['add_to_prize_only'] == 'TRUE', entrants))
    tickets_sold = sum([int(e['num_entries']) for e in participating_entries])
    prize_additions = sum([int(e['num_entries']) for e in prize_addition_entries])
    prize_pool = (tickets_sold/2 + prize_additions) * ticket_cost
    num_winners_ = int(np.floor(prize_pool / prize_tier_increment) + 1)
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

    tz = datetime.now().astimezone().tzinfo
    print(f"The time is currently: {datetime.now()} ({tz})")
    total_prize_str = '{:,.0f}'.format(sum(prize_amounts))
    plural = True if num_winners > 1 else False
    winner_str = "winners" if plural else "winner"
    is_are_str = "are" if plural else "is"
    print(f"The total prize pool is {total_prize_str} gold. "
          f"There will be {num_winners} {winner_str}. The {winner_str} {is_are_str}:\n")
    winners = []
    for i in range(num_winners):
        winners.extend([random.choice(pick_list)])
        prize_str = "{:,.0f}".format(int(prize_amounts[i]))
        print(f"\t{ordinal(i+1) + ' Place:':>11} {winners[i]:<15} |"
              f"{prize_str:>10} gold ( {f'{100 * prize_dist[i]:.2f}% )':>9}")
        # remove all instances of this winner from the pickList
        pick_list = [usr for usr in pick_list if usr != winners[i]]

    print(f"\nCongratulations to the {winner_str}!")


def write_entries_table(entrants=None):
    if entrants is None:
        entrants = get_all_entrants()

    participating_entries = list(filter(lambda e: e['not_participating'] == 'FALSE'
                                        and e['add_to_prize_only'] == 'FALSE', entrants))
    df = pd.DataFrame(participating_entries)
    users = sorted(pd.unique(df.user_id), key=str.lower)
    longest_username = len(max(users, key=len))

    usr_entries = []
    d = f"{datetime.now().strftime('%Y-%m-%d')}"
    f = open(f"Greymoor Ravagers Raffle Entries {d}.txt", "w")
    f.write(f"Raffle ticket summary for {d}\n")
    hdr = f"| {'User ID':>{longest_username}} | {'Tickets'} |\n"
    f.write(hdr)
    f.write(f"{'-' * len(hdr)}\n")
    for usr in users:
        usr_entries.append(np.sum(df.num_entries[df.user_id == usr].to_numpy('int')))
        f.write(f"| {usr:>{longest_username}} | {usr_entries[-1]:>7.0f} |\n")
    f.write(f"{'-' * len(hdr)}\n")
    f.close()


def get_prize_update(plot=False):
    prize_gold, prize_dist, num_winners = get_prizes()
    total_prize = np.sum(prize_gold)

    tickets_left = 2 * (prize_tier_increment - np.mod(total_prize, prize_tier_increment)) / ticket_cost
    ticket_str = "tickets" if tickets_left > 1 else "Ticket"

    tz = datetime.now().astimezone().tzinfo
    print(f"Hey Ravagers, prize update! {tickets_left:,.0f} {ticket_str} until next winner is unlocked!")
    print("```")
    print(f"{'Place':^11} | {'Winnings':^24}|")
    print(39 * "-")
    prize_str = []
    for i in range(num_winners):
        tmp_str = "{:,.0f}".format(int(prize_gold[i]))
        prize_pct_str = f"({100 * prize_dist[i]:>6.2f}%)"
        prize_str.append(f"{ordinal(i + 1) + ' Place:'}\n{tmp_str} gold\n{prize_pct_str}")
        print(f"{ordinal(i + 1) + ' Place: ':>10} | {tmp_str:>8} gold {prize_pct_str} |")
    print(39 * "-")
    print(f"{'Total':>11} | {total_prize:>8,.0f} gold")
    print(f"*As of {datetime.now().strftime('%Y-%m-%d %I:%M %p')} ({tz})")
    print("```")
    print("Rules and how to enter in this pinned message: "
          "https://discordapp.com/channels/713529934051803146/761629645077741578/765063088902111233")
    print()
    one_line_prizes = ", ".join(prize_str).replace("\n", " ")
    one_line_prizes = f"{one_line_prizes}. " if num_winners > 1 else ""
    winner_str = "winners" if num_winners > 1 else "winner"

    print(f"50/50 GOLD RAFFLE UPDATE! Total Prize: {total_prize:,.0f} gold with "
          f"{num_winners} {winner_str}. {one_line_prizes}{tickets_left:,.0f} {ticket_str} until next winner is unlocked!")

    if plot:
        fig, ax = plt.subplots()
        ax.pie(prize_gold, labels=prize_str)
        ax.axis('equal')
        ax.set_title(f"Total Prize: {'{:,.0f}'.format(total_prize)} gold\n"
                     f"As of {datetime.now().strftime('%Y-%m-%d %I:%M %p')} ({tz})")
        plt.savefig("PrizeUpdate.png")
        plt.show()


if __name__ == "__main__":
    main()
