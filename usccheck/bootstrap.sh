ROOT_DIR=$(git rev-parse --show-toplevel)
# cd $ROOT_DIR && cat usccheck/implementation_interface_proxies/ethereum_mainnet.txt | parallel -j 9 -N 1 echo {1} 

# echo "ethereum_mainnet"
# cd $ROOT_DIR && cat usccheck/implementation_interface_proxies/ethereum_mainnet.txt | parallel -j 1 -N 1 python usccheck/query_implementations.py ethereum_mainnet.txt {1} usccheck/proxy_implementations

echo "ethereum_goerli"
cd $ROOT_DIR && cat usccheck/implementation_interface_proxies/ethereum_goerli.txt | parallel -j 1 -N 1 python usccheck/query_implementations.py ethereum_goerli.txt {1} usccheck/proxy_implementations

echo "arbitrum_mainnet"
cd $ROOT_DIR && cat usccheck/implementation_interface_proxies/arbitrum_mainnet.txt | parallel -j 1 -N 1 python usccheck/query_implementations.py arbitrum_mainnet.txt {1} usccheck/proxy_implementations

echo "avalanche_mainnet"
cd $ROOT_DIR && cat usccheck/implementation_interface_proxies/avalanche_mainnet.txt | parallel -j 1 -N 1 python usccheck/query_implementations.py avalanche_mainnet.txt {1} usccheck/proxy_implementations

echo "optimism_mainnet"
cd $ROOT_DIR && cat usccheck/implementation_interface_proxies/optimism_mainnet.txt | parallel -j 1 -N 1 python usccheck/query_implementations.py optimism_mainnet.txt {1} usccheck/proxy_implementations

echo "polygon_mainnet"
cd $ROOT_DIR && cat usccheck/implementation_interface_proxies/polygon_mainnet.txt | parallel -j 1 -N 1 python usccheck/query_implementations.py polygon_mainnet.txt {1} usccheck/proxy_implementations

echo "polygon_mumbai"
cd $ROOT_DIR && cat usccheck/implementation_interface_proxies/polygon_mumbai.txt | parallel -j 1 -N 1 python usccheck/query_implementations.py polygon_mumbai.txt {1} usccheck/proxy_implementations