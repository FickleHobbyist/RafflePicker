import random
import raffle
import raffle.db.utils as rdbu
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime


ticket_cost = 1000
prize_tier_increment = 500000


def get_prizes(entrants=None, prize_adds=None):
    if entrants is None or prize_adds is None:
        entrants, prize_adds = rdbu.get_drawing_sales_summary()

    tickets_sold = sum(n for _, n in entrants)
    prize_additions = sum(n for _, n in prize_adds)

    prize_pool = (tickets_sold/2 + prize_additions) * ticket_cost
    num_winners_ = int(np.floor(prize_pool / prize_tier_increment) + 1)
    tmp_dist = np.logspace(1, 0, num=2 + num_winners_, base=100)
    prize_dist_ = tmp_dist[1:-1] / np.sum(tmp_dist[1:-1])
    prizes = np.round(prize_dist_ * prize_pool)
    return prizes, prize_dist_, num_winners_


def get_winners():
    entrants, pr_adds = rdbu.get_drawing_sales_summary()

    prize_amounts, prize_dist, num_winners = get_prizes(entrants=entrants, prize_adds=pr_adds)
    prize_amounts = [int(p) for p in prize_amounts]
    pick_list = []
    for name, num_tix in entrants:
        pick_list.extend([name]*num_tix)

    # This also works but I don't fully understand the syntax of the nested comprehension
    # pick_list = [y for (name, num_tix) in entrants for y in [name] * num_tix]

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
        winner_name = random.choice(pick_list)
        winners.extend([(winner_name, i, prize_amounts[i])])
        prize_str = "{:,.0f}".format(prize_amounts[i])
        print(f"\t{raffle.utils.ordinal(i+1) + ' Place:':>11} {winner_name:<15} |"
              f"{prize_str:>10} gold ( {f'{100 * prize_dist[i]:.2f}% )':>9}")
        # remove all instances of this winner from the pickList
        pick_list = [usr for usr in pick_list if usr != winner_name]

    print(f"\nCongratulations to the {winner_str}!")

    return winners


def get_prize_update(plot=False):
    prize_gold, prize_dist, num_winners = get_prizes()
    total_prize = np.sum(prize_gold)

    tickets_left = 2 * (prize_tier_increment - np.mod(total_prize, prize_tier_increment)) / ticket_cost
    ticket_str = "tickets" if tickets_left > 1 else "Ticket"

    tz = datetime.now().astimezone().tzinfo
    print(f"Hey Ravagers, prize update! {tickets_left:,.0f} {ticket_str} until next winner is unlocked!")
    print("```")
    print(f"{'Place':^11} | {'Winnings':^25}|")
    print(40 * "-")
    prize_str = []
    for i in range(num_winners):
        tmp_str = "{:,.0f}".format(int(prize_gold[i]))
        prize_pct_str = f"({100 * prize_dist[i]:>6.2f}%)"
        prize_str.append(f"{raffle.utils.ordinal(i + 1) + ' Place:'}\n{tmp_str} gold\n{prize_pct_str}")
        print(f"{raffle.utils.ordinal(i + 1) + ' Place: ':>10} | {tmp_str:>9} gold {prize_pct_str} |")
    print(40 * "-")
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
          f"{num_winners} {winner_str}. {one_line_prizes}"
          f"{tickets_left:,.0f} {ticket_str} until the next winner is unlocked!")

    if plot:
        fig, ax = plt.subplots()
        ax.pie(prize_gold, labels=prize_str)
        ax.axis('equal')
        ax.set_title(f"Total Prize: {'{:,.0f}'.format(total_prize)} gold\n"
                     f"As of {datetime.now().strftime('%Y-%m-%d %I:%M %p')} ({tz})")
        plt.savefig("PrizeUpdate.png")
        plt.show()
