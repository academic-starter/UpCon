// SPDX-License-Identifier: GPL-3.0-or-later
// Deployed with donations via Gitcoin GR9

pragma solidity 0.7.6;
pragma abicoder v2;

import '../libraries/Orders.sol';

interface ITwapDelay {
    event OrderExecuted(uint256 indexed id, bool indexed success, bytes data, uint256 gasSpent, uint256 ethRefunded);
    event RefundFailed(address indexed to, address indexed token, uint256 amount, bytes data);
    event EthRefund(address indexed to, bool indexed success, uint256 value);
    event OwnerSet(address owner);
    event BotSet(address bot, bool isBot);
    event DelaySet(uint256 delay);
    event RelayerSet(address relayer);
    event MaxGasLimitSet(uint256 maxGasLimit);
    event GasPriceInertiaSet(uint256 gasPriceInertia);
    event MaxGasPriceImpactSet(uint256 maxGasPriceImpact);
    event TransferGasCostSet(address token, uint256 gasCost);
    event ToleranceSet(address pair, uint16 amount);
    event NonRebasingTokenSet(address token, bool isNonRebasing);
    event OrderDisabled(address pair, Orders.OrderType orderType, bool disabled);
    event UnwrapFailed(address to, uint256 amount);

    function factory() external returns (address);

    function relayer() external returns (address);

    function owner() external returns (address);

    function isBot(address bot) external returns (bool);

    function tolerance(address pair) external returns (uint16);

    function isNonRebasingToken(address token) external view returns (bool);

    function gasPriceInertia() external returns (uint256);

    function gasPrice() external view returns (uint256);

    function maxGasPriceImpact() external returns (uint256);

    function maxGasLimit() external returns (uint256);

    function delay() external returns (uint256);

    function totalShares(address token) external returns (uint256);

    function weth() external returns (address);

    function getTransferGasCost(address token) external returns (uint256);

    function getDepositDisabled(address pair) external returns (bool);

    function getWithdrawDisabled(address pair) external returns (bool);

    function getBuyDisabled(address pair) external returns (bool);

    function getSellDisabled(address pair) external returns (bool);

    function getOrderStatus(uint256 orderId, uint256 validAfterTimestamp) external view returns (Orders.OrderStatus);

    function setOrderDisabled(
        address pair,
        Orders.OrderType orderType,
        bool disabled
    ) external payable;

    function setOwner(address _owner) external payable;

    function setBot(address _bot, bool _isBot) external payable;

    function setMaxGasLimit(uint256 _maxGasLimit) external payable;

    function setDelay(uint32 _delay) external payable;

    function setRelayer(address _relayer) external payable;

    function setGasPriceInertia(uint256 _gasPriceInertia) external payable;

    function setMaxGasPriceImpact(uint256 _maxGasPriceImpact) external payable;

    function setTransferGasCost(address token, uint256 gasCost) external payable;

    function setTolerance(address pair, uint16 amount) external payable;

    function setNonRebasingToken(address token, bool isNonRebasing) external payable;

    function deposit(Orders.DepositParams memory depositParams) external payable returns (uint256 orderId);

    function withdraw(Orders.WithdrawParams memory withdrawParams) external payable returns (uint256 orderId);

    function sell(Orders.SellParams memory sellParams) external payable returns (uint256 orderId);

    function relayerSell(Orders.SellParams memory sellParams) external payable returns (uint256 orderId);

    function buy(Orders.BuyParams memory buyParams) external payable returns (uint256 orderId);

    function execute(Orders.Order[] calldata orders) external payable;

    function retryRefund(Orders.Order calldata order) external;

    function cancelOrder(Orders.Order calldata order) external;
}
