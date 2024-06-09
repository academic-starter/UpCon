import os 
import json 

def generate_proxies_list():
    implementation_interface = "function implementation() public"
    workdir = "./study/data/proxies_with_uschunt_results"
    output_workdir = "./usccheck/implementation_interface_proxies"
    if not os.path.exists(output_workdir):
        os.mkdir(output_workdir)
    proxies_address = list()
    for chain in os.listdir(workdir):
        # if chain!="ethereum":
        #     continue
        for network in os.listdir(os.path.join(workdir, chain)):
            # if network!="mainnet":
            #     continue
            for solidity_version in \
                os.listdir(os.path.join(workdir, chain, network, "proxies")):
                if not os.path.isdir(os.path.join(workdir, chain, network, "proxies", solidity_version)):
                    continue
                for item in os.listdir(os.path.join(workdir, chain, network, "proxies", solidity_version)):
                    if item.find("_") != -1 and os.path.isdir(os.path.join(workdir, chain, network, "proxies", solidity_version, item)):
                        address = "0x"+item.split("_")[0]
                        contract = os.path.join(workdir, chain, network, "proxies", solidity_version, item, item)
                        if not os.path.exists(contract):
                            continue
                        codes = open(contract).readlines()
                        if any(map(lambda code: code.find(implementation_interface)!=-1, codes)):
                            print(address)
                            proxies_address.append(dict(chain=chain, network=network, address=address))
    
    print("**"*10)
    print(f"Summary Result: {len(proxies_address)} proxies that contain implementation interface function")
    print("**"*10)
    json.dump(proxies_address, open(os.path.join(output_workdir, "proxies_list.json"), "w"))
   

generate_proxies_list()

