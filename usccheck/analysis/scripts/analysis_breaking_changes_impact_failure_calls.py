import os
import json
import itertools
import numpy as np
import pandas as pd
import subprocess
from download_abi import download_contract_abi
from decode_transaction_input import decode_transaction_input


def load_contract_abi(impl):
    abi_file = os.path.join(
        "./usccheck/contract_abi", impl+".abi.json")
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


if not os.path.exists("usccheck/analysis/all_failure_txs_input_including_internal_calls.json"):
    items = os.listdir("usccheck/analysis/proxyfailurecalls")
    df = None
    for item in items:
        _df = pd.read_csv(os.path.join(
            "usccheck/analysis/proxyfailurecalls", item))
        if df is not None:
            df = pd.concat([df, _df], axis=0, ignore_index=True)
        else:
            df = _df

    print(len(df))
    print(df)

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
                # print(sorted_result)
                cnt += 1
                blocks = list(map(lambda x: x["block"], sorted_result))
                max_block = max([max_block, max(blocks)])
                blocks_results[address] = blocks

                impls = list(map(lambda x: x["implementation"], sorted_result))
                impls_results[address] = impls

    failure_inputs = {}
    succ_inputs = {}
    for address in blocks_results:
        # print(address)
        # download_contract_abi(address)
        blocks = blocks_results[address]
        all_selected_item = df[(df["to_address"] == address)]

        failed_all_selected_item = all_selected_item[(
            all_selected_item["error"] == "Reverted")]

        succ_all_selected_item = all_selected_item[(
            all_selected_item["error"] != "Reverted")]

        pre_block = blocks[0]
        for i in range(len(blocks)):
            impl = impls_results[address][i]
            # download_contract_abi(impl)
            pre_block = blocks[i]
            next_block = blocks[i + 1] if i + \
                1 < len(blocks) else max(max_block + 1, 18916002)
            block_count = next_block - pre_block
            tx_count = len(all_selected_item[(all_selected_item["block_number"] > pre_block) & (
                all_selected_item["block_number"] < next_block)])

            failed_selected_item = failed_all_selected_item[(failed_all_selected_item["block_number"] > pre_block) & (
                failed_all_selected_item["block_number"] < next_block)]
            failure_tx_inputs = failed_selected_item["input"].tolist()
            failure_tx_hashes = failed_selected_item["transaction_hash"].tolist(
            )

            failure_clients = failed_selected_item["from_address"].tolist()
            is_client_contracts = [
                trace_address is not None for trace_address in failed_selected_item["trace_address"].tolist()]
            succ_selected_item = succ_all_selected_item[(succ_all_selected_item["block_number"] > pre_block) & (
                succ_all_selected_item["block_number"] < next_block)]
            succ_tx_inputs = succ_selected_item["input"].tolist()
            succ_tx_hashes = succ_selected_item["transaction_hash"].tolist()

            pre_block = next_block

            result = failure_inputs.get(address, [])
            result.append({
                "implementation_address": impl,
                "tx_count": tx_count,
                "block_count": block_count,
                "failure_input": failure_tx_inputs,
                "failure_txs": failure_tx_hashes,
                "succ_input": succ_tx_inputs,
                "succ_txs": succ_tx_hashes,
                "failure_clients": failure_clients,
                "is_client_contracts": is_client_contracts
            })
            failure_inputs[address] = result

    json.dump(failure_inputs, open(
        "usccheck/analysis/all_failure_txs_input_including_internal_calls.json", "w"), indent=4)


if not os.path.exists("usccheck/analysis/all_failure_txs_input_including_internal_calls.statistics.json"):
    # We want to know which functions are likely to contain breaking changes during upgradation.
    # Heuristics are that we select candidate functions with the increased failure rate
    # and then we investigate those functions to determine what breaking changes are introduced
    failure_inputs = json.load(
        open("usccheck/analysis/all_failure_txs_input_including_internal_calls.json"))
    # json.dump(failure_inputs, open(
    #     "usccheck/analysis/all_failure_txs_input.json", "w"), indent=4)

    all_failure_rates = {}
    for proxy_address in failure_inputs:
        all_failure_rates[proxy_address] = {}
        version = 0
        while version < len(failure_inputs[proxy_address]):
            all_failure_rates[proxy_address][version] = {}

            item = failure_inputs[proxy_address][version]
            block_count = item["block_count"]
            _failure_inputs = item["failure_input"]
            _succ_inputs = item["succ_input"]

            function_call_failure_statistics = {}
            for failure_input in _failure_inputs:
                function_call_failure_statistics[failure_input[:10]] = function_call_failure_statistics.get(
                    failure_input[:10], 0) + 1

            function_call_succ_statistics = {}
            for succ_input in _succ_inputs:
                function_call_succ_statistics[succ_input[:10]] = function_call_succ_statistics.get(
                    succ_input[:10], 0) + 1

            failure_rates = {}
            func_selectors = set(function_call_failure_statistics.keys()).union(
                set(function_call_succ_statistics.keys()))
            for func_selector in func_selectors:
                failure_count = function_call_failure_statistics.get(
                    func_selector, 0)
                succ_count = function_call_succ_statistics.get(
                    func_selector, 0)
                failure_rate = failure_count / (failure_count + succ_count)
                failure_rates[func_selector] = failure_rate

            item["function_call_failure_statistics"] = function_call_failure_statistics
            item["function_call_succ_statistics"] = function_call_succ_statistics
            item["failure_rates"] = failure_rates
            version += 1

    json.dump(failure_inputs, open(
        "usccheck/analysis/all_failure_txs_input_including_internal_calls.statistics.json", "w"), indent=4)

