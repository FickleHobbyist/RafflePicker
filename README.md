# RafflePicker
Contains a set of python routines to read raffle entries from Google Sheets and pick a winner for the Greymoor Ravagers guild in Elder Scrolls Online.

## First Time Setup
1. Clone this repository to your local drive

    ```>> git clone https://github.com/FickleHobbyist/RafflePicker.git [destination]```

### Windows
2. Open a command prompt **_as administrator_** and navigate to your `[destination]`
3. Create a new virtual environment using Python 3.8 (you may need to use the `python3` command depending on your 
   path settings. I am using `python` because I only have Python 3.8 installed).

    ```>> python -m venv .\venv```
4. Activate the virtual environment

    ```>> .\venv\Scripts\activate.bat```
5. You should now see `(venv)` prepended to the directory in your command prompt.
6. Update pip

    ```>> python -m pip install --upgrade pip```
7. Install requirements as listed in `requirements.txt`

    ```>> pip install -r requirements.txt```

8. Try running the script `PrizeUpdate.py`
    
    ```>> python PrizeUpdate.py```
    
    You should see an output in the command prompt such as this:
    
    ````
    Hey Ravagers, prize update! 687 tickets until next winner is unlocked!
    ```
       Place    |         Winnings         |
    ----------------------------------------
    1st Place:  |   156,500 gold (100.00%) |
    ----------------------------------------
          Total |  156,500 gold
    *As of 2020-11-18 09:07 PM (Pacific Standard Time)
    ```
    Rules and how to enter in this pinned message: https://discordapp.com/channels/713529934051803146/761629645077741578/765063088902111233
   
    50/50 GOLD RAFFLE UPDATE! Total Prize: 156,500 gold with 1 winner. 687 tickets until the next winner is unlocked!
    ````