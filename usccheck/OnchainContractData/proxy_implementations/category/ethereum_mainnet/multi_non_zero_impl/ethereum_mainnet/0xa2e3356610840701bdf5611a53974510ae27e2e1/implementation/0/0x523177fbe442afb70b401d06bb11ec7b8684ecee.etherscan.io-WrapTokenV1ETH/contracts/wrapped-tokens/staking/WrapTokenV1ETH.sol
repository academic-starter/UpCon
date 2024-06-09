// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.6.12;

import "./StakedTokenV1.sol";

contract WrapTokenV1ETH is StakedTokenV1 {
    /**
     * @dev gas limit of eth transfer.
     */
    uint256 private constant _ETH_TRANSFER_GAS = 5000;

    /**
     * @dev Function to deposit eth to the contract for wBETH
     * @param referral The referral address
     */
    function deposit(address referral) external payable {
        require(msg.value > 0, "zero ETH amount");

        // msg.value and exchangeRate are all scaled by 1e18
        uint256 wBETHUnit = 10 ** uint256(decimals);
        uint256 wBETHAmount = msg.value.mul(wBETHUnit).div(exchangeRate());

        _mint(msg.sender, wBETHAmount);

        emit DepositEth(msg.sender, msg.value, wBETHAmount, referral);
    }

    /**
     * @dev Function to supply eth to the contract
     */
    function supplyEth() external payable onlyOperator {
        require(msg.value > 0, "zero ETH amount");

        emit SuppliedEth(msg.sender, msg.value);
    }

    /**
     * @dev Function to move eth to the ethReceiver
     * @param amount The eth amount to move
     */
    function moveToStakingAddress(uint256 amount) external onlyOperator {
        require(
            amount > 0,
            "withdraw amount cannot be 0"
        );

        address _ethReceiver = ethReceiver();
        require(_ethReceiver != address(0), "zero ethReceiver");

        require(amount <= address(this).balance, "balance not enough");
        (bool success, ) = _ethReceiver.call{value: amount, gas: _ETH_TRANSFER_GAS}("");
        require(success, "transfer failed");

        emit MovedToStakingAddress(_ethReceiver, amount);
    }
}
