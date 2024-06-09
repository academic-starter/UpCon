### Proxy and Implementation Bugs

## Implementation Bugs
Proxy:0xf8b5012d04f3b551d11b7de0d0c991149e017c14 0xf3c8895fd04bc9cdcd76041399bf0b8a25ac1385
0x6b58643307871dd70e0c6c110f8c0c2ff428478d
0xcd680b74c6809ebdfbc7fe26f3b904f4c48f4a04
Implementation:0xb038e47399aef432fdfd117c0d83b0fb6e9eff85


https://etherscan.io/address/0xb038e47399aef432fdfd117c0d83b0fb6e9eff85#readContract
```solidity
    function initData(string memory name, string memory token, string memory u, uint256 max, uint256 c) public {
        require(initialized == false);
        super.initial(name, token);
        owner = tx.origin;
        maxSupply = max;
        cost = c;
        uri = u;
        initialized = true;
    }
    // initialize = false currently on the blockchain
    // that means anyonce can take the ownership of the implementation contract
```