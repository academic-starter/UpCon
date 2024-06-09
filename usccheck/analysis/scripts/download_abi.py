import requests
import os
import json


def get_contract_abi(contract_address, api_key):
    try:
        url = f"https://api.etherscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={api_key}"
        print(url)
        response = requests.get(url)
        data = response.json()
        return data['result']
    except:
        return None


def download_contract_abi(contract_address="0x67e70eeb9dd170f7b4a9ef620720c9069d5e706c", ouput_dir="./usccheck/contract_abi", api_key="SDI5QEC2UAY1CX4C1VPXC4WE9HIMH2SF1C"):
    contract_address = contract_address.lower()
    if contract_address == "0x0000000000000000000000000000000000000000" or contract_address == "0x0" or contract_address == "0x":
        return
    if os.path.exists(os.path.join(ouput_dir, contract_address+".abi.json")):
        return
    abi = get_contract_abi(contract_address, api_key)
    # print("Contract ABI:")
    # print(abi)
    if abi is None or abi.strip() == "Contract source code not verified":
        return
    else:
        try:
            json.dump(json.loads(abi), open(os.path.join(
                ouput_dir, contract_address+".abi.json"), 'w'), indent=4)
        except:
            print("wrong result for Contract ABI:")
            print(abi)
            return
