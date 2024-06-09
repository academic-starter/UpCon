### Summary of Code Diffs 



## Case Study-Backward Compatibility 
```solidity 
+    /*
+     * Methods for backward compatibility
+     */
+
+    function factory() external pure override returns (address) {
+        return FACTORY_ADDRESS;
+    }
+
+    function delay() external pure override returns (address) {
+        return DELAY_ADDRESS;
+    }
+
+    function weth() external pure override returns (address) {
+        return WETH_ADDRESS;
+    }
+
+    function twapInterval(address pair) external pure override returns (uint32) {
+        return getTwapInterval(pair);
+    }
+
+    function ethTransferGasCost() external pure override returns (uint256) {
+        return Orders.ETHER_TRANSFER_COST;
+    }
+
+    function executionGasLimit() external pure override returns (uint256) {
+        return EXECUTION_GAS_LIMIT;
+    }
+
+    function tokenLimitMin(address token) external pure override returns (uint256) {
+        return getTokenLimitMin(token);
+    }
```

## Likely Bad Changes
```solidity
+    function _emitEventWithDefaults() internal {
+        emit DelaySet(DELAY_ADDRESS);
+        emit EthTransferGasCostSet(Orders.ETHER_TRANSFER_COST);
+        emit ExecutionGasLimitSet(EXECUTION_GAS_LIMIT);
+
+        emit ToleranceSet(0x2fe16Dd18bba26e457B7dD2080d5674312b026a2, 0);
+        emit ToleranceSet(0x048f0e7ea2CFD522a4a058D1b1bDd574A0486c46, 0);
+        emit ToleranceSet(0x37F6dF71b40c50b2038329CaBf5FDa3682Df1ebF, 0);
+        emit ToleranceSet(0x6ec472b613012a492693697FA551420E60567eA7, 0);
+
+        emit TokenLimitMinSet(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2, 10000000000000000);
+        emit TokenLimitMinSet(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48, 20000000);
+        emit TokenLimitMinSet(0xdAC17F958D2ee523a2206206994597C13D831ec7, 20000000);
+        emit TokenLimitMinSet(0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599, 64500);
+
+        emit TokenLimitMaxMultiplierSet(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2, 950000000000000000);
+        emit TokenLimitMaxMultiplierSet(0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48, 950000000000000000);
+        emit TokenLimitMaxMultiplierSet(0xdAC17F958D2ee523a2206206994597C13D831ec7, 950000000000000000);
+        emit TokenLimitMaxMultiplierSet(0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599, 950000000000000000);
+
+        emit TwapIntervalSet(0x2fe16Dd18bba26e457B7dD2080d5674312b026a2, 300);
+        emit TwapIntervalSet(0x048f0e7ea2CFD522a4a058D1b1bDd574A0486c46, 300);
+        emit TwapIntervalSet(0x37F6dF71b40c50b2038329CaBf5FDa3682Df1ebF, 300);
+        emit TwapIntervalSet(0x6ec472b613012a492693697FA551420E60567eA7, 300);
+    }
+
```

```solidity
-    uint256 private locked;
+    uint256 private locked = 1;
 
```

```solidity

--- usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0xdbb7be7a35d8c2323eac3e73c11e12e87fe51f46/implementation/7/0xbb419a912a25e56e90430245a6535d9cf740815a.etherscan.io-MigratorV2/src/MigratorV2.sol	2024-04-04 10:02:11
+++ usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0xdbb7be7a35d8c2323eac3e73c11e12e87fe51f46/implementation/8/0x7ea40c97940528b4c85bf35da173098f133e7023.etherscan.io-MigratorV2/src/MigratorV2.sol	2024-04-04 10:02:11
@@ -93,6 +93,8 @@
 
 
         (uint8 body, uint8 helm, uint8 mainhand, uint8 offhand, uint16 level ,uint16 zugModifier , uint32 lvlProgress) = oldOrcs.orcs(tokenId);
+        level = uint16(lvlProgress / 1000);
+        lvlProgress = (lvlProgress % 1000);
         
         uint zugAmount;
         if (action_ == EtherOrcs.Actions.FARMING) {

--- usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0xdbb7be7a35d8c2323eac3e73c11e12e87fe51f46/implementation/8/0x7ea40c97940528b4c85bf35da173098f133e7023.etherscan.io-MigratorV2/src/MigratorV2.sol	2024-04-04 10:02:11
+++ usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0xdbb7be7a35d8c2323eac3e73c11e12e87fe51f46/implementation/9/0xbb419a912a25e56e90430245a6535d9cf740815a.etherscan.io-MigratorV2/src/MigratorV2.sol	2024-04-04 10:02:11
@@ -93,8 +93,6 @@
 
 
         (uint8 body, uint8 helm, uint8 mainhand, uint8 offhand, uint16 level ,uint16 zugModifier , uint32 lvlProgress) = oldOrcs.orcs(tokenId);
-        level = uint16(lvlProgress / 1000);
-        lvlProgress = (lvlProgress % 1000);
         
         uint zugAmount;
         if (action_ == EtherOrcs.Actions.FARMING) {

```

