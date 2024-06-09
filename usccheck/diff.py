import os 
import json 
import glob 

workdir = "usccheck/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet"

def diff(a, b, implementation_dir):
    resultsA = glob.glob(os.path.join(implementation_dir, a, "*"))
    resultsB = glob.glob(os.path.join(implementation_dir, b, "*"))
    if len(resultsA) == 1 and len(resultsB) ==1:
        if not os.path.isdir(resultsA[0]) and not os.path.isdir(resultsB[0]):
            cmd = "diff -u -d %s %s" % (resultsA[0], resultsB[0])
            # print(cmd)
            os.system(cmd)

for proxy in os.listdir(workdir):
    # print("Proxy: ", os.path.join(workdir, proxy))
    implementation_dir = os.path.join(workdir, proxy, "implementation")
    implementation_indice = sorted(map(int, os.listdir(implementation_dir)))
    for i in range(len(implementation_indice)-1):
        a = implementation_indice[i]
        b = implementation_indice[i+1]
        diff(str(a), str(b), implementation_dir)


