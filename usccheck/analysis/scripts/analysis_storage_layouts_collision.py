import os
import json
import itertools
import numpy as np
import pandas as pd
import subprocess


def test_pre_impl_storage_included_new_impl(pre_impl_storage, new_impl_storage):
    pre_storageLayout = pre_impl_storage["storageLayout"]
    new_storageLayout = new_impl_storage["storageLayout"]

    if pre_storageLayout is None or new_storageLayout is None:
        return True, "No storage layout specified"

    if not ("storage" in pre_storageLayout and "storage" in new_storageLayout):
        return True, "No storage layout specified"

    if len(pre_storageLayout["storage"]) > len(new_storageLayout["storage"]):
        return False, "Error: Some state variables are removed"

    for i in range(len(pre_storageLayout["storage"])):
        pre_state_variable = pre_storageLayout["storage"][i]
        new_state_variable = new_storageLayout["storage"][i]
        if new_state_variable["label"].lower().find(pre_state_variable["label"].lower()) != -1:
            if pre_storageLayout["types"][pre_state_variable["type"]] != pre_storageLayout["types"][pre_state_variable["type"]]:
                return False, "Error: state variable type mismatch between " + pre_state_variable["label"] + " " + new_state_variable["label"]
        else:
            return False, "Error: state variable name largely mismatch between " + pre_state_variable["label"] + " " + new_state_variable["label"]

    return True, "Storage layout remain compatible with previous storage"


def download_src_storage_layout(impl):
    output_file = os.path.join(
        "./usccheck/contract_storage_layout", impl.lower()+".json")
    export_dir = "./usccheck/contract_code"
    cmd = ""
    cmd += "bash usccheck/analysis/scripts/download_src_storage_abi.sh {0} {1} {2}".format(
        impl, export_dir, output_file)
    print(cmd)
    exit_code = os.system(cmd)
    # print(exit_code)
    if os.path.exists(output_file):
        return json.load(open(output_file))
    else:
        return None


def compute_storage_layout(impl):
    artifact_file = os.path.join(
        "./usccheck/contract_storage_layout", impl.lower()+".json")
    if impl == "0x0000000000000000000000000000000000000000" or impl == "0x0" or impl == "0x":
        return None
    if os.path.exists(artifact_file):
        return json.load(open(artifact_file))
    else:
        return download_src_storage_layout(impl)


def load_storage_layout(impl):
    artifact_file = os.path.join(
        "./usccheck/contract_storage_layout", impl.lower()+".json")
    if impl == "0x0000000000000000000000000000000000000000" or impl == "0x0" or impl == "0x":
        return None
    if os.path.exists(artifact_file):
        return json.load(open(artifact_file))
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


storage_collision_results = []
for address in impls_results:
    cnt = 0
    pre_impl = None
    pre_impl_storage = None
    for new_impl in impls_results[address]:
        print(address, cnt, new_impl)
        # new_impl_storage = compute_storage_layout(new_impl)
        new_impl_storage = compute_storage_layout = load_storage_layout(
            new_impl)

        if pre_impl_storage is not None and new_impl_storage is not None:
            isIncluded, errorMsg = test_pre_impl_storage_included_new_impl(
                pre_impl_storage, new_impl_storage)

            if not isIncluded:
                storage_collision_results.append(
                    [address, pre_impl, new_impl, errorMsg])

        pre_impl_storage = new_impl_storage
        pre_impl = new_impl
        # exit(0)
        cnt += 1

print("=="*20)
print("Summary:")
print("Storage Collision results:", len(storage_collision_results))
print("Details:", "\n".join([" ".join(item)
      for item in storage_collision_results]))

json.dump(storage_collision_results, open(
    "usccheck/analysis/security_issues_storage_collision.json", "w"), indent=4)