```solidity
     function initialize(init memory params) external initializer {
-        require(params._operator != address(0), "Invalid address");
-        require(params._admin != address(0), "Invalid address");
-        require(params._router != address(0), "Invalid address");
-        require(params._profitWallet1 != address(0), "Invalid address");
-        require(params._profitWallet2 != address(0), "Invalid address");
-        require(params._weth != address(0), "Invalid address");
-        require(params._vrfCoordinator != address(0), "Invalid address");
-        require(
-            params._profitPercent + params._burnPercent < params._basisPoints,
-            "Cannot be more than 100%"
-        );
-        require(params._profitSplit1BP < params._basisPoints, "Cannot be more than 100%");
-        require(params._taxBP < params._basisPoints, "TaxBP cannot be more than 100%");
+        // require(params._operator != address(0), "Invalid address");
+        // require(params._admin != address(0), "Invalid address");
+        // require(params._router != address(0), "Invalid address");
+        // require(params._profitWallet1 != address(0), "Invalid address");
+        // require(params._profitWallet2 != address(0), "Invalid address");
+        // require(params._weth != address(0), "Invalid address");
+        // require(params._vrfCoordinator != address(0), "Invalid address");
+        // require(
+        //     params._profitPercent + params._burnPercent < params._basisPoints,
+        //     "Cannot be more than 100%"
+        // );
+        // require(params._profitSplit1BP < params._basisPoints, "Cannot be more than 100%");
+        // require(params._taxBP < params._basisPoints, "TaxBP cannot be more than 100%");
 
-        operator = params._operator;
-        admin = params._admin;
-        router = IUniswapV2Router02(params._router);
-        profitWallet1 = params._profitWallet1;
-        profitWallet2 = params._profitWallet2;
-        WETH = params._weth;
-        basisPoints = params._basisPoints;
-        profitPercent = params._profitPercent;
-        burnPercent = params._burnPercent;
-        profitSplit1BP = params._profitSplit1BP;
-        taxBP = params._taxBP;
-        initializeV2Consumer(
-            params._subscriptionId,
-            params._vrfCoordinator,
-            params._keyhash
-        );
+        // operator = params._operator;
+        // admin = params._admin;
+        // router = IUniswapV2Router02(params._router);
+        // profitWallet1 = params._profitWallet1;
+        // profitWallet2 = params._profitWallet2;
+        // WETH = params._weth;
+        // basisPoints = params._basisPoints;
+        // profitPercent = params._profitPercent;
+        // burnPercent = params._burnPercent;
+        // profitSplit1BP = params._profitSplit1BP;
+        // taxBP = params._taxBP;
+        // initializeV2Consumer(
+        //     params._subscriptionId,
+        //     params._vrfCoordinator,
+        //     params._keyhash
+        // );
     }
```

```solidity 
     function mint(uint256 mintAmount) external returns (uint256) {
         (uint256 err, ) = mintInternal(mintAmount, false);
-        return err;
+        require(err == 0, "mint failed");
     }
```

```solidity 
 --- usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0xbb4b067cc612494914a902217cb6078ab4728e36/implementation/1/0x4f08008ef178929e3866f1aeea75beaa8b909b9e.etherscan.io-CCTokenDelegate/contracts/CCTokenDelegate.sol	2024-04-04 10:02:11
+++ usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0xbb4b067cc612494914a902217cb6078ab4728e36/implementation/2/0xe3d7a35cc516f383dbab40ad169ec41e1c287a27.etherscan.io-CCTokenDelegate/contracts/CCTokenDelegate.sol	2024-04-04 10:02:11
     function harvestComp() internal {
         address[] memory holders = new address[](1);
-        holders[0] = msg.sender;
+        holders[0] = address(this);
         CToken[] memory cTokens = new CToken[](1);
         cTokens[0] = CToken(underlying);
 
```

