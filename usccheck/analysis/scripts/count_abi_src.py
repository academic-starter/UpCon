import os
import json
import itertools
import glob
statistics_file = "usccheck/OnchainContractData/proxy_implementations/etherscan_mainnet.statistics.json"
impls = json.load(open(statistics_file))

multiple_non_zero_impls = impls[
    "multiple_non_zero_impls"]


new_multiple_non_zero_impls = []
for x in multiple_non_zero_impls:
    proxy = x["proxy"]
    implementations = x["implementations"]
    new_implementations = list(
        filter(lambda addr: addr != "0x" and int(addr, 16) != 0, implementations))
    if len(new_implementations) < 2:
        print(" Proxy non-zero implementations less than 2 are not supported: " +
              repr(implementations))
    else:
        new_multiple_non_zero_impls.append(
            {"proxy": proxy, "implementations": new_implementations})


proxies = list(map(lambda x: x["proxy"], new_multiple_non_zero_impls))
impls = list(itertools.chain.from_iterable(
    list(map(lambda x: x["implementations"], new_multiple_non_zero_impls))))
print(len(proxies), " proxy contracts")
print(len(impls), " impl contracts")
print(len(set(impls)), " impl contracts (unique)")
# print("({0})".format(", ".join(map(lambda x: "\"" + x.lower() + "\"", proxies))))

contract_abi_dir = "usccheck/contract_abi"
cnt = 0
for addr in set(impls):
    if os.path.exists(os.path.join(contract_abi_dir, addr+".abi.json")):
        cnt += 1

print("{0} implementation contracts abi found".format(cnt))


contract_src_dir = "usccheck/contract_code/etherscan-contracts"
cnt = 0
for addr in set(impls):
    results = glob.glob(os.path.join(contract_abi_dir, addr+".*"))
    if len(results) > 0:
        cnt += 1

print("{0} implementation contracts code found".format(cnt))
