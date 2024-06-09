import os
import json
import itertools
import numpy as np
import pandas as pd
import subprocess
import math
from download_abi import download_contract_abi
from decode_transaction_input import decode_transaction_input
from matplotlib import pyplot as plt
from matplotlib_venn import venn3


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

ABI_breaking_change_function_removal = []
ABI_breaking_change_function_parameter_update = []
ABI_breaking_change_function_returns_update = []
for address in impls_results:
    prev_impl = impls_results[address][0]
    for new_impl in impls_results[address][1:]:
        # download_contract_abi(prev_impl)
        # download_contract_abi(new_impl)
        prev_impl_abi = load_contract_abi(prev_impl)
        new_impl_abi = load_contract_abi(new_impl)

        if prev_impl_abi is not None and new_impl_abi is not None:
            # calculate function removals
            for abi_function in prev_impl_abi:
                if abi_function["type"] == "function":
                    abi_function_name = abi_function["name"]
                    if not any([_abi_func["name"] == abi_function_name for _abi_func in new_impl_abi if _abi_func["type"] == "function"]):
                        ABI_breaking_change_function_removal.append(
                            [address, new_impl, prev_impl, abi_function])

            # calculate function parameter modifications
            for abi_function in prev_impl_abi:
                if abi_function["type"] == "function":
                    abi_function_name = abi_function["name"]
                    abi_function_signature = abi_function_name + \
                        "(" + ",".join([_input["type"]
                                        for _input in abi_function["inputs"]])+")"

                    abi_function_parameters = [_input["name"]
                                               for _input in abi_function["inputs"]]
                    if any([_abi_func["name"] == abi_function_name for _abi_func in new_impl_abi if _abi_func["type"] == "function"]):

                        if not any([_abi_func["name"]+"(" + ",".join([_input["type"]
                                                                      for _input in _abi_func["inputs"]])+")" == abi_function_signature for _abi_func in new_impl_abi if _abi_func["type"] == "function"]):
                            ABI_breaking_change_function_parameter_update.append(
                                [address, new_impl, prev_impl, abi_function])
                        else:
                            for _abi_func in new_impl_abi:
                                if _abi_func["type"] == "function":
                                    if abi_function_signature == _abi_func["name"]+"(" + ",".join([_input["type"]
                                                                                                   for _input in _abi_func["inputs"]])+")":
                                        new_abi_function_parameters = [_input["name"]
                                                                       for _input in _abi_func["inputs"]]
                                        if set(abi_function_parameters) == set(new_abi_function_parameters) and new_abi_function_parameters != abi_function_parameters:
                                            # parameter order changes
                                            print("parameter order changes:", abi_function_name,
                                                  abi_function_parameters, "->", new_abi_function_parameters)
                                            ABI_breaking_change_function_parameter_update.append(
                                                [address, new_impl, prev_impl, abi_function])

            # calculate function return types modifications
            for abi_function in prev_impl_abi:
                if abi_function["type"] == "function":
                    abi_function_name = abi_function["name"]
                    abi_function_signature = abi_function_name + \
                        "(" + ",".join([_input["type"]
                                        for _input in abi_function["inputs"]])+")"
                    abi_function_signature_outputs = abi_function_signature + "(" + ",".join([_output["type"]
                                                                                              for _output in abi_function["outputs"]])+")"
                    if any([_abi_func["name"] == abi_function_name for _abi_func in new_impl_abi if _abi_func["type"] == "function"]):

                        if any([_abi_func["name"]+"(" + ",".join([_input["type"]
                                                                  for _input in _abi_func["inputs"]])+")" == abi_function_signature for _abi_func in new_impl_abi if _abi_func["type"] == "function"]):
                            if not any([_abi_func["name"]+"(" + ",".join([_input["type"]
                                                                          for _input in _abi_func["inputs"]])+")" + "(" + ",".join([_output["type"] for _output in _abi_func["outputs"]])+")" == abi_function_signature_outputs for _abi_func in new_impl_abi if _abi_func["type"] == "function"]):

                                ABI_breaking_change_function_returns_update.append(
                                    [address, new_impl, prev_impl, abi_function])


print("================================")
print("Summary:")
print(" ABI breaking changes-removal of functions: ",
      len(ABI_breaking_change_function_removal))
print(" ABI breaking changes-update of function parameters: ",
      len(ABI_breaking_change_function_parameter_update))
print(" ABI breaking changes-modification of function return types: ",
      len(ABI_breaking_change_function_returns_update))


proxies_function_removal = set(
    [item[0] for item in ABI_breaking_change_function_removal])
proxies_parameter_update = set(
    [item[0] for item in ABI_breaking_change_function_parameter_update])
proxies_returns_update = set(
    [item[0] for item in ABI_breaking_change_function_returns_update])
print("================================")
print("Summary:")
print(" ABI breaking changes-removal of functions: ",
      len(proxies_function_removal))
print(" ABI breaking changes-update of function parameters: ",
      len(proxies_parameter_update))
print(" ABI breaking changes-modification of function return types: ",
      len(proxies_returns_update))

# Set font properties
# Use Times New Roman or similar serif font
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 18  # Adjust font size as needed


# Create the Venn diagram
venn = venn3([proxies_function_removal, proxies_parameter_update, proxies_returns_update],
             ('Function\nremoval', 'Parameter\nupdate', 'Return\nchange'), set_colors=("orange", "blue", "red"), alpha=0.5)


# # Display the plot
# # plt.title('ABI breaking changes in the implemenation of proxy contracts')
# plt.show()

# Output the results to a file
plt.savefig('usccheck/analysis/ABI_breaking_changes.pdf', format='pdf')

# close the plot
plt.close()
