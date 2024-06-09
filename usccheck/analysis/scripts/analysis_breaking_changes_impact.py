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


if not os.path.exists("usccheck/analysis/all_failure_txs_input.json"):
    items = os.listdir("usccheck/analysis/fulldata")
    df = None
    for item in items:
        _df = pd.read_csv(os.path.join("usccheck/analysis/fulldata", item))
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
        download_contract_abi(address)
        blocks = blocks_results[address]
        all_selected_item = df[(df["to_address"] == address)]

        failed_all_selected_item = all_selected_item[(
            all_selected_item["receipt_status"] == 0)]

        succ_all_selected_item = all_selected_item[(
            all_selected_item["receipt_status"] == 1)]

        pre_block = blocks[0]
        for i in range(len(blocks)):
            impl = impls_results[address][i]
            download_contract_abi(impl)
            pre_block = blocks[i]
            next_block = blocks[i + 1] if i + \
                1 < len(blocks) else max(max_block + 1, 18916002)
            block_count = next_block - pre_block
            tx_count = len(all_selected_item[(all_selected_item["block_number"] > pre_block) & (
                all_selected_item["block_number"] < next_block)])

            failed_selected_item = failed_all_selected_item[(failed_all_selected_item["block_number"] > pre_block) & (
                failed_all_selected_item["block_number"] < next_block)]
            failure_tx_inputs = failed_selected_item["input"].tolist()
            succ_selected_item = succ_all_selected_item[(succ_all_selected_item["block_number"] > pre_block) & (
                succ_all_selected_item["block_number"] < next_block)]
            succ_tx_inputs = succ_selected_item["input"].tolist()

            pre_block = next_block

            result = failure_inputs.get(address, [])
            result.append({
                "implementation_address": impl,
                "tx_count": tx_count,
                "block_count": block_count,
                "failure_input": failure_tx_inputs,
                "succ_input": succ_tx_inputs
            })
            failure_inputs[address] = result

    json.dump(failure_inputs, open(
        "usccheck/analysis/all_failure_txs_input.json", "w"), indent=4)

elif not os.path.exists("usccheck/analysis/failure_rate_10_percent.json"):
    # We want to know which functions are likely to contain breaking changes during upgradation.
    # Heuristics are that we select candidate functions with the increased failure rate
    # and then we investigate those functions to determine what breaking changes are introduced
    #
    failure_inputs = json.load(
        open("usccheck/analysis/all_failure_txs_input.json"))
    # json.dump(failure_inputs, open(
    #     "usccheck/analysis/all_failure_txs_input.json", "w"), indent=4)

    failure_rate_10_percent = []
    all_failure_rates = []
    for proxy_address in failure_inputs:
        version = 1
        while version < len(failure_inputs[proxy_address]):
            item = failure_inputs[proxy_address][version]
            block_count = item["block_count"]
            _failure_inputs = item["failure_input"]

            tx_count = item["tx_count"]
            if tx_count == 0:
                failure_rate = 0
            else:
                failure_rate = len(_failure_inputs)/tx_count
            all_failure_rates.append(failure_rate)

            prev_success_inputs = failure_inputs[proxy_address][version-1]["succ_input"]
            prev_succ_function_selectors = list()
            for succ_input in prev_success_inputs:
                if succ_input == "0x0":
                    prev_succ_function_selectors.append("fallback")
                else:
                    prev_succ_function_selectors.append(
                        succ_input[:10].lower())

            candiate_breaking_function_selectors = {}
            for failure_input in _failure_inputs:
                if failure_input == "0x0":
                    if "fallback" in prev_succ_function_selectors:
                        candiate_breaking_function_selectors[failure_input] = "fallback"
                else:
                    if failure_input[:10].lower() in prev_succ_function_selectors:
                        if failure_input[:10].lower() in candiate_breaking_function_selectors:
                            continue
                        url = "https://www.4byte.directory/api/v1/signatures/?hex_signature={0}".format(
                            failure_input[:10])
                        result = run_curl_command(url)
                        result = json.loads(result)
                        candiate_breaking_function_selectors[failure_input[:10]] = [
                            item["text_signature"] for item in result["results"]]

            if failure_rate > 0.1:
                failure_rate_10_percent.append({
                    "proxy": proxy_address,
                    "implementation_version": version,
                    "failure_rate": failure_rate,
                    "candidate_breaking_function_selectors": candiate_breaking_function_selectors,
                    "txs": item
                })
            version += 1

    nparray = np.array(all_failure_rates)
    for threshold in range(0, 10):
        print("Threshold(%f): %d" % (threshold*0.1, np.sum(
            nparray is not None and nparray > threshold*0.1)))

    json.dump(failure_rate_10_percent, open(
        "usccheck/analysis/failure_rate_10_percent.json", "w"), indent=4)
elif not os.path.exists("usccheck/analysis/all_failure_txs_input.statistics.json"):
    # We want to know which functions are likely to contain breaking changes during upgradation.
    # Heuristics are that we select candidate functions with the increased failure rate
    # and then we investigate those functions to determine what breaking changes are introduced
    failure_inputs = json.load(
        open("usccheck/analysis/all_failure_txs_input.json"))
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
        "usccheck/analysis/all_failure_txs_input.statistics.json", "w"), indent=4)

