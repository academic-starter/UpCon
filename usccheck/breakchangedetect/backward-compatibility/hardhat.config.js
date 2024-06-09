require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.24",
  networks: {
    hardhat: {
      forking: {
        url: "https://mainnet.infura.io/v3/30df87c8ffa645cfaea52f6344791203",
        blockNumber: 16906389,
        chainId: 1
      },
      mining: {
        mempool: {
          order: "fifo"
        }
      },
      chainId: 1
    }
  }
};
