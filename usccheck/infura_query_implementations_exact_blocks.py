
import sys
import os
import json
import traceback
from infura import get_implementation
from datetime import datetime, date, timedelta


def is_modified_recently(file_path):
    # Get the modification timestamp of the file
    modification_timestamp = os.path.getmtime(file_path)

    # Convert the timestamp to a datetime object
    modification_date = datetime.fromtimestamp(modification_timestamp).date()

    # Get today's date
    today = date.today()

    yesterday = datetime.now().date() - timedelta(days=1)

    if modification_date == today or modification_date == yesterday:
        return True
    else:
        return False


def get_implementations_exact_block(chain, network, address, left_impl, right_impl, start_block, end_block):
    if right_impl == "0x":
        print("Null implementation and so use infura query count: ", 0)
        return end_block

    def binary_search_new_implementation_block(start_block, end_block, left_impl, right_impl, query_count):
        if start_block >= end_block:
            return end_block, query_count
        else:
            mid_block = int((end_block+start_block)/2)
            mid_block_impl, _ = get_implementation(
                chain=chain, network=network, address=address, block=mid_block)

            if mid_block_impl == "0x":
                mid_block_impl = None

            query_count += 1
            if mid_block_impl == right_impl:
                return binary_search_new_implementation_block(
                    start_block=start_block+1, end_block=mid_block, left_impl=left_impl, right_impl=right_impl, query_count=query_count)
            elif mid_block_impl == left_impl:
                return binary_search_new_implementation_block(
                    start_block=mid_block+1, end_block=end_block, left_impl=left_impl, right_impl=right_impl, query_count=query_count)
            else:
                # assert False, "Invalid mid_block_impl"
                print("Invalid mid_block_impl")
                return end_block, query_count

    exact_block, query_count = binary_search_new_implementation_block(
        start_block=start_block, end_block=end_block, left_impl=left_impl, right_impl=right_impl, query_count=0)
    print("Used infura query count: ", query_count)
    return exact_block


proxy_implementation_dir = "usccheck/OnchainContractData/proxy_implementations/ethereum_mainnet/"

cnt = 0
impls_results = {}
refined_cnt = 0
for item in os.listdir(proxy_implementation_dir):
    if item.endswith(".json"):
        address = item.split(".implementations.json")[0]

        if is_modified_recently(os.path.join(proxy_implementation_dir, item)):
            refined_cnt += 1
            print(refined_cnt, " have refined the result:", os.path.join(
                proxy_implementation_dir, item))
            continue

        result = json.load(open(os.path.join(proxy_implementation_dir, item)))

        if len(result) > 1:
            sorted_result = sorted(result, key=lambda x: x["block"])
            # print(sorted_result)

            previous_impl = None
            start_block = 1

            impl_blocks = []
            print("Proxy#{0}: {1}".format(cnt, address))
            for impl in sorted_result:
                print(impl["implementation"])
                upgradation_block = get_implementations_exact_block(
                    "ethereum", "mainnet", address, previous_impl, impl["implementation"], start_block=start_block, end_block=impl["block"])
                if impl["block"] != upgradation_block:
                    print(impl["block"], "-->", upgradation_block)

                impl["block"] = upgradation_block
                impl_blocks.append(impl)

                previous_impl = impl["implementation"]
                start_block = impl["block"]

            json.dump(impl_blocks, open(
                os.path.join(proxy_implementation_dir, item), "w"), indent=4)

            cnt += 1
            impls_results[address] = sorted_result

print(len(impls_results), "proxy contracts")

# query_count = 0


# results = {}

# for proxy_address in impls_results:
#     impls = impls_results[proxy_address]
#     previous_impl = None
#     start_block = 1

#     impl_blocks = []
#     print("Proxy:", proxy_address)
#     for impl in impls:
#         print(impl["implementation"])
#         upgradation_block = get_implementations_exact_block(
#             "ethereum", "mainnet", proxy_address, previous_impl, impl["implementation"], start_block=start_block, end_block=impl["block"])
#         if impl["block"] != upgradation_block:
#             print(impl["block"], "-->", upgradation_block)

#         impl["block"] = upgradation_block
#         impl_blocks.append(impl)

#         previous_impl = impl["implementation"]
#         start_block = impl["block"]

#     results[proxy_address] = impl_blocks


# json.dump(results, open(
#     "usccheck/OnchainContractData/proxy_implementations/etherscan_mainnet.exact.full.statistics.json", "w"), indent=4)
