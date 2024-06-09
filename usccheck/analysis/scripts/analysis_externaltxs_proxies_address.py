import matplotlib.pyplot as plt
import math
import os
import json
import itertools
import numpy as np
import pandas as pd

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
for item in os.listdir(proxy_implementation_dir):
    if item.endswith(".json"):
        address = item.split(".implementations.json")[0]
        result = json.load(open(os.path.join(proxy_implementation_dir, item)))
        if len(result) > 1:
            sorted_result = sorted(result, key=lambda x: x["block"])
            # print(sorted_result)
            cnt += 1
            blocks = list(map(lambda x: x["block"], sorted_result))
            blocks_results[address] = blocks

items = os.listdir("usccheck/analysis/fulldata")
df = None
for item in items:
    _df = pd.read_csv(os.path.join("usccheck/analysis/fulldata", item))
    if df is not None:
        df = pd.concat([df, _df], axis=0, ignore_index=True)
    else:
        df = _df

print(len(df), " transactions")

# externaltxs_proxies_between_20220101_20240101 = "usccheck/analysis/bq-results-alltxs.csv"
# df = pd.read_csv(externaltxs_proxies_between_20220101_20240101)
# print(df)

failure_rates = {}
for address in blocks_results:
    # print(address)
    blocks = blocks_results[address]
    all_selected_item = df[df["to_address"] == address]
    pre_block = blocks[0]
    for next_block in blocks[1:]:
        selected_item = all_selected_item[(all_selected_item["block_number"] > pre_block) & (
            all_selected_item["block_number"] < next_block)]

        # print(pre_block, next_block)
        fail_txs = selected_item[selected_item["receipt_status"] == 0]
        failure_rate = len(fail_txs) / \
            len(selected_item) if len(selected_item) > 0 else 0

        existing = failure_rates.get(address, [])
        existing.append(failure_rate)
        failure_rates[address] = existing

        pre_block = next_block


data = list(range(0, 10))

values_failure_rate = {}
for value in data:
    _failure_rates = []
    for address in failure_rates:
        if len(failure_rates[address]) <= value:
            continue
        else:
            if failure_rates[address][value] == 0:
                # zero failure rate is meaningless, may affect the validity about the change of overall failure rate
                continue
            _failure_rates.append(failure_rates[address][value])
    values_failure_rate[value] = _failure_rates

values = list(values_failure_rate.keys())
data = list(values_failure_rate.values())


# Set font properties
# Use Times New Roman or similar serif font
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 12  # Adjust font size as needed

# # Create a box plot
plt.boxplot(data, labels=list(map(str, values)))

# Add labels and title
plt.xlabel('Implementation version')
plt.ylabel('Failure rate')

# Show the plot
# plt.show()

plt.savefig('usccheck/analysis/boxplot_overall_failure_rate.pdf', format='pdf')

# close the plot
plt.close()


# # Create a box plot
plt.plot(values, [sum(item)/len(item) for item in data])

# Add labels and title
plt.xlabel('Implementation version')
plt.ylabel('Failure rate')

# Show the plot
# plt.show()

plt.savefig('usccheck/analysis/plot_overall_failure_rate.pdf', format='pdf')

# close the plot
plt.close()


data = list(range(0, 6))
values_failure_rate = {}
cnt = 0
for value in data:
    _failure_rates = []
    for address in failure_rates:
        if len(failure_rates[address]) < 6:
            continue
        else:
            # if failure_rates[address][value] == 0:
            #     # zero failure rate is meaningless, may affect the validity about the change of overall failure rate
            #     continue
            _failure_rates.append(failure_rates[address][value])
            cnt += 1
    values_failure_rate[value] = _failure_rates

values = list(values_failure_rate.keys())
data = list(values_failure_rate.values())


# Set font properties
# Use Times New Roman or similar serif font
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 12  # Adjust font size as needed

# # Create a box plot
plt.boxplot(data, labels=list(map(str, values)))

# Add labels and title
plt.xlabel('Implementation version')
plt.ylabel('Failure rate')

# Show the plot
# plt.show()

plt.savefig('usccheck/analysis/boxplot_6_failure_rate.pdf', format='pdf')

# close the plot
plt.close()


# # Create a box plot
plt.plot(values, [sum(item)/len(item) for item in data])

# Add labels and title
plt.xlabel('Implementation version')
plt.ylabel('Failure rate')

# Show the plot
# plt.show()

plt.savefig('usccheck/analysis/plot_6_failure_rate.pdf', format='pdf')

# close the plot
plt.close()

print("%d proxy contract having more than six implementation contracts" % cnt)


data = list(range(0, 10))
values_failure_rate = {}
cnt = 0
for value in data:
    _failure_rates = []
    for address in failure_rates:
        if len(failure_rates[address]) < 10:
            continue
        else:
            # if failure_rates[address][value] == 0:
            #     # zero failure rate is meaningless, may affect the validity about the change of overall failure rate
            #     continue
            _failure_rates.append(failure_rates[address][value])
            cnt += 1
    values_failure_rate[value] = _failure_rates

values = list(values_failure_rate.keys())
data = list(values_failure_rate.values())