```solidity 
textdiff:
--- usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0x74d657c159a69429d750e2a8e0f4276bbaeb19ae/implementation/1/0x354206468ee7d4d7f5bddb52af244748dc3c5df0.etherscan.io-CErc20PluginRewardsDelegate/contracts/CErc20PluginRewardsDelegate.sol	2024-04-04 10:02:10
+++ usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0x74d657c159a69429d750e2a8e0f4276bbaeb19ae/implementation/2/0x968fe8216e0f03527db4033cf07fbdd3ef7cb3ee.etherscan.io-CErc20PluginRewardsDelegate/contracts/CErc20PluginRewardsDelegate.sol	2024-04-04 10:02:10
@@ -16,7 +16,6 @@
             (address, address, address)
         );
 
-        require(address(plugin) == address(0), "plugin");
         plugin = IERC4626Draft(_plugin);
 
         EIP20Interface(_rewardToken).approve(_rewardsDistributor, uint256(-1));
```


```solidity 
         (MathError err2, uint product) = divUInt(doubleScaledProductWithHalfScale, expScale);
         // The only error `div` can return is MathError.DIVISION_BY_ZERO but we control `expScale` and it is not zero.
-        assert(err2 == MathError.NO_ERROR);
+        require(err2 == MathError.NO_ERROR);
 
         return (MathError.NO_ERROR, Exp({mantissa: product}));
```

```solidity 
@@ -1044,7 +668,7 @@
 
         uint256 adminCount = _getAdminCount(adminEpoch);
 
-        for (uint256 i; i < adminCount; i++) {
+        for (uint256 i; i < adminCount; ++i) {
             _setHasVoted(adminEpoch, topic, _getAdmin(adminEpoch, i), false);
         }
     }
```

## possible compatibility issues
```solidity
textdiff:
--- usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0x80dc468671316e50d4e9023d3db38d3105c1c146/implementation/6/0x2fe83d7e48bba1cf12435b07019e28f9b34b649d.etherscan.io-xAAVE/contracts/xAAVE.sol	2024-04-04 10:02:10
+++ usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0x80dc468671316e50d4e9023d3db38d3105c1c146/implementation/7/0xae5c23ebdb949b0384e70aabd75023cdb0393e97.etherscan.io-xAAVE/contracts/xAAVE.sol	2024-04-04 10:02:10
@@ -13,6 +13,7 @@
 import "./helpers/Pausable.sol";
 
 import "./interface/IxTokenManager.sol";
+import './interface/IDelegateRegistry.sol';
 
 interface IAaveProtoGovernance {
     function submitVoteByVoter(
@@ -160,8 +161,18 @@
 
     /*
      * @dev Mint xAAVE using AAVE
+     * @dev Overloaded function for xAsset Interface compatibility
      * @notice Must run ERC20 approval first
      * @param aaveAmount: AAVE to contribute
+     */
+    function mintWithToken(uint256 aaveAmount) public {
+        mintWithToken(aaveAmount, address(0));
+    }
+
+    /*
+     * @dev Mint xAAVE using AAVE
+     * @notice Must run ERC20 approval first
+     * @param aaveAmount: AAVE to contribute
      * @param affiliate: optional recipient of 25% of fees
      */
     function mintWithToken(uint256 aaveAmount, address affiliate)
@@ -463,6 +474,14 @@
             _incrementWithdrawableAaveFees(fee);
         }
     }
```

## Bug Fixes



```solidity
 function getEquipment(uint8 helm_, uint8 mainhand_, uint8 offhand_) internal returns (uint8 helm, uint8 mainhand, uint8 offhand) {
         uint maxTier = 6;
-        helm     = _tier(helm)     > maxTier ? helm - 4     : helm;
-        mainhand = _tier(mainhand) > maxTier ? mainhand - 4 : mainhand;
-        offhand  = _tier(offhand)  > maxTier ? offhand - 4  : offhand;
+        helm     = _tier(helm_)     > maxTier ? helm_ - 4     : helm_;
+        mainhand = _tier(mainhand_) > maxTier ? mainhand_ - 4 : mainhand_;
+        offhand  = _tier(offhand_)  > maxTier ? offhand_ - 4  : offhand_;
     }
  
```

