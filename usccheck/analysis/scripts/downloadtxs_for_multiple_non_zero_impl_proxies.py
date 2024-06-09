import os
import json
import itertools
import time
import datetime

statistics_file = "../../OnchainContractData/proxy_implementations/etherscan_mainnet.statistics.json"
multiple_non_zero_impls = json.load(open(statistics_file))[
    "multiple_non_zero_impls"]
proxies = list(map(lambda x: x["proxy"], multiple_non_zero_impls))
impls = list(itertools.chain.from_iterable(
    list(map(lambda x: x["implementations"], multiple_non_zero_impls))))
print(len(proxies), " proxy contracts")
print(len(impls), " impl contracts")
print(len(set(impls)), " impl contracts (unique)")

cmd = "python -m plugin.BlockchainDataProvider {0}"
cnt = 0
for proxy in proxies:
    # Get the current datetime
    now = datetime.datetime.now()
    # Format the datetime as a string
    formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
    print(formatted_datetime)
    print(cnt, cmd.format(proxy))
    os.system(cmd.format(proxy))
    cnt += 1
