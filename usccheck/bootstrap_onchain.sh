#!/bin/bash
echo "Bash version ${BASH_VERSION}..."
ROOT_DIR=$(git rev-parse --show-toplevel)

# echo "metatrust ethereum_mainnet onchain proxy contracts"
# cd $ROOT_DIR && head -n 10000 usccheck/OnchainContractData/ethereum_mainnet.list | parallel -j 1 -N 2 python usccheck/query_implementations.py ethereum_mainnet {1} usccheck/OnchainContractData/proxy_implementations {2}

ONE_DAY=86400 # 3600*24 seconds per day
start=`date +%s.%N`
echo $start
for i in $(seq 10000 20000 88564);
do 
  
    if [ "$i" -eq 70000 ]; then
        size=$( echo "88564 - $i" | bc -l )
    else
        size=20000
    fi  
    echo "$i -- $( echo "$i + $size" | bc -l )"
   
    cd $ROOT_DIR && head -n $( echo "$i + $size" | bc -l ) usccheck/OnchainContractData/ethereum_mainnet.list|tail -n $size | parallel -j 1 -N 2 python usccheck/infura_query_implementations.py ethereum_mainnet {1} usccheck/OnchainContractData/proxy_implementations {2}
    
    end=`date +%s.%N`
    # echo $end
    runtime=$( echo "$end - $start" | bc -l )
    # echo $runtime
  
    if [ "$runtime" -lt "$ONE_DAY" ]; then
        gap=$( echo "$ONE_DAY - $runtime" | bc -l) 
        sleep $gap
    fi 
done