# Set font properties
# Use Times New Roman or similar serif font
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 12  # Adjust font size as needed

# # Create a box plot
plt.boxplot(data, labels=list(map(str, values)))

# Add labels and title
plt.xlabel('Implementation version')
plt.ylabel('Failure rate')

# Show the plot
# plt.show()

plt.savefig('usccheck/analysis/boxplot_10_failure_rate.pdf', format='pdf')

# close the plot
plt.close()


# # Create a box plot
plt.plot(values, [sum(item)/len(item) for item in data])

# Add labels and title
plt.xlabel('Implementation version')
plt.ylabel('Failure rate')

# Show the plot
# plt.show()

plt.savefig('usccheck/analysis/plot_10_failure_rate.pdf', format='pdf')

# close the plot
plt.close()

print("%d proxy contract having more than 10 implementation contracts" % cnt)
# failure_rates = {}
# for address in blocks_results:
#     # print(address)
#     blocks = blocks_results[address]
#     all_selected_item = df[df["to_address"] == address]
#     pre_block = blocks[0]
#     for next_block in blocks[1:]:
#         selected_item = all_selected_item[(all_selected_item["block_number"] >= pre_block) & (all_selected_item["block_number"] <= pre_block + 1000000) & (
#             all_selected_item["block_number"] < next_block)]

#         # print(pre_block, next_block)
#         fail_txs = selected_item[selected_item["receipt_status"] == 0]
#         failure_rate = len(fail_txs) / \
#             len(selected_item) if len(selected_item) > 0 else 0

#         existing = failure_rates.get(address, [])
#         existing.append(failure_rate)
#         failure_rates[address] = existing

#         pre_block = next_block


# data = list(range(0, 10))

# values_failure_rate = {}
# for value in data:
#     _failure_rates = []
#     for address in failure_rates:
#         if len(failure_rates[address]) <= value:
#             continue
#         else:
#             if failure_rates[address][value] == 0:
#                 # zero failure rate is meaningless, may affect the validity about the change of overall failure rate
#                 continue
#             _failure_rates.append(failure_rates[address][value])
#     values_failure_rate[value] = _failure_rates

# values = list(values_failure_rate.keys())
# data = list(values_failure_rate.values())


# # Set font properties
# # Use Times New Roman or similar serif font
# plt.rcParams['font.family'] = 'serif'
# plt.rcParams['font.size'] = 12  # Adjust font size as needed


# # If we were to simply plot pts, we'd lose most of the interesting
# # details due to the outliers. So let's 'break' or 'cut-out' the y-axis
# # into two portions - use the top (ax1) for the outliers, and the bottom
# # (ax2) for the details of the majority of our data
# fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
# fig.subplots_adjust(hspace=0.05)  # adjust space between axes


# # plot the same data on both axes
# ax1.boxplot(data, labels=list(map(str, values)))
# ax2.boxplot(data, labels=list(map(str, values)))

# # zoom-in / limit the view to different portions of the data
# ax1.set_ylim(.78, 1.02)  # outliers only
# ax2.set_ylim(-0.02, .28)  # most of the data

# # Remove x-axis ticks and labels from the first subplot
# plt.setp(ax1.get_xticklabels(), visible=False)

# # hide the spines between ax and ax2
# ax1.spines.bottom.set_visible(False)
# ax2.spines.top.set_visible(False)
# ax1.xaxis.tick_top()
# ax1.tick_params(labeltop=False)  # don't put tick labels at the top
# ax2.xaxis.tick_bottom()

# # Now, let's turn towards the cut-out slanted lines.
# # We create line objects in axes coordinates, in which (0,0), (0,1),
# # (1,0), and (1,1) are the four corners of the axes.
# # The slanted lines themselves are markers at those locations, such that the
# # lines keep their angle and position, independent of the axes size or scale
# # Finally, we need to disable clipping.

# d = .5  # proportion of vertical to horizontal extent of the slanted line
# kwargs = dict(marker=[(-1, -d), (1, d)], markersize=12,
#               linestyle="none", color='k', mec='k', mew=1, clip_on=False)
# ax1.plot([0, 1], [0, 0], transform=ax1.transAxes, **kwargs)
# ax2.plot([0, 1], [1, 1], transform=ax2.transAxes, **kwargs)

# # # Create a box plot
# # plt.boxplot(data, labels=list(map(str, values)))

# # Add labels and title
# plt.xlabel('Implementation version')
# ax1.set_ylabel('Failure rate')
# ax2.set_ylabel('Failure rate')
# ax1.set_title('Failure rate with different implementation versions')

# # Show the plot
# # plt.show()

# plt.savefig(
#     'usccheck/analysis/boxplot_overall_failure_rate_1000000.pdf', format='pdf')

# # close the plot
# plt.close()

# print("start failure rate calcaulation...")
# failure_rates_plus = {}
# failure_rates_minus = {}
# for address in blocks_results:
#     # print(address)
#     blocks = blocks_results[address]
#     all_selected_item = df[df["to_address"] == address]
#     callers = all_selected_item["from_address"].unique()
#     pre_block = blocks[0]
#     for i in range(1, len(blocks)):
#         next_block = blocks[i]
#         next_next_block = blocks[i + 1] if i+1 < len(blocks) else 2*10**7
#         minus_selected_item = all_selected_item[(all_selected_item["block_number"] >= pre_block) & (all_selected_item["block_number"] >= next_block - 200000) & (
#             all_selected_item["block_number"] < next_block)]

