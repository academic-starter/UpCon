import os
import json
import itertools
import numpy as np
import pandas as pd
import subprocess
from infura import func_call, code_exists


def load_contract_abi(impl):
    abi_file = os.path.join(
        "./usccheck/contract_abi", impl.lower()+".abi.json")
    if impl == "0x0000000000000000000000000000000000000000" or impl == "0x0" or impl == "0x":
        return None
    if os.path.exists(abi_file):
        return json.load(open(abi_file))
    else:
        return None


def run_curl_command(url):
    # Run the cURL command and capture its output
    result = subprocess.run(['curl', url], capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode == 0:
        return result.stdout
    else:
        # Print error message if the command failed
        print("Error:", result.stderr)
        return None


statistics_file = "usccheck/OnchainContractData/proxy_implementations/etherscan_mainnet.statistics.json"
multiple_non_zero_impls = json.load(open(statistics_file))[
    "multiple_non_zero_impls"]
proxies = list(map(lambda x: x["proxy"], multiple_non_zero_impls))
impls = list(itertools.chain.from_iterable(
    list(map(lambda x: x["implementations"], multiple_non_zero_impls))))
print(len(proxies), " proxy contracts")
print(len(impls), " impl contracts")
print(len(set(impls)), " impl contracts (unique)")
# print("({0})".format(", ".join(map(lambda x: "\"" + x.lower() + "\"", proxies))))

proxy_implementation_dir = "usccheck/OnchainContractData/proxy_implementations/ethereum_mainnet/"

cnt = 0
blocks_results = {}
impls_results = {}
max_block = 0
for item in os.listdir(proxy_implementation_dir):
    if item.endswith(".json"):
        address = item.split(".implementations.json")[0]
        result = json.load(
            open(os.path.join(proxy_implementation_dir, item)))
        if len(result) > 1:
            sorted_result = sorted(result, key=lambda x: x["block"])
            cnt += 1
            blocks = list(map(lambda x: x["block"], sorted_result))
            max_block = max([max_block, max(blocks)])
            blocks_results[address] = blocks

            impls = list(map(lambda x: x["implementation"], sorted_result))
            impls_results[address] = impls


destroyable_implementations = list()
for address in impls_results:
    for new_impl in impls_results[address]:
        new_impl_abi = load_contract_abi(new_impl)
        if new_impl_abi is not None:
            for abi_func in new_impl_abi:
                if abi_func["type"] == "function":
                    if abi_func["name"] == "destroy" or any([abi_func["name"].startswith(item) for item in ["destruct", "kill"]]):
                        destroyable_implementations.append(
                            (address, new_impl, abi_func["name"], abi_func))


print("================================================================")
print("Summary:")
print("Destroyable implementations:", len(destroyable_implementations))
print("Destroyable implementations (unique):",
      len(set([item[1] for item in destroyable_implementations])))
print("Detailed implementation addresses:")

destroy_json_file = "usccheck/analysis/security_issues_destroyable_implementations_destroyable_proxies.json"
if not os.path.exists(destroy_json_file):
    implementation_destroyable = {}
    proxy_destroyable = {}
    for item in destroyable_implementations:
        proxy_address, impl_address, func_name, abi_func = item
        print("------"*10)
        try:
            print(impl_address, func_name)
            func_call(impl_address, abi_func)
            implementation_destroyable[impl_address] = True
            print("success")
        except:
            if impl_address not in implementation_destroyable:
                implementation_destroyable[impl_address] = False
            print("fail")

        print("------"*10)
        try:
            print(proxy_address, func_name)
            func_call(proxy_address, abi_func)
            proxy_destroyable[proxy_address] = True
            print("success")
        except:
            if proxy_address not in proxy_destroyable:
                proxy_destroyable[proxy_address] = False
            print("fail")

    print("================================================================")
    print("Summary:")
    destroyable_implementations = list(
        [key for key, value in implementation_destroyable.items() if value == True])
    print("destroyable implementations:",
          len(destroyable_implementations))
    destroyable_proxies = list(
        [key for key, value in proxy_destroyable.items() if value == True])
    print("destroyable proxies:", len(destroyable_proxies))

    json.dump({
        "implementation_destroyable_all": implementation_destroyable,
        "destroyable_implementations": destroyable_implementations,
        "destroyable_proxies": destroyable_proxies
    }, open(destroy_json_file, "w"), indent=4)
else:
    print("Destroyable")
    destroy_results = json.load(open(destroy_json_file))
    true_results = dict()
    for key in destroy_results:
        true_results[key] = []
        for addr in destroy_results[key]:
            if code_exists(address=addr):
                print(addr)
                true_results[key].append(addr)

    json.dump(true_results, open(destroy_json_file, "w"), indent=4)


initializable_implementations = list()
for address in impls_results:
    for new_impl in impls_results[address]:
        new_impl_abi = load_contract_abi(new_impl)
        if new_impl_abi is not None:
            for abi_func in new_impl_abi:
                if abi_func["type"] == "function":
                    if abi_func["name"] in ["init", "initialize"]:
                        initializable_implementations.append(
                            (address, new_impl, abi_func["name"], abi_func))


print("================================================================")
print("Summary:")
print("Initializable implementations:", len(initializable_implementations))
print("Initializable implementations (unique):",
      len(set([item[1] for item in initializable_implementations])))
print("Detailed implementation addresses:")

initialize_json_file = "usccheck/analysis/security_issues_un_initalialize_implementations_re_initializable_proxies.json"
if not os.path.exists(initialize_json_file):
    implementation_initalizable = {}
    proxy_re_initalizable = {}
    for item in initializable_implementations:
        proxy_address, impl_address, func_name, abi_func = item
        print("------"*10)
        # if impl_address not in implementation_initalizable:
        try:
            print(impl_address, func_name)
            func_call(impl_address, abi_func)
            implementation_initalizable[impl_address] = True
            print("success")
        except:
            if impl_address not in implementation_initalizable:
                implementation_initalizable[impl_address] = False
            print("fail")

        print("------"*10)
        # if proxy_address not in implementation_initalizable:
        try:
            print(proxy_address, func_name)
            func_call(proxy_address, abi_func)
            proxy_re_initalizable[proxy_address] = True
            print("success")
        except:
            if proxy_address not in proxy_re_initalizable:
                proxy_re_initalizable[proxy_address] = False
            print("fail")

    print("================================================================")
    print("Summary:")
    un_initialize_implementations = list(
        [key for key, value in implementation_initalizable.items() if value == True])
    print("un_initializable implementations:",
          len(un_initialize_implementations))
    re_initialize_proxies = list(
        [key for key, value in proxy_re_initalizable.items() if value == True])
    print("re_initializable proxies:", len(re_initialize_proxies))

    json.dump({
        "un_initalialize_implementations": un_initialize_implementations,
        "re_initializable_proxies": re_initialize_proxies
    }, open(initialize_json_file, "w"), indent=4)

else:
    print("Initialization")
    initialize_results = json.load(open(initialize_json_file))
    true_results = dict()
    for key in initialize_results:
        true_results[key] = []
        for addr in initialize_results[key]:
            if code_exists(address=addr):
                print(addr)
                true_results[key].append(addr)

    json.dump(true_results, open(initialize_json_file, "w"), indent=4)