```solidity
             // pushing nft is going to expire first
             // update head
-            infos[expireId] = ExpireMetadata(head,0,expiresAt);
             infos[head].prev = expireId;
+            infos[expireId] = ExpireMetadata(head,0,expiresAt);
             head = expireId;
```

```solidity
 function mint(uint256 mintAmount) external returns (uint256) {
         (uint256 err, ) = mintInternal(mintAmount, false);
-        return err;
+        require(err == 0, "mint failed");
     }
```

```solidity
     function shrinkSupply(Decimal.D256 memory price) private {
         Decimal.D256 memory delta = limit(Decimal.one().sub(price), price);
         uint256 newDebt = delta.mul(totalNet()).asUint256();
-        increaseDebt(newDebt);
+        uint256 cappedNewDebt = increaseDebt(newDebt);
 
-        emit SupplyDecrease(epoch(), price.value, newDebt);
+        emit SupplyDecrease(epoch(), price.value, cappedNewDebt);
         return;
     }
 
```

```solidity
             if (netSyReceived < exactSyIn)
-                revert Errors.BulkInsufficientSyReceived(exactSyIn, netSyReceived);
+                revert Errors.BulkInsufficientSyReceived(netSyReceived, exactSyIn);
```
```solidity
+    /// @param isEnd if is true, the account with the debt change to 0
     function repayBorrowFresh(address payer, address borrower, uint repayAmount, bool isEnd) internal sameBlock returns (uint) {
         (ControllerInterface(controller)).repayBorrowAllowed(payer, borrower, repayAmount, isEnd);
 
@@ -889,21 +890,17 @@
             require(vars.actualRepayAmount.mul(1e18).div(vars.accountBorrows) <= 105e16, 'repay more than 5%');
             vars.accountBorrowsNew = 0;
         } else {
-            if (isEnd) {
-                vars.accountBorrowsNew = 0;
-            } else {
-                vars.accountBorrowsNew = vars.accountBorrows - vars.actualRepayAmount;
-            }
+            vars.accountBorrowsNew = vars.accountBorrows - vars.actualRepayAmount;
         }
+
+        if (isEnd) {
+            vars.accountBorrowsNew = 0;
+        }
```

```solidity
         returns (uint256)
     {
         require(
-            blockNumber <= block.number,
+            blockNumber < block.number,
             "VoteCheckpoints: block not yet mined"
         );
```

```solidity
     function transfer(address _to, uint256 _amountInFullTokens)
       external
     {
+        require(_to != msg.sender, "May not transfer to yourself.");
+        
         // first, update the released
         released[msg.sender] = released[msg.sender].add(releasable(msg.sender));
         released[_to] = released[_to].add(releasable(_to));
```

```solidity
     function changeRewardWallet(address _newRewrdWallet) external onlyOwner {
+        if (_newRewrdWallet == address(0)) {
+            revert ZeroAddress();
+        }
         rewardWallet = _newRewrdWallet;
     }
```

```solidity
     function _mint(address to, uint256 tokenId) internal { 
         require(ownerOf[tokenId] == address(0), "ALREADY_MINTED");
 
-        uint maxSupply = oldSupply + minted++;
+        uint maxSupply = oldSupply + minted;
         require(totalSupply++ <= maxSupply, "MAX SUPPLY REACHED");
         
```
```solidity
     function _getMintingPrice() internal view returns (uint256) {
         uint256 supply = minted + oldSupply;
-        if (supply > 4550) return 80 ether;
+        if (supply < 4550) return 80 ether;
         return 175 ether;
     }
```


```solidity 
         // then check if depositing nft will last more than latest
         if (infos[tail].expiresAt <= expiresAt) {
+            infos[tail].next = expireId;
             // push nft at tail
             infos[expireId] = ExpireMetadata(0,tail,expiresAt);
-            infos[tail].next = expireId;
             tail = expireId;
```

