ROOT_DIR=$(git rev-parse --show-toplevel)
# cd $ROOT_DIR && cat usccheck/implementation_interface_proxies/ethereum_mainnet.txt | parallel -j 9 -N 1 echo {1} 

echo "ethereum_mainnet hacked proxy contracts"
cd $ROOT_DIR && cat usccheck/attacks/proxy.list | parallel -j 1 -N 1 python usccheck/query_implementations.py ethereum_mainnet {1} usccheck/etherscan_hack_proxy_implementations

