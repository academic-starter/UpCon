#!/bin/bash

impl_dir=usccheck/OnchainContractData/proxy_implementations/ethereum_mainnet
for item in $(ls ${impl_dir})
do 
    if [ -d "${impl_dir}/${item}" ]; then
        # echo "${item} is a directory"
        echo "uploading ${item} contracts..."
        find ${impl_dir}/${item} -name *.sol | xargs -n 1 -I {} curl -F source_file=@{} https://www.4byte.directory/api/v1/import-solidity/
        echo "done"
    fi 
done 