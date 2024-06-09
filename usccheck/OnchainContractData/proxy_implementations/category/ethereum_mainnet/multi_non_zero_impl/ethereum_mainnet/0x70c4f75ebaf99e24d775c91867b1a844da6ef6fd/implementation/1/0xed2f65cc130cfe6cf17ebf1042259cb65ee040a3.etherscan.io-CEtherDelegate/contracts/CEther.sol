// SPDX-License-Identifier: BSD-3-Clause
pragma solidity 0.8.23;

import "contracts/CToken.sol";

/**
 * @title Compound's CEther Contract
 * @notice CToken which wraps Ether
 * @author Compound
 */
contract CEther is CToken, CEtherInterface {

    IWeth public immutable weth;

    /**
     * @notice Construct a new CEther money market
     * @param weth_ The address of the Wrapped Ether contract
     */
    constructor(IWeth weth_) {
        admin = payable(msg.sender);
        weth = weth_;
    }

    /**
     * @notice Initialize a new CEther money market
     * @param comptroller_ The address of the Comptroller
     * @param interestRateModel_ The address of the interest rate model
     * @param initialExchangeRateMantissa_ The initial exchange rate, scaled by 1e18
     * @param name_ ERC-20 name of this token
     * @param symbol_ ERC-20 symbol of this token
     * @param decimals_ ERC-20 decimal precision of this token
     */
    function initialize(ComptrollerInterface comptroller_,
                InterestRateModel interestRateModel_,
                uint initialExchangeRateMantissa_,
                string memory name_,
                string memory symbol_,
                uint8 decimals_) override public {

        marketType = CTokenStorage.MarketType.ERC20_MARKET;

        super.initialize(comptroller_, interestRateModel_, initialExchangeRateMantissa_, name_, symbol_, decimals_);

        underlying = 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE;
    }


    /*** User Interface ***/

    /**
     * @notice Sender supplies assets into the market and receives cTokens in exchange
     * @dev Reverts upon any failure
     */
    function mint() override external payable {

        comptroller.autoEnterMarkets(msg.sender); // silent failure allowed

        mintInternal(msg.value);
    }

    /**
     * @notice Sender redeems cTokens in exchange for the underlying asset
     * @dev Accrues interest whether or not the operation succeeds, unless reverted
     * @param redeemTokens The number of cTokens to redeem into underlying
     * @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
     */
    function redeem(uint redeemTokens) override external returns (uint) {
        redeemInternal(redeemTokens);
        return NO_ERROR;
    }

    /**
     * @notice Sender redeems cTokens in exchange for a specified amount of underlying asset
     * @dev Accrues interest whether or not the operation succeeds, unless reverted
     * @param redeemAmount The amount of underlying to redeem
     * @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
     */
    function redeemUnderlying(uint redeemAmount) override external returns (uint) {
        redeemUnderlyingInternal(redeemAmount);
        return NO_ERROR;
    }

    /**
      * @notice Sender borrows assets from the protocol to their own address
      * @param borrowAmount The amount of the underlying asset to borrow
      * @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
      */
    function borrow(uint borrowAmount) override external returns (uint) {

        comptroller.autoEnterMarkets(msg.sender); // silent failure allowed

        borrowInternal(borrowAmount);
        return NO_ERROR;
    }

    /**
     * @notice Sender repays their own borrow
     * @dev Reverts upon any failure
     */
    function repayBorrow() override external payable {
        repayBorrowInternal(msg.value);
    }

    /**
     * @notice Sender repays a borrow belonging to borrower
     * @dev Reverts upon any failure
     * @param borrower the account with the debt being payed off
     */
    function repayBorrowBehalf(address borrower) override external payable {
        repayBorrowBehalfInternal(borrower, msg.value);
    }

    /**
     * @notice Borrows are repaid by another user (possibly the borrower).
     * @param payer the account paying off the borrow
     * @param borrower the account with the debt being payed off
     * @param repayAmount the amount of underlying tokens being returned, or -1 for the full outstanding amount
     * @return (uint) the actual repayment amount.
     */
    function repayBorrowFresh(address payer, address borrower, uint repayAmount) internal virtual override returns (uint) {
        /* Fail if repayBorrow not allowed */
        uint allowed = comptroller.repayBorrowAllowed(address(this), payer, borrower, repayAmount);
        if (allowed != 0) {
            revert RepayBorrowComptrollerRejection(allowed);
        }

        /* Verify market's block number equals current block number */
        if (accrualBlockNumber != getBlockNumber()) {
            revert RepayBorrowFreshnessCheck();
        }

        /* We fetch the amount the borrower owes, with accumulated interest */
        uint accountBorrowsPrev = borrowBalanceStoredInternal(borrower);

        /////////////////////////
        // EFFECTS & INTERACTIONS
        // (No safe failures beyond this point)

        /*
         * We call doTransferIn for the payer and the repayAmount
         *  Note: The cToken must handle variations between ERC-20 and ETH underlying.
         *  On success, the cToken holds an additional repayAmount of cash.
         *  doTransferIn reverts if anything goes wrong, since we can't be sure if side effects occurred.
         *   it returns the amount actually transferred, in case of a fee.
         */
        uint actualRepayAmount = doTransferIn(payer, repayAmount);

        // actualRepayAmount == msg.value
        if (actualRepayAmount > accountBorrowsPrev) {
            // refund overage to payer
            doTransferOut(payable(payer), actualRepayAmount - accountBorrowsPrev);

            actualRepayAmount = accountBorrowsPrev;
        }

        /*
         * We calculate the new borrower and total borrow balances, failing on underflow:
         *  accountBorrowsNew = accountBorrows - actualRepayAmount
         *  totalBorrowsNew = totalBorrows - actualRepayAmount
         */
        uint accountBorrowsNew = accountBorrowsPrev - actualRepayAmount;
        uint totalBorrowsNew = totalBorrows > actualRepayAmount ? totalBorrows - actualRepayAmount : 0;

        /* We write the previously calculated values into storage */
        accountBorrows[borrower].principal = accountBorrowsNew;
        accountBorrows[borrower].interestIndex = borrowIndex;
        totalBorrows = totalBorrowsNew;

        /* We emit a RepayBorrow event */
        emit RepayBorrow(payer, borrower, actualRepayAmount, accountBorrowsNew, totalBorrowsNew);

        if (accountBorrowsNew == 0 && accountTokens[borrower] == 0) {
            comptroller.autoExitMarkets(borrower); // silent failure allowed
        }

        return actualRepayAmount;
    }

    /**
     * @notice The liquidator liquidates the borrowers collateral.
     *  This function can only be called by the Comptroller.
     * @param liquidator The liquidator who called Comptroller::batchLiquidateBorrow
     * @param borrower The borrower of this cToken to be liquidated
     * @param repayAmount The amount of the underlying borrowed asset to repay. This amount must be provided in WETH.
     * @return uint The amount of the underlying borrowed asset that was actually repaid
     */
    function _liquidateBorrow(address liquidator, address borrower, uint repayAmount) override external returns (uint) {
        weth.transferFrom(liquidator, address(this), repayAmount);
        weth.withdraw(repayAmount);
        return _liquidateBorrowInternal(liquidator, borrower, repayAmount);
    }

    /**
     * @notice The sender adds to reserves.
     * @return uint 0=success, otherwise a failure (see ErrorReporter.sol for details)
     */
    function _addReserves() override external payable returns (uint) {
        return _addReservesInternal(msg.value);
    }

    /**
     * @notice A public function to sweep accidental ERC-20 transfers to this contract. Tokens are sent to admin (timelock)
     * @param token The address of the ERC-20 token to sweep
     */
    function sweepToken(EIP20NonStandardInterface token) override external {
        if (msg.sender != admin) {
            revert Unauthorized();
        }
        uint256 balance = token.balanceOf(address(this));
        token.transfer(admin, balance);
    }

    /**
     * @notice Send Ether to CEther to mint
     */
    receive() external payable {
        if (msg.sender != address(weth)) {
            comptroller.autoEnterMarkets(msg.sender); // silent failure allowed
            mintInternal(msg.value);
        }
    }

    /*** Safe Token ***/

    /**
     * @notice Gets balance of this contract in terms of Ether, before this message
     * @dev This excludes the value of the current message, if any
     * @return The quantity of Ether owned by this contract
     */
    function getCashPrior() override internal view returns (uint) {
        return address(this).balance - msg.value;
    }

    /**
     * @notice Perform the actual transfer in, which is a no-op
     * @param from Address sending the Ether
     * @param amount Amount of Ether being sent
     * @return The actual amount of Ether transferred
     */
    function doTransferIn(address from, uint amount) override internal returns (uint) {
        // Sanity checks
        if (msg.sender != address(comptroller)) {
            if (msg.sender != from) {
                revert SenderMismatch();
            }
            if (msg.value != amount) {
                revert ValueMismatch();
            }
        }
        return amount;
    }

    function doTransferOut(address payable to, uint amount) virtual override internal {
        (bool success,) = to.call{value: amount}("");
        if (!success) {
            revert TransferOutFailed();
        }
    }

    function _ensureNonEmpty(address minter, uint amount) override external {
        weth.transferFrom(minter, address(this), amount);
        weth.withdraw(amount);
        _ensureNonEmptyInternal(minter, amount);
    }
}
