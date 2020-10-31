import gspread
import numpy as np
import pandas as pd
from datetime import datetime
import os


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


def get_all_entrants():
    def complete_entry(entry):
        complete = True
        for val in entry.values():
            if val == '':
                complete = False
        return complete

    # connect to the service account
    file = os.path.join(os.path.dirname(__file__), 'greymoor-ravager-1590443909240-071a0e2dcf39.json')
    gc = gspread.service_account(filename=file)
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
