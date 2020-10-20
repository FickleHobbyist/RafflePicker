import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import pandas as pd


def ordinal(n):
    ord_str = "%d%s" % (n, "tsnrhtdd"[(n//10 % 10 != 1)*(n % 10 < 4)*n % 10::4])
    return ord_str


tier_increment = 500000
sample_increment = 500
prize_max = 3495000
iSample = 0

max_winners = int(np.floor(prize_max / tier_increment) + 1)
num_samples = int(np.floor(prize_max / sample_increment)) + 1
prize_pool = np.arange(0, prize_max+sample_increment, sample_increment)
prize_pool = prize_pool[:, np.newaxis]
prize_amounts = np.full( (num_samples, max_winners) , np.nan)
for iSample in range(num_samples):
    num_winners = int(np.floor(prize_pool[iSample] / tier_increment) + 1)

    # spacing = np.logspace(0, np.pi/2, num=2 + num_winners, base=100)
    # tmp_dist = np.cos(spacing)

    spacing = np.logspace(1, 0, num=2 + num_winners, base=100)
    tmp_dist = spacing

    prize_dist = tmp_dist[1:len(tmp_dist) - 1] / np.sum(tmp_dist[1:len(tmp_dist) - 1])
    prize_amounts[iSample, 0:num_winners] = np.round(prize_pool[iSample] * prize_dist)
    j = 1
    msg = []
    while j <= num_winners:
        prize_str = "{:,}".format(int(prize_amounts[iSample, j - 1]))
        msg.extend([f"{ordinal(j)} Place: {prize_str} ({100*prize_dist[j-1]:.2f}%)"])
        j += 1
    # print(f"Prize pool: {prize_pool[iSample]} || {', '.join(msg)}")


fig, ax = plt.subplots()
for n in range(0,max_winners):
    ax.plot(prize_pool, prize_amounts[:, n], label=f"{ordinal(n+1)} Place")

ax.set_xlabel('Prize Pool')
ax.set_ylabel('Winnings')
ax.set_title('Greymoor Ravagers Raffle Prize Tiers')
plt.minorticks_on()
ax.grid(b=True, which='major', axis='both', linestyle='-')
ax.grid(b=True, which='minor', axis='both', linestyle='--')
ax.yaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
plt.legend()
plt.show()


# out = np.concatenate((prize_pool, prize_amounts), axis=1)
# np.savetxt("test2.csv", out, delimiter=',')