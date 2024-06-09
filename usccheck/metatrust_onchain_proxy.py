import json 
import os 
from itertools import chain

def contain_implementation(abi):
    for item in abi:
        if "name" in item and item["name"] == "implementation" and item["type"] == "function":
            return True
    return False

proxy_file = "usccheck/OnchainContractData/proxy_warehouse_public_ads_contract_metadata.json"

all_proxy_contracts = json.load(open(proxy_file))
all_ethereum_mainnet_proxy_contracts = list(filter(lambda x: x["chain_id"]==1, all_proxy_contracts))
implementation_interfaces_proxy_contracts =  []
for proxy_contract in all_ethereum_mainnet_proxy_contracts:
    print(proxy_contract["block"])
    print(proxy_contract["address"])
    if contain_implementation(proxy_contract["abi"]):
        implementation_interfaces_proxy_contracts.append(proxy_contract)

print("**"*10)
print("Total number of ethereum mainnet proxy_contracts: ", len(all_ethereum_mainnet_proxy_contracts))
print("Total number of ethereum mainnet proxy_contracts having implementation interfaces: ", len(implementation_interfaces_proxy_contracts))

output_file = os.path.join("usccheck/OnchainContractData", "ethereum_mainnet.json")
json.dump(implementation_interfaces_proxy_contracts, open(output_file, "w"))

result = list(chain.from_iterable([[proxy_contract["address"], proxy_contract["block"]] for proxy_contract in all_ethereum_mainnet_proxy_contracts]))
open(os.path.join("usccheck/OnchainContractData", "ethereum_mainnet.list"), "w").write("\n".join(map(str, result)))