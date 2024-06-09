
import sys
import os
import json
import traceback
from infura import get_implementation

query_count = 0


def get_implementations(chain, network, address, start_block=1):
    global query_count
    result = []
    latest_impl, latest_block = get_implementation(
        chain=chain, network=network, address=address)
    result.append(dict(implementation=latest_impl, block=latest_block))
    default_impl, default_impl_block = get_implementation(
        chain=chain, network=network, address=address, block=start_block)
    if default_impl != None and default_impl != latest_impl:
        result.append(dict(implementation=default_impl,
                      block=default_impl_block))
    query_count = 2

    def binary_search_new_implementation(start_block, end_block, left_impl, right_impl):
        global query_count
        if start_block >= end_block:
            return
        elif left_impl == right_impl:
            return
        else:
            mid_block = int((end_block+start_block)/2)
            mid_block_impl, _ = get_implementation(
                chain=chain, network=network, address=address, block=mid_block)
            query_count += 1
            if mid_block_impl == right_impl:
                binary_search_new_implementation(
                    start_block=start_block, end_block=mid_block-1, left_impl=left_impl, right_impl=mid_block_impl)
            elif mid_block_impl == left_impl:
                binary_search_new_implementation(
                    start_block=mid_block+1, end_block=end_block, left_impl=mid_block_impl, right_impl=right_impl)
            else:
                result.append(
                    dict(implementation=mid_block_impl, block=mid_block))
                binary_search_new_implementation(
                    start_block=start_block, end_block=mid_block-1, left_impl=left_impl, right_impl=mid_block_impl)
                binary_search_new_implementation(
                    start_block=mid_block+1, end_block=end_block, left_impl=mid_block_impl, right_impl=right_impl)

    binary_search_new_implementation(
        start_block=start_block, end_block=latest_block, left_impl=default_impl, right_impl=latest_impl)
    return result


def main():
    global query_count
    args = sys.argv[1:]
    chain_network_file = args[0]
    address = args[1]
    result_dir = args[2]
    start_block = None if len(args) < 3 else int(args[3])
    try:
        chain, network = os.path.basename(
            chain_network_file).split(".txt")[0].split("_")
        result = get_implementations(
            chain=chain, network=network, address=address, start_block=start_block)
        print(address, result, query_count)
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)
        if not os.path.exists(os.path.join(result_dir, chain+"_"+network)):
            os.mkdir(os.path.join(result_dir, chain+"_"+network))
        json.dump(result, open(os.path.join(result_dir, chain+"_" +
                  network, address+".implementations.json"), "w"))
    except:
        # traceback.print_exc()
        print(f"Error in processing {address}")


if __name__ == "__main__":
    main()


def test():
    result = get_implementations(
        chain="ethereum", network="mainnet", address="0x25200235ca7113c2541e70de737c41f5e9acd1f6")
    print(result, query_count)