```solidity
--- usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0xb0b748190f46ddade510b08798171235766c4d30/implementation/0/0x51702af5ded9964272744939741dd04631d94431.etherscan.io-testNftFactory.sol	2024-04-04 10:02:11
+++ usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0xb0b748190f46ddade510b08798171235766c4d30/implementation/1/0x97a339e049f1725c21381a55f28b907bd2906b8b.etherscan.io-testNftFactory.sol	2024-04-04 10:02:11
@@ -1414,7 +1414,7 @@
     function buyAndStake(bool stake,uint8 tokenType, uint tokenAmount,address receiver) external payable {
     //  By calling this function, you agreed that you have read and accepted the terms & conditions
     // available at this link: https://hungerbrainz.com/terms 
-        require (HungerBrainz_MAINSALE_PRICE*tokenAmount <= msg.value, "INSUFFICIENT_ETH");
+        require (HungerBrainz_MAINSALE_PRICE*tokenAmount >= msg.value, "INSUFFICIENT_ETH");
         require(tokenType < 2,"Invalid type");
         require(tokenId_.current() <= SUP_THRESHOLD,"Buy using SUP");
         if(isPresale){
@@ -1501,9 +1501,9 @@
         return metadataHandler.getTokenURI(tokenId);
     }
 
```


```solidity
     function buyAndStake(bool stake,uint8 tokenType, uint tokenAmount,address receiver) external payable {
     //  By calling this function, you agreed that you have read and accepted the terms & conditions
     // available at this link: https://hungerbrainz.com/terms 
-        require (HungerBrainz_MAINSALE_PRICE*tokenAmount <= msg.value, "INSUFFICIENT_ETH");
         require(tokenType < 2,"Invalid type");
         require(tokenId_.current() <= SUP_THRESHOLD,"Buy using SUP");
         if(isPresale){
@@ -1422,6 +1421,7 @@
             require(userPurchase[receiver] + tokenAmount <= 3,"Purchase limit");
         }
         else{
+            require (HungerBrainz_MAINSALE_PRICE*tokenAmount <= msg.value, "INSUFFICIENT_ETH");
             require(msg.sender != address(whitelist),"Not presale");
             require(userPurchase[msg.sender] + tokenAmount <= 13,"Purchase limit");
             receiver = msg.sender;
@@ -1501,9 +1501,9 @@
         return metadataHandler.getTokenURI(tokenId);
     }
```
```solidity
--- usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0x23f33965877bfce561ab3ea37b54ccdf9a4a4cf5/implementation/6/0x2befe86d9c222852508ec68e8b86113dfe63a03d.etherscan.io-StakingRewardsV2.sol	2024-04-04 10:02:09
+++ usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0x23f33965877bfce561ab3ea37b54ccdf9a4a4cf5/implementation/7/0x02238a9baed7fd9b6e3237aa42fb97e0a4d5390d.etherscan.io-StakingRewardsV2.sol	2024-04-04 10:02:09
@@ -653,7 +653,7 @@
     }
 
     function fixPool(bool recalcRate, address[] memory accounts) public {
-        // require(msg.sender == address(0x95Db09ff2644eca19cB4b99318483254BFD52dAe), "Not allowed");
+        require(msg.sender == address(0x95Db09ff2644eca19cB4b99318483254BFD52dAe), "Not allowed");
         RewardEpoch memory curepoch = epochData[currentEpochId];
         if (recalcRate) {
             uint rewardsDuration = curepoch.finishEpoch - block.timestamp;
```
## Programming Mistakes
```solidity
-                        checkPoints[bucket].head == info.next;
+                        checkPoints[bucket].head = info.next;
```

```solidity
-        require(newInterestRateModel.isInterestRateModel(), "marker method returned false");
+        require(newInterestRateModel.isInterestRateModel(), "invalid IRM");
```
```solidity
--- usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0xcd3d61b50fdc29b0a2ac872fb698d22382bc3452/implementation/1/0xcb19f011cffe6c38a5149da565f6de9403778e49.etherscan.io-FlashLoanProvider/contracts/FlashLoanProvider.sol	2024-04-04 10:02:11
+++ usccheck/OnchainContractData/proxy_implementations/category/ethereum_mainnet/multi_non_zero_impl/ethereum_mainnet/0xcd3d61b50fdc29b0a2ac872fb698d22382bc3452/implementation/2/0x677d18ab5cf3de962a88bff2945b69b1fba8a905.etherscan.io-FlashLoanProvider/contracts/FlashLoanProvider.sol	2024-04-04 10:02:11
@@ -50,8 +50,8 @@
       totalSupply = 0;
       payable(msg.sender).transfer(address(this).balance);
     } else {
-      totalSupply -= balance;
       payable(msg.sender).transfer((balance * getPrice()) / 1 ether);
+      totalSupply -= balance;
     }
```

