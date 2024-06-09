import os
import json

proxy_statistics = "usccheck/OnchainContractData/proxy_implementations/etherscan_mainnet.statistics.json"
dapp_statistics = "usccheck/OnchainContractData/ads_dapp.json"
dapp_contract_statistics = "usccheck/OnchainContractData/ads_dapp_contract.json"
project_statistics = "usccheck/OnchainContractData/ads_project.json"
project_contract_statistics = "usccheck/OnchainContractData/ads_project_contract.json"
project_dapp_statistics = "usccheck/OnchainContractData/ads_project_dapp_relation.json"
project_source_statistics = "usccheck/OnchainContractData/ads_project_source.json"

proxies = json.load(open(proxy_statistics))
dapps = json.load(open(dapp_statistics))
dapp_contracts = json.load(open(dapp_contract_statistics))
projects = json.load(open(project_statistics))
project_contracts = json.load(open(project_contract_statistics))
project_dapps = json.load(open(project_dapp_statistics))
project_sources = json.load(open(project_source_statistics))

dapp_proxy_statistics = {}
project_proxy_statistics = {}

# for item in proxies["multiple_non_zero_impls"] + proxies["sole_non_zero_impls"] + proxies["uninitialized_impls"]:
for item in proxies["multiple_non_zero_impls"]:
    chain_network = item["chain_network"]
    proxy = item["proxy"]
    impls = item["implementations"]

    _dapp_contracts = list(filter(lambda x: x["chain_id"] == 1 and (x["address"].lower() == proxy.lower(
    ) or x["address"].lower() in list(map(lambda x: x.lower(), impls))), dapp_contracts))
    _dapp_ids = list(map(lambda x: x["dapp_id"].lower(), _dapp_contracts))
    for id in _dapp_ids:
        dapp_proxy_statistics[id] = dapp_proxy_statistics.get(
            id, []) + [proxy] + impls + ["EOF"]

    _project_contracts = list(filter(lambda x: x["chain_id"] == 1 and (x["address"].lower() == proxy.lower(
    ) or x["address"].lower() in list(map(lambda x: x.lower(), impls))), project_contracts))
    _project_ids = list(
        map(lambda x: x["project_id"].lower(), _project_contracts))
    for id in _project_ids:
        project_proxy_statistics[id] = project_proxy_statistics.get(
            id, []) + [proxy] + impls + ["EOF"]

multi_dapp_proxy_statistics = {}
for id in dapp_proxy_statistics:
    for item in proxies["multiple_non_zero_impls"]:
        proxy = item["proxy"]
        impls = item["implementations"]
        if len(set([proxy]+impls).intersection(dapp_proxy_statistics[id])) > 0:
            multi_dapp_proxy_statistics[id] = dapp_proxy_statistics[id]
            break


for id in multi_dapp_proxy_statistics:
    _dapps = list(filter(lambda x: x["id"].lower() == id, dapps))
    assert len(_dapps) >= 1, "Proxy statistics  for %s not found" % id
    dapp = _dapps[0]
    print("Dapp: %s\nDescription: %s\n Proxy statistics: %s\n\n" %
          (dapp["name"], dapp["description"], multi_dapp_proxy_statistics[id]))

json.dump(dapp_proxy_statistics, open(
    "usccheck/OnchainContractData/proxy_implementations/etherscan_mainnet.dapp.statistics.json", "w"), indent=4)
json.dump(multi_dapp_proxy_statistics, open(
    "usccheck/OnchainContractData/proxy_implementations/etherscan_mainnet.dapp.multi_impls.statistics.json", "w"), indent=4)

multi_project_proxy_statistics = {}
for id in project_proxy_statistics:
    for item in proxies["multiple_non_zero_impls"]:
        proxy = item["proxy"]
        impls = item["implementations"]
        if len(set([proxy]+impls).intersection(project_proxy_statistics[id])) > 0:
            multi_project_proxy_statistics[id] = project_proxy_statistics[id]
            break


readable_multi_project_proxy_statistics = []
for id in multi_project_proxy_statistics:
    _projects = list(filter(lambda x: x["id"].lower() == id, projects))
    assert len(_projects) >= 1, "Proxy statistics  for %s not found" % id
    project = _projects[0]
    print("Project: %s\nDescription: %s\n Proxy statistics: %s\n\n" %
          (project["name"], project["description"], multi_project_proxy_statistics[id]))
    links = list(map(lambda x: x["link"], filter(
        lambda x: "project_id" in x and x["project_id"] == id, project_sources)))
    readable_multi_project_proxy_statistics.append(dict(
        name=project["name"], id=project["id"], description=project["description"], proxy_impls=multi_project_proxy_statistics[id], links=links, github=[]))

json.dump(project_proxy_statistics, open(
    "usccheck/OnchainContractData/proxy_implementations/etherscan_mainnet.project.statistics.json", "w"), indent=4)
json.dump(readable_multi_project_proxy_statistics, open(
    "usccheck/OnchainContractData/proxy_implementations/etherscan_mainnet.project.multi_impls.statistics.json", "w"), indent=4)
