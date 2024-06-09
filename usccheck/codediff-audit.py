import os 
import json 
import glob 
import argparse 
import subprocess
import keyboard

sample_diff_json = "usccheck/OnchainContractData/gumtreediff/sampled_ethereum_mainnet.json"
workdir = "usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet"
gumtree_diff = "usccheck/OnchainContractData/gumtreediff/ethereum_mainnet"
def codediff_audit(proxy, a, b):
    left = glob.glob(os.path.join(workdir, proxy, "implementation",  a, "*"))[0]
    right = glob.glob(os.path.join(workdir, proxy, "implementation",  b, "*"))[0]
    cmd = "gumtree swingdiff {0} {1}".format(left, right)
    print(cmd)
    os.system(cmd)


def main():
    
    sampled_diffs = json.load(open(sample_diff_json))
    for diff in sampled_diffs:
     
        cmd  = "open {0}".format(diff)
        ret = os.system(cmd)
        print("press <any-key> to next case:")
        input()
        print(f"continue to next case")
        # proxy = os.path.basename(os.path.dirname(diff))
        # implementations = os.path.basename(diff).split(".html")[0].split("-")
        # a = implementations[0]
        # b = implementations[1]
        # codediff_audit(proxy, a, b)

if __name__ == "__main__":
    main()