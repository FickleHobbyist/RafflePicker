import RafflePicker as rp
import pandas as pd
import numpy as np
from datetime import datetime

ent = rp.get_entrants()

participating_entries = list(filter(lambda e: e['not_participating'] == 'FALSE'
                                    and e['add_to_prize_only'] == 'FALSE', ent))
df = pd.DataFrame(participating_entries)
users = sorted(pd.unique(df.user_id), key=str.lower)
longest_username = len(max(users, key=len))

usr_entries = []
d = f"{datetime.now().strftime('%Y-%m-%d')}"
f = open(f"Greymoor Ravagers Raffle Entries {d}.txt", "w")
f.write(f"Raffle ticket summary for {d}\n")
hdr = f"| {'User ID':>{longest_username}} | {'Tickets'} |\n"
f.write(hdr)
f.write(f"{'-'*len(hdr)}\n")
for usr in users:
    usr_entries.append(np.sum(df.num_entries[df.user_id == usr].to_numpy('int')))
    f.write(f"| {usr:>{longest_username}} | {usr_entries[-1]:>7.0f} |\n")

f.write(f"{'-'*len(hdr)}\n")
f.close()
df_out = pd.DataFrame({'USER_ID': users, 'TICKETS_PURCHASED': usr_entries})
kb = 1