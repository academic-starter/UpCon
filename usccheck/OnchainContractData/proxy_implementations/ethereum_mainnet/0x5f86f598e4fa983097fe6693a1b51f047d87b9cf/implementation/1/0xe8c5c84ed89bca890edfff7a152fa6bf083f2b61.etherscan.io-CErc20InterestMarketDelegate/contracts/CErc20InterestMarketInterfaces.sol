// SPDX-License-Identifier: BSD-3-Clause
pragma solidity 0.8.23;

import "contracts/CTokenInterfaces.sol";


contract CErc20InterestMarketStorage {

    uint public totalVirtual;
}

abstract contract CErc20InterestMarketInterface is CErc20Interface, CErc20InterestMarketStorage {

    /**
     * @notice Collect the interest from supplied ERC721 tokens for the lender and adds them to his supply.
     *         Must be called by the supply market.
     * @param lender The address for which the interest should be collected
     * @param interestTokens The amount of market tokens to claim
     * @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
     */
    function collectInterest(address lender, uint interestTokens) virtual external returns (uint);

    /**
     * @notice Pay the interest for borrowed ERC721 tokens.
     *         Must be called by the borrow market.
     * @param payer The address that pays the interest
     * @param interestTokens The amount of market tokens to pay
     * @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
     */
    function payInterest(address payer, uint interestTokens) virtual external returns (uint);

    /**
     * @notice Sender claims interest from NFT markets then redeems cTokens in exchange for the underlying asset
     * @dev Accrues interest whether or not the operation succeeds, unless reverted
     * @param redeemTokens The number of cTokens to redeem into underlying
     * @param cTokens The list of cToken addresses to redeem interest from.
     *                Only possible for cErc721 markets.
     * @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
     */
    function redeemWithClaim(uint redeemTokens, address[] memory cTokens) virtual external returns (uint);

    /**
     * @notice Sender claims interest from NFT markets then redeems cTokens in exchange for a specified amount of underlying asset
     * @dev Accrues interest whether or not the operation succeeds, unless reverted
     * @param redeemAmount The amount of underlying to redeem
     * @param cTokens The list of cToken addresses to redeem interest from.
     *                Only possible for cErc721 markets.
     * @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
     */
    function redeemUnderlyingWithClaim(uint redeemAmount, address[] memory cTokens) virtual external returns (uint);

    event CollectInterest(address supplyMarket, address lender, uint interestTokens);
    event PayInterest(address borrowMarket, address payer, uint interestTokens);
}