#         minus_succ_txs = minus_selected_item[minus_selected_item["receipt_status"] == 1].groupby(
#             "from_address").size()
#         minus_fail_txs = minus_selected_item[minus_selected_item["receipt_status"] == 0].groupby(
#             "from_address").size()
#         minus_callers = minus_selected_item["from_address"].unique()
#         # print(fail_txs)

#         plus_selected_item = all_selected_item[(all_selected_item["block_number"] <= next_block + 200000) & (
#             all_selected_item["block_number"] > next_block) & (
#             all_selected_item["block_number"] < next_next_block)]

#         plus_succ_txs = plus_selected_item[plus_selected_item["receipt_status"] == 1].groupby(
#             "from_address").size()
#         plus_fail_txs = plus_selected_item[plus_selected_item["receipt_status"] == 0].groupby(
#             "from_address").size()
#         plus_callers = plus_selected_item["from_address"].unique()

#         common_callers = set(minus_callers).intersection(plus_callers)
#         for caller in common_callers:
#             if caller in minus_fail_txs.index:
#                 caller_fail_txs = int(minus_fail_txs[caller])
#             else:
#                 caller_fail_txs = 0
#             if caller in minus_succ_txs.index:
#                 caller_succ_txs = int(minus_succ_txs[caller])
#             else:
#                 caller_succ_txs = 0

#             failure_rate = caller_fail_txs / \
#                 (caller_fail_txs + caller_succ_txs)

#             existing = failure_rates_minus.get(address, {})
#             eexisting = existing.get(caller, [])
#             eexisting.append(failure_rate)
#             existing[caller] = eexisting
#             failure_rates_minus[address] = existing

#         # print(fail_txs)

#         for caller in common_callers:
#             if caller in plus_fail_txs.index:
#                 caller_fail_txs = int(plus_fail_txs[caller])
#             else:
#                 caller_fail_txs = 0
#             if caller in plus_succ_txs.index:
#                 caller_succ_txs = int(plus_succ_txs[caller])
#             else:
#                 caller_succ_txs = 0

#             if caller_succ_txs == 0 and caller_fail_txs == 0:
#                 failure_rate = 0
#             else:
#                 failure_rate = caller_fail_txs / \
#                     (caller_fail_txs + caller_succ_txs)

#             existing = failure_rates_plus.get(address, {})
#             eexisting = existing.get(caller, [])
#             eexisting.append(failure_rate)
#             existing[caller] = eexisting
#             failure_rates_plus[address] = existing

#         pre_block = next_block


# print("done!")


# print("start computing Pearson coefficient...")

# negatives = []
# positives = []
# neutrals = []
# for address in failure_rates_plus:
#     for caller in failure_rates_plus[address]:
#         # if not (address in failure_rates_minus and caller in failure_rates_minus[address] and len(failure_rates_plus[address][caller]) != len(failure_rates_minus[address][caller])):
#         #     continue
#         if sum(failure_rates_plus[address][caller]) == 0 and sum(failure_rates_minus[address][caller]) == 0:
#             continue
#         if sum(failure_rates_plus[address][caller])/len(failure_rates_plus[address][caller]) > sum(failure_rates_minus[address][caller])/len(failure_rates_minus[address][caller]):
#             positives.append([address, caller])
#         elif sum(failure_rates_plus[address][caller])/len(failure_rates_plus[address][caller]) == sum(failure_rates_minus[address][caller])/len(failure_rates_minus[address][caller]):
#             neutrals.append([address, caller])
#         else:
#             negatives.append([address, caller])


# json.dump({"positives": positives, "negatives": negatives, "neutrals": neutrals}, open(
#     'usccheck/analysis/positives_negatives_neutrals.users.csv', 'w'), indent=4)

# print("done!")

# print("Summary of correlation coefficient")
# print("--------------------------------")
# print("Decrease %d" % len(negatives))
# print("Increase %d" % len(positives))
# print("Neutral %d" % len(neutrals))


# # Set font properties
# # Use Times New Roman or similar serif font
# plt.rcParams['font.family'] = 'serif'
# plt.rcParams['font.size'] = 12  # Adjust font size as needed


# # plt.figure(figsize=(6, 6))

# plt.pie([len(negatives), len(positives), len(neutrals)],
#         labels=["Decrease", "Increase", "Neutral"], autopct='%1.1f%%', startangle=90)

# plt.axis('equal')

# # Add numbers to the pie chart
# plt.text(0, 0, 'Total: {}'.format(sum([len(negatives), len(
#     positives), len(neutrals)])), color='black', fontsize=12, ha='center')

# # Add a title
# # plt.title('User failure rate correlation with implementation upgrading.')

# plt.savefig(
#     'usccheck/analysis/user_trend_failure_rate.pdf', format='pdf')

# # close the plot
# plt.close()
