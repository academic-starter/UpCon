const hre = require("hardhat");
const helpers = require("@nomicfoundation/hardhat-network-helpers");
async function impersonalizeEOA(address){
    hre.network.provider.request({
        method: "hardhat_impersonateAccount",
        params: [address],
    })
}

async function impersonalizeContract(address, runtime_code){
    await hre.network.provider.send(
        "hardhat_setCode",
        [
            address,
            runtime_code
        ]
    );
}

async function replayTransaction(chain_id, blockNumber, timestamp, from, to, gasPrice, gasLimit, value, data){
    await hre.network.provider.request({
        method: "hardhat_reset",
        params: [
          {
            forking: {
              jsonRpcUrl: "https://mainnet.infura.io/v3/30df87c8ffa645cfaea52f6344791203",
              blockNumber: blockNumber-1
            },
            chainId: chain_id
          },
        ],
      });
    let _blockNumber = await hre.network.provider.send(
        "eth_blockNumber")
    console.log(parseInt(_blockNumber, 16));
    
    let _code  = await hre.network.provider.send("eth_getCode", [to])
    console.log(_code);

    await impersonalizeEOA(from);
    let signer = await hre.ethers.provider.getSigner(from)
    let response = await signer.sendTransaction({
            to: to,
            gasPrice: gasPrice,
            gas: gasLimit,
            value: value,
            data: data
    });
    console.log(response);
    _blockNumber = await hre.network.provider.send(
        "eth_blockNumber")
    console.log(parseInt(_blockNumber, 16));
}

async function main() {
  const accounts = await hre.ethers.getSigners();

  for (const account of accounts) {
    console.log(account.address);
  }
// failed:  https://etherscan.io/tx/0x502cace0340dcb9d9f999e6797ce0f1003e2dac056cad3e1672cbe6a28781aa7
// work: https://etherscan.io/tx/0x61edeb60ca90d70ed15e1c313ef37644b2710e716a8c0f4c3efd022b4ed8b0f6
    chain_id = 1 // ETH_MAINNET
    blockno = 16906390
    timestamp = Date.parse("2023-05-25T18:55:35")
    console.log(timestamp)
    sender = "0xeCa2e2D894D19778939bD4DfC34D2a3C45E96456"
    to = "0xA69babEF1cA67A37Ffaf7a485DfFF3382056e78C"
    value = 0 
    gasLimit = 221708
    gasPrice = 19.87393765 * 10**9
    data = "0x78e111f600000000000000000000000032e41aa2b278cd4f3dcad40ef9ff2370b53d8a58000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000000c404764a8a00000000000000000000000000000000000000000000000099a6cacc70960dcf00000000000000000000000000000000000000160063d4ea8135000000000000000000000000000000000000000000000000000006214c0c7412db97835fb9ff0000000000000000000000000000000000000000000000000de0b6b3a764000000000000000000000000000000000000000000000000000000000000641f43e0bf0000000000000000000000000000000000000000000000000000000000fd4700000000000000000000000000000000000000000000000000000000"
    
    await replayTransaction(1, blockno, timestamp, sender, to, gasPrice, gasLimit, value, data)
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});