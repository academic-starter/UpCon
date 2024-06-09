import json
import pandas as pd
import numpy as np

contract_count_ls = json.load(
    open("usccheck/OnchainContractData/statistics_contract_cnt.json"))
proxy_count_ls = json.load(open(
    "usccheck/OnchainContractData/statistics_proxy.json"))

rows = []
for item in contract_count_ls:
    chain = item["chain_id"]
    contract_count = item["count"]
    match_items = list(
        filter(lambda x: x["chain_id"] == chain, proxy_count_ls))
    if len(match_items) == 0:
        proxy_count = 0
    else:
        proxy_item = match_items[0]
        proxy_count = proxy_item["count"]

    rows.append([chain, contract_count, proxy_count])

print(rows)

df = pd.DataFrame(np.array(rows), columns=[
    "chain", "contract count", "proxy count"])

print(df)

df.to_csv(open("usccheck/analysis/table_contract_proxy_ratio.csv", "w"))