elif not os.path.exists("usccheck/analysis/candidate_breaking_function_txs_function_update.json"):
    failure_inputs = json.load(
        open("usccheck/analysis/all_failure_txs_input.statistics.json"))

    candidate_breaking_function_txs = []
    all_failure_rates = []
    for proxy_address in failure_inputs:
        version = 1
        proxy_abi = load_contract_abi(proxy_address)
        while version < len(failure_inputs[proxy_address]):
            print(proxy_address, version)
            item = failure_inputs[proxy_address][version]
            prev_item = failure_inputs[proxy_address][version -
                                                      1]
            failure_rates = item["failure_rates"]

            prev_failure_rates = prev_item["failure_rates"]

            common_func_selectors = set(failure_rates.keys()).intersection(
                set(prev_failure_rates.keys()))

            prev_impl = prev_item["implementation_address"]
            new_impl = item["implementation_address"]

            prev_impl_abi = load_contract_abi(prev_impl)
            new_impl_abi = load_contract_abi(new_impl)

            candiate_breaking_function_selectors = {}
            for func_selector in common_func_selectors:
                if item["function_call_failure_statistics"].get(func_selector, 0) + item["function_call_succ_statistics"].get(func_selector, 0) < 3:
                    continue
                if prev_item["function_call_failure_statistics"].get(func_selector, 0) + prev_item["function_call_succ_statistics"].get(func_selector, 0) < 3:
                    continue
                if failure_rates[func_selector] > prev_failure_rates[func_selector] + 0.02:
                    if new_impl_abi is None:
                        url = "https://www.4byte.directory/api/v1/signatures/?hex_signature={0}".format(
                            func_selector)
                        result = run_curl_command(url)
                        result = json.loads(result)
                        candiate_breaking_function_selectors[func_selector] = {
                            "prev_failure_rate": prev_failure_rates[func_selector],
                            "cur_failure_rate": failure_rates[func_selector],
                            "text_signature":   [
                                item["text_signature"] for item in result["results"]]
                        }
                    else:
                        func_abi = None
                        failure_tx_inputs = []
                        for func_input in item["failure_input"]:
                            if func_input[:10].lower() == func_selector:
                                decoded_result = decode_transaction_input(
                                    new_impl_abi, func_input)
                                if decoded_result is None:
                                    decoded_result = decode_transaction_input(
                                        proxy_abi, func_input)

                                if decoded_result is None:
                                    failure_tx_inputs.append({
                                        "raw_input": func_input,
                                        "decoded_inputs": "Unknown"
                                    }
                                    )
                                    func_abi = None
                                else:

                                    func_abi = decoded_result["func"]
                                    decoded_inputs = decoded_result["inputs"]
                                    failure_tx_inputs.append({
                                        "raw_input": func_input,
                                        "decoded_inputs": decoded_inputs
                                    }
                                    )
                        candiate_breaking_function_selectors[func_selector] = {
                            "prev_failure_rate": prev_failure_rates[func_selector],
                            "cur_failure_rate": failure_rates[func_selector],
                            "abi_function": func_abi,
                            "failure_tx_inputs": failure_tx_inputs
                        }
            if len(candiate_breaking_function_selectors) > 0:
                candidate_breaking_function_txs.append({
                    "proxy": proxy_address,
                    "implementation_version": version,
                    "prev_implementation_address": prev_impl,
                    "new_implementation_address": new_impl,
                    "failure_rate": failure_rates,
                    "candidate_breaking_function_selectors": candiate_breaking_function_selectors
                })
            version += 1

    json.dump(candidate_breaking_function_txs, open(
        "usccheck/analysis/candidate_breaking_function_txs_function_update.json", "w"), indent=4)
else:
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
        open("usccheck/analysis/all_failure_txs_input.statistics.json"))

    candidate_breaking_function_txs = []
    all_failure_rates = []
    removed_function_failure_txs = {}
    modified_function_failure_txs = {}
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

            for func_input in item["failure_input"]:
                flag, prev_impl = belongs_to_prev_impl(
                    func_input, previous_impls=previous_impls, new_impl=new_impl)
                if flag is True:
                    if is_removed_function(func_input, prev_impl, new_impl):
                        removed_function_failure_txs[proxy_address][version].append(
                            [func_input, {
                                "prev_impl": prev_impl,
                                "new_impl": new_impl,
                                "decoded_input": decode_transaction_input(load_contract_abi(prev_impl), func_input)
                            }])
                    else:
                        modified_function_failure_txs[proxy_address][version].append(
                            [func_input, {
                                "prev_impl": prev_impl,
                                "new_impl": new_impl,
                                "decoded_input": decode_transaction_input(load_contract_abi(prev_impl), func_input)
                            }])

            if len(removed_function_failure_txs[proxy_address][version]) == 0:
                removed_function_failure_txs[proxy_address].pop(version)

            if len(modified_function_failure_txs[proxy_address][version]) == 0:
                modified_function_failure_txs[proxy_address].pop(version)

            version += 1
        if len(removed_function_failure_txs[proxy_address]) == 0:
            removed_function_failure_txs.pop(proxy_address)

        if len(modified_function_failure_txs[proxy_address]) == 0:
            modified_function_failure_txs.pop(proxy_address)

    json.dump({
        "removed_function_failure_txs": removed_function_failure_txs,
        "modified_function_failure_txs": modified_function_failure_txs
    }, open("./usccheck/analysis/candidate_breaking_function_txs_function_removal_modification.json", "w"), indent=4)
