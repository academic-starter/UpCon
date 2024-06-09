import os
import json
import glob

workdir = "usccheck/proxy_implementations"

smart_contract_sanctuary = "../smart-contract-sanctuary"


def get_sourcecode_path_from_santury(chain_network, address):
    chain, network = chain_network.split("_")
    # print(os.path.join(smart_contract_sanctuary, chain, "contracts", network, address[2:4], address[2:]+"*"))
    results = glob.glob(os.path.join(smart_contract_sanctuary,
                        chain, "contracts", network, address[2:4], address[2:]+"*"))
    if len(results) == 1:
        print(results)
        return results[0]
    else:
        return None


uninitialized_impls = []
sole_non_zero_impls = []
multiple_non_zero_impls = []
for chain_network in os.listdir(workdir):
    for item in os.listdir(os.path.join(workdir, chain_network)):
        if not item.endswith(".implementations.json"):
            continue
        proxy_impls = json.load(
            open(os.path.join(workdir, chain_network, item)))
        impls = list(map(lambda x: x["implementation"], sorted(
            proxy_impls, key=lambda x: x["block"])))
        if len(impls) == 1:
            if impls[0] == "0x"+"00"*20:
                uninitialized_impls.append(dict(chain_network=chain_network, proxy=item.split(
                    ".implementations.json")[0], implementations=impls))
            else:
                sole_non_zero_impls.append(dict(chain_network=chain_network, proxy=item.split(
                    ".implementations.json")[0], implementations=impls))
        else:
            impls = list(filter(lambda x: x != "0x"+"00"*20, impls))
            if len(impls) == 1:
                sole_non_zero_impls.append(dict(chain_network=chain_network, proxy=item.split(
                    ".implementations.json")[0], implementations=impls))
            else:
                multiple_non_zero_impls.append(dict(chain_network=chain_network, proxy=item.split(
                    ".implementations.json")[0], implementations=impls))

        impls = list(filter(lambda x: x != "0x"+"00"*20, impls))
        proxy_code_file = get_sourcecode_path_from_santury(
            chain_network=chain_network, address=item.split(".implementations.json")[0])
        impls_files = [get_sourcecode_path_from_santury(
            chain_network=chain_network, address=impl) for impl in impls]
        if os.path.exists(os.path.join(workdir, chain_network, item.split(".implementations.json")[0])):
            os.system("rm -rf " + os.path.join(workdir, chain_network,
                      item.split(".implementations.json")[0]))

        if not os.path.exists(os.path.join(workdir, chain_network, item.split(".implementations.json")[0])):
            os.mkdir(os.path.join(workdir, chain_network,
                     item.split(".implementations.json")[0]))
            os.mkdir(os.path.join(workdir, chain_network,
                     item.split(".implementations.json")[0], "proxy"))
            if len(impls) > 0:
                os.mkdir(os.path.join(workdir, chain_network, item.split(
                    ".implementations.json")[0], "implementation"))

        if proxy_code_file:
            proxy_dir = os.path.join(workdir, chain_network, item.split(
                ".implementations.json")[0], "proxy")
            cmd = f"cp {proxy_code_file} {proxy_dir}/ "
            os.system(cmd)

        index = 0
        for impl_file in impls_files:
            if impl_file:
                impl_dir = os.path.join(workdir, chain_network, item.split(
                    ".implementations.json")[0], "implementation", str(index))
                if not os.path.exists(impl_dir):
                    os.mkdir(impl_dir)
                cmd = f"cp {impl_file} {impl_dir}/ "
                os.system(cmd)
            index += 1

print("**"*10)
print("Statistics:")
print("unintialized proxies: ", len(uninitialized_impls))
print("proxies with sole non-zero implementation: ", len(sole_non_zero_impls))
print("proxies with multiple non-zero implementation: ",
      len(multiple_non_zero_impls))
print("**"*10)

json.dump(dict(uninitialized_impls=uninitialized_impls,
               sole_non_zero_impls=sole_non_zero_impls,
               multiple_non_zero_impls=multiple_non_zero_impls),
          open(os.path.join("usccheck", "proxy_implementation.statistics.json"), "w"),
          indent=4
          )

category_dir = "./usccheck/category/multi_non_zero_impl"
if not os.path.exists(category_dir):
    os.makedirs(category_dir)


for multiple_non_zero_impl in multiple_non_zero_impls:
    chain_network = multiple_non_zero_impl["chain_network"]
    proxy = multiple_non_zero_impl["proxy"]

    item_dir = os.path.join(workdir, chain_network, proxy)

    new_folder = os.path.join(category_dir, chain_network)
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    cmd = f"cp -rf {item_dir} {new_folder}"
    os.system(cmd)

category_dir = "./usccheck/category/sole_non_zero_impl"
if not os.path.exists(category_dir):
    os.makedirs(category_dir)


for sole_non_zero_impls in sole_non_zero_impls:
    chain_network = sole_non_zero_impls["chain_network"]
    proxy = sole_non_zero_impls["proxy"]

    item_dir = os.path.join(workdir, chain_network, proxy)

    new_folder = os.path.join(category_dir, chain_network)
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    cmd = f"cp -rf {item_dir} {new_folder}"
    os.system(cmd)

category_dir = "./usccheck/category/uninitialized_impl"
if not os.path.exists(category_dir):
    os.makedirs(category_dir)


for uninitialized_impls in uninitialized_impls:
    chain_network = uninitialized_impls["chain_network"]
    proxy = uninitialized_impls["proxy"]

    item_dir = os.path.join(workdir, chain_network, proxy)

    new_folder = os.path.join(category_dir, chain_network)
    if not os.path.exists(new_folder):
        os.makedirs(new_folder)

    cmd = f"cp -rf {item_dir} {new_folder}"
    os.system(cmd)
