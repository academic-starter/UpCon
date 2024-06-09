import json 

proxies_list_file = "usccheck/implementation_interface_proxies/proxies_list.json"
proxies_list = json.load(open(proxies_list_file))

# ethereum_mainnet = list(filter(lambda proxy: proxy["chain"] == "ethereum" and proxy["network"] == "mainnet", proxies_list))

# addresses  = list(map(lambda proxy: proxy["address"], ethereum_mainnet))

# with open("usccheck/implementation_interface_proxies/ethereum_mainnet.txt", "w") as f:
#     f.write("\n".join(addresses))



chains = set(map(lambda proxy: proxy["chain"], proxies_list))

for chain in chains:
    networks = set(map(lambda proxy: proxy["network"], filter(lambda proxy: proxy["chain"] == chain, proxies_list)))
    for network in networks:
        chain_network = list(filter(lambda proxy: proxy["chain"] == chain and proxy["network"] == network, proxies_list))
        addresses  = list(map(lambda proxy: proxy["address"], chain_network))

        with open(f"usccheck/implementation_interface_proxies/{chain}_{network}.txt", "w") as f:
            f.write("\n".join(addresses))

