import os
import json
import itertools
import numpy as np
import pandas as pd
import subprocess
import math
from download_abi import download_contract_abi
from decode_transaction_input import decode_transaction_input


def load_contract_abi(impl):
    abi_file = os.path.join(
        "./usccheck/contract_abi", impl.lower()+".abi.json")
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


if not os.path.exists("usccheck/analysis/all_failure_txs_input_succall_failtxs.json"):
    items = os.listdir("usccheck/analysis/proxysuccCallsFailureTxs")
    df = None
    for item in items:
        _df = pd.read_csv(os.path.join(
            "usccheck/analysis/proxysuccCallsFailureTxs", item))
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
            all_selected_item["error"] == "Reverted")]

        succ_all_selected_item = all_selected_item[(
            all_selected_item["error"] != "Reverted")]

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
            failure_clients = failed_selected_item["from_address"].tolist()
            is_client_contracts = [
                trace_address is not None for trace_address in failed_selected_item["trace_address"].tolist()]
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
                "succ_input": succ_tx_inputs,
                "failure_clients": failure_clients,
                "is_client_contracts": is_client_contracts
            })
            failure_inputs[address] = result

    json.dump(failure_inputs, open(
        "usccheck/analysis/all_failure_txs_input_succall_failtxs.json", "w"), indent=4)


if not os.path.exists("usccheck/analysis/all_failure_txs_input_succall_failtxs.statistics.json"):
    # We want to know which functions are likely to contain breaking changes during upgradation.
    # Heuristics are that we select candidate functions with the increased failure rate
    # and then we investigate those functions to determine what breaking changes are introduced
    failure_inputs = json.load(
        open("usccheck/analysis/all_failure_txs_input_succall_failtxs.json"))
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
                selector = succ_input[:10] if isinstance(
                    succ_input, str) or not math.isnan(succ_input) else "0x"
                function_call_succ_statistics[selector] = function_call_succ_statistics.get(
                    selector, 0) + 1

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
        "usccheck/analysis/all_failure_txs_input_succall_failtxs.statistics.json", "w"), indent=4)


if not os.path.exists("./usccheck/analysis/candidate_breaking_function_txs_function_returntypes_modification_only_internal_calls.json"):
   # breaking change classification
   #  3. Client Contract-> Proxy Contract -> Implementation...
   #  return types changes may impact on client contract compatibility

    def belongs_to_prev_new_impl_but_differ_in_return_types(function_input, previous_impl, new_impl):
        new_impl_abi = load_contract_abi(new_impl)
        if new_impl_abi is not None:
            ret1 = decode_transaction_input(new_impl_abi, function_input)
            if ret1 is not None:
                previous_impl_abi = load_contract_abi(previous_impl)
                if previous_impl_abi is not None:
                    ret2 = decode_transaction_input(
                        previous_impl_abi, function_input)

                    if ret2 is not None:
                        ret1_return_types = tuple([item["type"]
                                                   for item in ret1["func"]["outputs"]])
                        ret2_return_types = tuple([item["type"]
                                                   for item in ret2["func"]["outputs"]])

                        if ret1_return_types != ret2_return_types:
                            return True
        return False

    failure_inputs = json.load(
        open("usccheck/analysis/all_failure_txs_input_succall_failtxs.statistics.json"))

    candidate_breaking_function_txs = []
    all_failure_rates = []
    modified_function_failure_txs = {}
    for proxy_address in failure_inputs:
        version = 1
        modified_function_failure_txs[proxy_address] = dict()
        while version < len(failure_inputs[proxy_address]):
            print(proxy_address, version)
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

            for i in range(len(item["succ_input"])):
                func_input = item["succ_input"][i]

                flag = belongs_to_prev_new_impl_but_differ_in_return_types(
                    func_input, previous_impl=previous_impls[0], new_impl=new_impl)
                if flag is True:
                    modified_function_failure_txs[proxy_address][version].append(
                        [func_input, {
                            "prev_impl": previous_impls[0],
                            "new_impl": new_impl,
                            "decoded_input": decode_transaction_input(load_contract_abi(previous_impls[0]), func_input)
                        }])

            if len(modified_function_failure_txs[proxy_address][version]) == 0:
                modified_function_failure_txs[proxy_address].pop(version)

            version += 1

        if len(modified_function_failure_txs[proxy_address]) == 0:
            modified_function_failure_txs.pop(proxy_address)

    json.dump({
        "modified_function_returntypes_failure_txs": modified_function_failure_txs
    }, open("./usccheck/analysis/candidate_breaking_function_txs_function_returntypes_modification_only_internal_calls.json", "w"), indent=4)
