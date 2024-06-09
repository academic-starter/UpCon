import os
from datetime import datetime, date

# Specify the path to the file
file_path = 'usccheck/OnchainContractData/proxy_implementations/ethereum_mainnet/0xff60d81287bf425f7b2838a61274e926440ddaa6.implementations.json'

# Get the modification timestamp of the file
modification_timestamp = os.path.getmtime(file_path)

# Convert the timestamp to a datetime object
modification_date = datetime.fromtimestamp(modification_timestamp).date()

# Get today's date
today = date.today()

# Check if the modification date is today
if modification_date == today:
    print("The file was modified today.")
else:
    print("The file was not modified today.")
