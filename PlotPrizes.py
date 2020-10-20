import RafflePicker as rp
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

tier_increment = 500000
ticket_cost = 1000

ent = rp.get_entrants()
prize_gold, prize_dist, num_winners = rp.get_prizes(ent)
total_prize = np.sum(prize_gold)


tickets_left = 2 * (tier_increment - np.mod(total_prize, tier_increment))/ticket_cost
ticket_str = "tickets" if tickets_left > 1 else "Ticket"

tz = datetime.now().astimezone().tzinfo
print(f"Hey Ravagers, prize update! {tickets_left:,.0f} {ticket_str} until next winner is unlocked!")
print("```")
print(f"{'Place':^11} | {'Winnings':^24}|")
print(39*"-")
prize_str = []
for i in range(num_winners):
    tmp_str = "{:,.0f}".format(int(prize_gold[i]))
    prize_pct_str = f"({100 * prize_dist[i]:>6.2f}%)"
    prize_str.append(f"{rp.ordinal(i + 1) + ' Place:'}\n{tmp_str} gold\n{prize_pct_str}")
    print(f"{rp.ordinal(i + 1) + ' Place: ':>10} | {tmp_str:>8} gold {prize_pct_str} |")
print(39*"-")
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
fig, ax = plt.subplots()
ax.pie(prize_gold, labels=prize_str)
ax.axis('equal')
ax.set_title(f"Total Prize: {'{:,.0f}'.format(total_prize)} gold\n"
             f"As of {datetime.now().strftime('%Y-%m-%d %I:%M %p')} ({tz})")
# ax.set_title(f"Sample Prize Distribution\n{num_winners} winner(s) totaling {'{:,.0f}'.format(sum(prize_gold))} gold")
plt.savefig("PrizeUpdate.png")
plt.show()