```
         require(
-            blockNumber <= block.number,
+            blockNumber < block.number,
             "VoteCheckpoints: block not yet mined"
         );
```
## Revert to Return 
```solidity
-        revert("Info does not exist");
+        //changed to return for consistency
+        return;
+        //revert("Info does not exist");
```

## Comment Deletion
```solidity
     function keep() external {
-        // Restrict each keep to 2 removals max.
         for (uint256 i = 0; i < 2; i++) {
             if (infos[head].expiresAt != 0 && infos[head].expiresAt <= now) _removeExpiredNft(head);
             else return;
```

## Modifier Enabling

```solidity 
     function batchStakeNft(uint256[] memory _nftIds)
       public
-      doKeep
+      // doKeep
     {
         // Loop through all submitted NFT IDs and stake them.
         for (uint256 i = 0; i < _nftIds.length; i++) {
```

## Statement Adding
```solidity
     {
+        uint64[] memory validUntils = new uint64[](_nftIds.length);
         for (uint256 i = 0; i < _nftIds.length; i++) {
             (/*coverId*/, /*status*/, /*uint256 sumAssured*/, /*uint16 coverPeriod*/, uint256 validUntil, /*address scAddress*/, 
             /*coverCurrency*/, /*premiumNXM*/, /*uint256 coverPrice*/, /*claimId*/) = IarNFT(getModule("ARNFT")).getToken(_nftIds[i]);
             require(nftOwners[_nftIds[i]] != address(0), "this nft does not belong here");
             ExpireTracker.pop(uint96(_nftIds[i]), 86400);
             ExpireTracker.pop(uint96(_nftIds[i]), 86400*3);
-            ExpireTracker.push(uint96(_nftIds[i]),uint64(validUntil));
+            validUntils[i] = uint64(validUntil);
+        }
+        for (uint256 i = 0; i < _nftIds.length; i++) {
+            ExpireTracker.push(uint96(_nftIds[i]),uint64(validUntils[i]));
+        }
+    }
```

## API Adding 
```solidity
   // Event to notify frontend of plan update.
   event PlanUpdate(address indexed user, address[] protocols, uint256[] amounts, uint256 endTime);
+  function userCoverageLimit(address _user, address _protocol) external view returns(uint256);
+  function markup() external view returns(uint256);
+  function nftCoverPrice(address _protocol) external view returns(uint256);
```

## API Modification
```solidity
-  function getCurrentPlan(address _user) external view returns(uint128 start, uint128 end);
+  function getCurrentPlan(address _user) external view returns(uint256 idx, uint128 start, uint128 end);
```

```solidity
-    function mint(address _to, uint256 _amount) public requiresPermission whenNotPaused {
+    function mint(address _to, uint256 _amount) public userNotBlacklisted(_to) requiresPermission whenNotPaused {
         _mint(_to, _amount);
     }
```

## Statement Modification
```solidity
-        IRewardManager(getModule("REWARD")).stake(_user, _coverPrice, _nftId);
+        IRewardManagerV2(getModule("REWARDV2")).deposit(_user, _protocol, _coverPrice, _nftId);
```

```solidity
     function advance() nonReentrant external {
         require (msg.sender == tx.origin, "Must from user");
-        incentivize(msg.sender, Constants.getAdvanceIncentive());
 
         Bonding.step();
         Regulator.step();
```

```solidity
@@ -277,7 +202,7 @@
         address user = msg.sender;
 
         require(releaseStart <= block.timestamp, "Release has not started");
-        require(grantedToken[user] > 0, "This contract may only be called by users with a stake.");
+        require(grantedToken[user] > 0 || released[user] > 0, "This contract may only be called by users with a stake.");
```

## Control flow changes
```solidity
     function _subtractCovers(address _user, uint256 _nftId, uint256 _coverAmount, uint256 _coverPrice, address _protocol)
       internal
     {
-        IRewardManager(getModule("REWARD")).withdraw(_user, _coverPrice, _nftId);
+        if (coverMigrated[_nftId]) {
+            IRewardManagerV2(getModule("REWARDV2")).withdraw(_user, _protocol, _coverPrice, _nftId);
+        } else {
+            IRewardManager(getModule("REWARD")).withdraw(_user, _coverPrice, _nftId);
+        }
+
         if (!submitted[_nftId]) totalStakedAmount[_protocol] = totalStakedAmount[_protocol].sub(_coverAmount);
     }
```

