import gspread
import random
from datetime import datetime


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
ws = sh.worksheet("Crown Crate Raffle Entries")
# collect all data from the sheet
# all_entrants = ws.get_all_records()  # returns list of dicts
tmp_entrants = ws.get('A1:C')
all_entrants = []
for ent in tmp_entrants[1:]:
    all_entrants.append(dict(zip(tmp_entrants[0], ent)))

current_wk_num = datetime.today().isocalendar()[1]

entrants = list(filter(lambda e: complete_entry(e), all_entrants))

pickList = []
for entrant in entrants:
    # print(entrant)
    if entrant['not_participating'] == 'FALSE':
        # user is participating, so add to the pick list with appropriate num entries
        pickList.extend([entrant['user_id']] * int(entrant['num_entries']))

winners = []
num_winners = 1
for i in range(num_winners):
    winners.extend([random.choice(pickList)])
    # remove all instances of this winner from the pickList
    pickList = [usr for usr in pickList if usr != winners[i]]

print("The time is currently (PDT): ", datetime.now())
print("The crown crate raffle winner is: ", ', '.join(map(str, winners)))
# print("The crown crate raffle winners are: ", ', '.join(map(str, winners)))
