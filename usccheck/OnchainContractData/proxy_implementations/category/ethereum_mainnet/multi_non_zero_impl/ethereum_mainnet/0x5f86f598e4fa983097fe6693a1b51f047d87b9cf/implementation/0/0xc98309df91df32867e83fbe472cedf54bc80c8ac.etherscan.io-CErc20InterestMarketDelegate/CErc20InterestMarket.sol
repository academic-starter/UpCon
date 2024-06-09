// SPDX-License-Identifier: BSD-3-Clause
pragma solidity 0.8.23;

import "CErc20.sol";
import "CErc20InterestMarketInterfaces.sol";

contract CErc20InterestMarket is CErc20, CErc20InterestMarketInterface {

    function initialize(address underlying_,
                        ComptrollerInterface comptroller_,
                        InterestRateModel interestRateModel_,
                        uint initialExchangeRateMantissa_,
                        string memory name_,
                        string memory symbol_,
                        uint8 decimals_) public {
        super.initialize(underlying_, comptroller_, interestRateModel_, initialExchangeRateMantissa_, name_, symbol_, decimals_, CTokenStorage.MarketType.ERC20_INTEREST_MARKET);
    }

    /**
     * @notice Collect the interest from supplied ERC721 tokens for the lender and adds them to his supply.
     *         Must be called by the supply market.
     * @param lender The address for which the interest should be collected
     * @param interestTokens The amount of market tokens to claim
     * @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
     */
    function collectInterest(address lender, uint interestTokens) override external nonReentrant returns (uint) {
        accrueInterest();
        collectInterestInternal(msg.sender, lender, interestTokens);

        return NO_ERROR;
    }

    /**
     * @notice Collect the interest from supplied ERC721 tokens for the lender and adds them to his supply.
     * @param supplyMarket The market on which the interest accrued
     * @param lender The address for which the interest should be collected
     * @param interestTokens The amount of market tokens to claim
     */
    function collectInterestInternal(address supplyMarket, address lender, uint interestTokens) internal {
        if (interestTokens == 0) {
            return;
        }

        /* Fail if collect interest not allowed */
        uint allowed = comptroller.collectInterestAllowed(address(this), supplyMarket, lender, interestTokens);
        if (allowed != 0) {
            revert CollectInterestNotAllowed();
        }

        uint remainingTokens;
        uint heldBalance = accountTokens[address(this)];
        if (heldBalance > interestTokens) {
            accountTokens[address(this)] = heldBalance - interestTokens;
            emit Transfer(address(this), address(0), interestTokens);
        } else {
            accountTokens[address(this)] = 0;
            emit Transfer(address(this), address(0), heldBalance);

            remainingTokens = interestTokens - heldBalance;
        }

        if (remainingTokens != 0) {
            /* We artificially inflate the supply with a virtual balance */
            totalSupply = totalSupply + remainingTokens;
            totalVirtual = totalVirtual + remainingTokens;
        }

        accountTokens[lender] = accountTokens[lender] + interestTokens;
        emit Transfer(address(0), lender, interestTokens);
    }

    /**
     * @notice Pay the interest for borrowed ERC721 tokens.
     *         Must be called by the borrow market.
     * @param payer The address that pays the interest
     * @param interestTokens The amount of market tokens to pay
     * @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
     */
    function payInterest(address payer, uint interestTokens) override external nonReentrant returns (uint) {
        accrueInterest();
        payInterestInternal(msg.sender, payer, interestTokens);

        return NO_ERROR;
    }

    /**
     * @notice Pay the interest for borrowed ERC721 tokens.
     * @param borrowMarket The market on which the interest accrued
     * @param payer The address that pays the interest
     * @param interestTokens The amount of market tokens to pay
     */
    function payInterestInternal(address borrowMarket, address payer, uint interestTokens) internal {
        if (interestTokens == 0) {
            return;
        }

        // payer interest market balance is reduced to cover interest being paid
        uint balancePayer = accountTokens[payer];
        if (balancePayer < interestTokens) {
            revert InsufficientBalance();
        }

        /* Fail if pay interest not allowed */
        uint allowed = comptroller.payInterestAllowed(address(this), borrowMarket, payer, interestTokens);
        if (allowed != 0) {
            revert PayInterestNotAllowed();
        }

        accountTokens[payer] = balancePayer - interestTokens;
        emit Transfer(payer, address(0), interestTokens);

        uint totalVirtual_ = totalVirtual;
        uint heldBalance;
        if (interestTokens > totalVirtual_) {
            heldBalance = interestTokens - totalVirtual_;
            totalSupply = totalSupply - totalVirtual_;
            totalVirtual = 0;
        } else {
            totalSupply = totalSupply - interestTokens;
            totalVirtual = totalVirtual_ - interestTokens;
        }

        if (heldBalance != 0) {
            // keep a reserve of cToken
            accountTokens[address(this)] = accountTokens[address(this)] + heldBalance;
            emit Transfer(address(0), address(this), heldBalance);
        }
    }

    /**
     * @notice Sender claims interest from NFT markets then redeems cTokens in exchange for the underlying asset
     * @dev Accrues interest whether or not the operation succeeds, unless reverted
     * @param redeemTokens The number of cTokens to redeem into underlying
     * @param cTokens The list of cToken addresses to redeem interest from.
     *                Only possible for cErc721 markets.
     * @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
     */
    function redeemWithClaim(uint redeemTokens, address[] memory cTokens) override external returns (uint) {

        comptroller.redeemAllInterest(msg.sender, cTokens);

        redeemInternal(redeemTokens);
        return NO_ERROR;
    }

    /**
     * @notice Sender claims interest from NFT markets then redeems cTokens in exchange for a specified amount of underlying asset
     * @dev Accrues interest whether or not the operation succeeds, unless reverted
     * @param redeemAmount The amount of underlying to redeem
     * @param cTokens The list of cToken addresses to redeem interest from.
     *                Only possible for cErc721 markets.
     * @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
     */
    function redeemUnderlyingWithClaim(uint redeemAmount, address[] memory cTokens) override external returns (uint) {

        comptroller.redeemAllInterest(msg.sender, cTokens);

        redeemUnderlyingInternal(redeemAmount);
        return NO_ERROR;
    }

    /**
     * @notice Calculates the exchange rate from the underlying to the CToken
     * @dev This function does not accrue interest before calculating the exchange rate
     * @return calculated exchange rate scaled by 1e18
     */
    function exchangeRateStoredInternal() override internal view returns (uint) {

        uint _totalSupply = totalSupply;
        uint _totalVirtual = totalVirtual;
        
        // it should be impossible for totalVirtual to be greater than totalSupply
        assert(_totalSupply >= _totalVirtual);

        _totalSupply = _totalSupply - _totalVirtual;

        if (_totalSupply == 0) {
            /*
             * If there are no tokens minted:
             *  exchangeRate = initialExchangeRate
             */
            return initialExchangeRateMantissa;
        } else {
            /*
             * Otherwise:
             *  exchangeRate = (totalCash + totalBorrows - totalReserves) / totalSupply
             */
            uint totalCash = getCashPrior();
            uint cashPlusBorrowsMinusReserves = totalCash + totalBorrows - totalReserves;
            uint exchangeRate = cashPlusBorrowsMinusReserves * expScale / _totalSupply;

            return exchangeRate;
        }
    }

    /**
     * @notice A public function to sweep accidental ERC-20 transfers to this contract. Tokens are sent to admin (timelock)
     * @param token The address of the ERC-20 token to sweep
     */
    function sweepToken(EIP20NonStandardInterface token) override external {
        if (msg.sender != admin) {
            revert Unauthorized();
        }
        if (address(token) == underlying || address(token) == address(this)) {
            revert CannotSweepUnderlying();
        }
        uint256 balance = token.balanceOf(address(this));
        token.transfer(admin, balance);
    }
}