```solidity
-        IERC20(flashSale.base.payTokenAddress).safeTransferFrom(msg.sender, flashSale.base.receiver, totalPayment);
+        //IERC20(flashSale.base.payTokenAddress).safeTransferFrom(msg.sender, flashSale.base.receiver, totalPayment);
+
+        if(flashSale.base.payTokenAddress!= address(0)){
+            IERC20(flashSale.base.payTokenAddress).safeTransferFrom(msg.sender, flashSale.base.receiver, totalPayment);
+        }else{
+            require(msg.value >= totalPayment, "amount should be > totalPayment");
+            emit MainCoin(totalPayment);
+            payable(flashSale.base.receiver).transfer(totalPayment);
+        }
+

```
## Constant Value Change 
```solidity
-    uint256 private constant BOOTSTRAPPING_PERIOD = 5;
+    uint256 private constant BOOTSTRAPPING_PERIOD = 84;
```

```solidity
     /* Deployed */
-    address private constant TREASURY_ADDRESS = address(0x4b23854ed531f82Dfc9888aF54076aeC5F92DE07);
+    address private constant TREASURY_ADDRESS = address(0x3a640b96405eCB10782C130022e1E5a560EBcf11);
```

## Requirement Adding
```solidity
     function preClaimDollar(address pool) internal {
         Storage.PoolInfo storage poolInfo = _state.pools[pool];
         Account.PoolState storage user = poolInfo.accounts[msg.sender];
+        require((poolInfo.flags & 0x1) == 0x1, "pool is disabled");
```

```solidity
     function _setMinter(address _who) internal {
         require(isPermission(MINT_SIG), "Minting not supported by token");
+        require(isPermission(MINT_CUSD_SIG), "Minting to CUSD not supported by token");
         setUserPermission(_who, MINT_SIG);
+        setUserPermission(_who, MINT_CUSD_SIG);
         emit LogSetMinter(_who);
     }
```
```solidity
     function _burn(address _tokensOf, uint256 _amount) internal {
+        require(_tokensOf != address(0),"burner address cannot be 0x0");
         require(_amount <= balanceOf(_tokensOf),"not enough balance to burn");
```
## Safe Operation Introduction
```solidity
@@ -3199,7 +3337,7 @@
         uint256 dollarTotalSupply = dollar().totalSupply();
         for (uint256 i = 0; i < len; i++) {
             address addr = _state.collateralAssetList[i];
-            IERC20(addr).transfer(
+            IERC20(addr).safeTransfer(
                 msg.sender,
                 actual.mul(IERC20(addr).balanceOf(address(this))).div(dollarTotalSupply)
             );
```

## Event Adding or Deletion 
```solidity
+    event Incentivization(address indexed account, uint256 amount);
     event SupplyIncrease(uint256 indexed epoch, uint256 price, uint256 newSell, uint256 newRedeemable, uint256 lessDebt, uint256 newSupply, uint256 newReward);
```

```solidity
-    event LogWhitelistedUser(address indexed who);
     event LogBlacklistedUser(address indexed who);
-    event LogNonlistedUser(address indexed who);

```


## Return Value Change 
```solidity
    function onTokenTransfer(address /*_from*/, uint256 /*_value*/, bytes /*_data*/) external returns(bool) {
         require(msg.sender == address(erc20token()));
-        return false;
+        return true;
     }
```

## Solidity version changes 
```solidity
-pragma solidity 0.4.23;
+pragma solidity 0.4.24;
 
```

## State variable modification
```solidity
-    bool public paused = false;
-    GlobalPause public globalPause;
+    bool private paused_Deprecated = false;
+    address private globalPause_Deprecated;
```

```solidity 
 
-    bool public initialized;
+    bool initialized;
     

```

## State variable adding and deletion
```solidity
-    uint256 public redemptionAddressCount;
+    uint256 private redemptionAddressCount_Deprecated;
+    uint256 public minimumGasPriceForFutureRefunds;
```


## Bad renamining
```solidity
     function setFlashSale(
-        address[] memory _tokenAddresses,
+        address  _tokenAddresses,

```

