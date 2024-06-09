import os
import math
import json
import itertools
import matplotlib.pyplot as plt
import numpy as np

proxy_implementation_dir = "usccheck/OnchainContractData/proxy_implementations/ethereum_mainnet/"

PlotChart = True
BarChart = True
if PlotChart:
    cnt = 0
    blocks_results = []
    proxy_results = {}
    for item in os.listdir(proxy_implementation_dir):
        if item.endswith(".json"):
            proxy_address = item.split(".")[0]
            result = json.load(
                open(os.path.join(proxy_implementation_dir, item)))
            # if len(result) > 1:
            sorted_result = sorted(result, key=lambda x: x["block"])
            # print(sorted_result)
            cnt += 1

            blocks = list(filter(lambda x: x["implementation"] is not None and x["implementation"] !=
                                 "" and x["implementation"] != "0x" and int(x["implementation"], base=16) != 0, sorted_result))
            if len(blocks) >= 2:  # for plot chart for upgraded proxies
                blocks_results.append(blocks)
                proxy_results[proxy_address] = sorted_result[0]["block"]

    print(len(blocks_results), "proxy contracts")

    # Implementation contracts
    # y - number of implementations
    # x - block number

    # Sample data (replace this with your data)
    all_blocks = list(itertools.chain.from_iterable(blocks_results))
    # data = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5]
    print(len(all_blocks), " implementation contracts")
    print(len(set(map(lambda item: item["implementation"],
          all_blocks))), " implementation contracts (unique)")
    min_all_blocks = min([item["block"] for item in all_blocks])
    max_all_blocks = max([item["block"] for item in all_blocks])
    print("min(all_blocks):", min_all_blocks)
    print("max(all_blocks):", max_all_blocks)

    firstProxyBlk = min([value for key, value in proxy_results.items()])
    lastProxyBlk = max([value for key, value in proxy_results.items()])
    print("firstProxyBlk:", firstProxyBlk)
    print("lastProxyBlk:", lastProxyBlk)

    data = list(range(min_all_blocks, max_all_blocks+200000, 200000))

    # Calculate number of implementations
    value_counts_impl = {}
    for value in data:
        value_counts_impl[value] = len(
            list(filter(lambda x: x["block"] <= value, all_blocks)))

    value_counts_impl_unique = {}
    for value in data:
        value_counts_impl_unique[value] = len(set(
            map(lambda x: x["implementation"], filter(lambda x: x["block"] <= value, all_blocks))))

    value_counts_proxy = {}
    for value in data:
        value_counts_proxy[value] = len(
            list(filter(lambda x: proxy_results[x] <= value, proxy_results)))

    # Extract values and number of implementations
    values = list(value_counts_impl.keys())
    implementations = list(value_counts_impl.values())

    implementations_unique = list(value_counts_impl_unique.values())

    # Set font properties
    # Use Times New Roman or similar serif font
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.size'] = 12  # Adjust font size as needed

    # Create the figure and the primary y-axis
    fig, ax1 = plt.subplots()

    # Create a scatter plot
    ax1.plot(values, implementations, '-', label='Proxy-Impl Pairs')
    # Create a scatter plot
    ax1.plot(values, implementations_unique, '-', label='Impls (Unique)')

    values = list(value_counts_impl.keys())
    proxies = list(value_counts_proxy.values())

    ax1.plot(values, proxies, '-', label='Proxies')

    ax1.set_xlabel('#Block')
    ax1.set_ylabel('#Contract')
    ax1.tick_params(axis='y')

    # # Create the secondary y-axis
    # ax2 = ax1.twinx()

    # # ratio: #Implementations/#Proxy
    # ratio = np.array(implementations) / np.array(proxies)
    # ax2.plot(values, ratio, 'r.-')

    # ax2.set_ylabel('#Pairs per Proxy')
    # ax2.tick_params(axis='y', labelcolor='r')

    # Add legends for both y-axes
    ax1.legend(loc='upper left')
    # ax2.legend(loc='upper center')

    # # Add labels and title
    # plt.ylabel('#Contract')
    # plt.title('Proxy & Implementation contracts')

    # Output the results to a file
    plt.savefig('usccheck/analysis/proxy_impl_number.pdf', format='pdf')

    # close the plot
    plt.close()


if BarChart:
    cnt = 0
    blocks_results = []
    proxy_results = {}
    for item in os.listdir(proxy_implementation_dir):
        if item.endswith(".json"):
            proxy_address = item.split(".")[0]
            result = json.load(
                open(os.path.join(proxy_implementation_dir, item)))
            # if len(result) > 1:
            sorted_result = sorted(result, key=lambda x: x["block"])
            # print(sorted_result)
            cnt += 1

            blocks = list(filter(lambda x: x["implementation"] is not None and x["implementation"] !=
                                 "" and x["implementation"] != "0x" and int(x["implementation"], base=16) != 0, sorted_result))
            if len(blocks) >= 0:  # for bar chart for upgrading frequency
                blocks_results.append(blocks)
                proxy_results[proxy_address] = sorted_result[0]["block"]

    print(len(blocks_results), "proxy contracts")

    # Implementation contracts
    # y - number of implementations
    # x - block number

    # Sample data (replace this with your data)
    all_blocks = list(itertools.chain.from_iterable(blocks_results))
    # data = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5]
    print(len(all_blocks), " implementation contracts")
    min_all_blocks = min([item["block"] for item in all_blocks])
    max_all_blocks = max([item["block"] for item in all_blocks])
    print("min(all_blocks):", min_all_blocks)
    print("max(all_blocks):", max_all_blocks)
    # Set font properties
    # Use Times New Roman or similar serif font
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.size'] = 12  # Adjust font size as needed

    # The classification of upgradability activities
    data = range(0, max(map(lambda x: len(x), blocks_results))+1)
    implementation_counts = {}
    for value in data:
        cnt = len(
            list(filter(lambda x: len(x) == value, blocks_results)))
        if cnt > 0:
            if cnt > 1:
                implementation_counts[value] = math.log(cnt, 2)
            else:
                implementation_counts[value] = math.log(cnt+0.3, 2)
        else:
            implementation_counts[value] = cnt
        print(value, cnt)

    values = list(implementation_counts.keys())
    frequency = list(implementation_counts.values())

    # Create a scatter plot
    plt.bar(values, frequency)
    plt.xlim(min(values)-0.5, max(values)+0.5)

    y_ticks = range(0, 16, 2)
    y_tick_labels = [2**y_tick if y_tick != 0 else 0 for y_tick in y_ticks]
    plt.yticks(y_ticks, y_tick_labels)
    plt.xlabel('#Implementation')
    plt.ylabel('#Proxy')
    # plt.title('Upgrading Frequency')

    # Show the plot
    # plt.show()
    # Adjust layout to prevent clipping of y-axis labels
    plt.tight_layout()
    # Output the results to a file
    plt.savefig('usccheck/analysis/proxy_impl_frequency.pdf', format='pdf')
