import os
import json
import glob


project_proxy_impls = json.load(open(
    "usccheck/OnchainContractData/proxy_implementations/etherscan_mainnet.project.multi_impls.statistics_curated.json"))

impl_dir = "usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet"

github_project_impls_diff = []

for project in project_proxy_impls:
    name = project["name"]
    github = project["github"]
    proxy_impls = project["proxy_impls"]
    proxy_impls_mapping = dict()
    # proxy = proxy_impls[0]
    new_proxy_begin = True
    for index in range(0, len(proxy_impls)):
        address = proxy_impls[index]
        if new_proxy_begin:
            proxy = address
            new_proxy_begin = False
            continue
        if address == "EOF":
            if index == len(proxy_impls) - 1:
                pass
            else:
                new_proxy_begin = True
        else:
            proxy_impls_mapping[proxy] = proxy_impls_mapping.get(
                proxy, []) + [address]

    for proxy in proxy_impls_mapping:
        impls = proxy_impls_mapping[proxy]
        contract_names = set()
        for impl in impls:
            matched_files_or_dirs = glob.glob(os.path.join(
                "usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet", "**", impl+".*"), recursive=True)

            for item in matched_files_or_dirs:
                if os.path.isdir(item):
                    contract_name = os.path.basename(
                        item).split(".etherscan.io-")[-1]
                else:
                    contract_name = os.path.basename(item).split(
                        ".etherscan.io-")[-1].strip(".sol")
                contract_names.add(contract_name)
        print(name, github, contract_names)
        github_project_impls_diff.append(
            dict(name=name, github=github, contract_names=contract_names))


def git_commit_filter(name, github, contract_names):
    for repo in github:
        if repo == "NA":
            continue
        local_dir = os.path.join(os.path.abspath(
            "usccheck/github-projects"), name.replace(" ", "-"))
        if not os.path.exists(local_dir):
            cmd = "mkdir -p %s && cd %s" % (local_dir, local_dir)
        else:
            cmd = "cd %s" % (local_dir)
        cmd += "&& git clone %s" % (repo)
        repo_name = repo.split("/")[-1].strip(".git")
        print(cmd)
        os.system(cmd)
        for contract_name in contract_names:
            log_file = os.path.join(
                local_dir, contract_name+"-upgradability.log")
            cmd = 'cd %s/%s && git log --all --patch -- \"*%s.sol\" >> %s 2>&1' % (local_dir, repo_name,
                                                                                   contract_name, log_file)
            print(cmd)
            os.system(cmd)


for item in github_project_impls_diff:
    git_commit_filter(**item)