if not os.path.exists("./usccheck/analysis/candidate_breaking_function_txs_function_removal_modification_including_internal_calls.json"):
   # breaking change classification
   #  1. functions are removed. that same-name function is removed
   #  2. function parameters are modified, i.e. new types, new parameters, deleted parameters.
   #  3. function signatures remain unchanged but functionality is changed.
   #  which may correspond to higher function failure rates

    def is_removed_function(function_input, previous_impl, new_impl):
        prev_impl_abi = load_contract_abi(previous_impl)
        new_impl_abi = load_contract_abi(new_impl)

        ret = decode_transaction_input(prev_impl_abi, function_input)
        if ret is not None:
            target_func = ret["func"]
            func_full_signature = target_func["name"]+"(" + ",".join(
                [_input["type"] for _input in target_func["inputs"]])+")"
            for item in new_impl_abi:
                if item["type"] == "function":
                    _func_full_signature = item["name"]+"(" + ",".join(
                        [_input["type"] for _input in item["inputs"]])+")"
                    if target_func["name"] == item["name"]:
                        return False
        return True

    def is_modified_function(function_input, previous_impl, new_impl):
        prev_impl_abi = load_contract_abi(previous_impl)
        new_impl_abi = load_contract_abi(new_impl)

        ret = decode_transaction_input(prev_impl_abi, function_input)
        if ret is not None:
            target_func = ret["func"]
            func_full_signature = target_func["name"]+"(" + ",".join(
                [_input["type"] for _input in target_func["inputs"]])+")"
            for item in new_impl_abi:
                if item["type"] == "function":
                    _func_full_signature = item["name"]+"(" + ",".join(
                        [_input["type"] for _input in item["inputs"]])+")"
                    if target_func["name"] == item["name"]:
                        return True
        return False

    def belongs_to_prev_impl(function_input, previous_impls, new_impl):
        new_impl_abi = load_contract_abi(new_impl)
        if new_impl_abi is not None:
            ret = decode_transaction_input(new_impl_abi, function_input)
            if ret is None:
                for previous_impl in previous_impls:
                    previous_impl_abi = load_contract_abi(previous_impl)
                    ret = decode_transaction_input(
                        previous_impl_abi, function_input)
                    if ret is not None:
                        return True, previous_impl
        return False, None

    failure_inputs = json.load(
        open("usccheck/analysis/all_failure_txs_input_including_internal_calls.statistics.json"))

    candidate_breaking_function_txs = []
    all_failure_rates = []
    removed_function_failure_txs = {}
    modified_function_failure_txs = {}
    txs_removed = list()
    txs_modified = list()
    for proxy_address in failure_inputs:
        version = 1
        removed_function_failure_txs[proxy_address] = dict()
        modified_function_failure_txs[proxy_address] = dict()
        while version < len(failure_inputs[proxy_address]):
            print(proxy_address, version)
            removed_function_failure_txs[proxy_address][version] = []
            modified_function_failure_txs[proxy_address][version] = []
            item = failure_inputs[proxy_address][version]

            previous_impls = []
            prev_version = version - 1
            while prev_version >= 0:
                prev_item = failure_inputs[proxy_address][prev_version]
                prev_impl = prev_item["implementation_address"]
                previous_impls.append(prev_impl)
                prev_version -= 1

            new_impl = item["implementation_address"]

            # for func_input in item["failure_input"]:
            for i in range(len(item["failure_input"])):
                func_input = item["failure_input"][i]
                tx_hash = item["failure_txs"][i]
                flag, prev_impl = belongs_to_prev_impl(
                    func_input, previous_impls=previous_impls, new_impl=new_impl)
                if flag is True:
                    if is_removed_function(func_input, prev_impl, new_impl):
                        removed_function_failure_txs[proxy_address][version].append(
                            [func_input, {
                                "tx_hash": tx_hash,
                                "prev_impl": prev_impl,
                                "new_impl": new_impl,
                                "decoded_input": decode_transaction_input(load_contract_abi(prev_impl), func_input)
                            }])
                        txs_removed.append(tx_hash)
                    else:
                        modified_function_failure_txs[proxy_address][version].append(
                            [func_input, {
                                "tx_hash": tx_hash,
                                "prev_impl": prev_impl,
                                "new_impl": new_impl,
                                "decoded_input": decode_transaction_input(load_contract_abi(prev_impl), func_input)
                            }])
                        txs_modified.append(tx_hash)

            if len(removed_function_failure_txs[proxy_address][version]) == 0:
                removed_function_failure_txs[proxy_address].pop(version)

            if len(modified_function_failure_txs[proxy_address][version]) == 0:
                modified_function_failure_txs[proxy_address].pop(version)

            version += 1
        if len(removed_function_failure_txs[proxy_address]) == 0:
            removed_function_failure_txs.pop(proxy_address)

        if len(modified_function_failure_txs[proxy_address]) == 0:
            modified_function_failure_txs.pop(proxy_address)

    print("Summary:")
    print("count of modified functions usage:", len(txs_modified))
    print("count of modified functions usage (unique txs):", len(set(txs_modified)))
    print("count of removed functions usage:", len(txs_removed))
    print("count of removed functions usage (unique txs):", len(set(txs_removed)))

    print("total txs (unique):", len(set(txs_modified + txs_removed)))

    json.dump({
        "removed_function_failure_txs": removed_function_failure_txs,
        "modified_function_failure_txs": modified_function_failure_txs
    }, open("./usccheck/analysis/candidate_breaking_function_txs_function_removal_modification_including_internal_calls.json", "w"), indent=4)
