// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC721/IERC721.sol";
import "@openzeppelin/contracts/token/ERC1155/IERC1155.sol";
import "@openzeppelin/contracts/token/ERC721/utils/ERC721Holder.sol";
import "@openzeppelin/contracts/token/ERC1155/utils/ERC1155Holder.sol";
import "@openzeppelin/contracts/proxy/utils/UUPSUpgradeable.sol";
import "./upgrade/Pausable.sol";
import "./upgrade/ReentrancyGuard.sol";
import "./interfaces/IUniswapV3SwapRouter.sol";
import "./interfaces/IWeth.sol";
import "./interfaces/IBaseGatewayEthereumV2.sol";

abstract contract BaseGatewayEthereumV2 is ERC721Holder, ERC1155Holder, ReentrancyGuard, Pausable, UUPSUpgradeable, IBaseGatewayEthereumV2 {
    using SafeERC20 for IERC20;
    //https://stackoverflow.com/questions/69706835/how-to-check-if-the-token-on-opensea-is-erc721-or-erc1155-using-node-js
    bytes4 internal constant INTERFACE_ID_ERC721 = 0x80ac58cd;
    bytes4 internal constant INTERFACE_ID_ERC1155 = 0xd9b67a26;
    uint256 public constant BASE_WEIGHTS = 1000000;
    uint256 internal constant DEFAULT_SWAP_DEADLINE_IN_SECOND = 60;

    struct NFTContractInfo {
        // list of weights by fomula
        uint256 weightsFomulaBase;
        uint256 weightsFomulaLottery;
        // pool address for each fomula
        address poolAddressBase;
        address poolAddressLottery;
        uint256 amounts; // total deposit token amount
        bool increaseable; // applying for the secondary markets transaction weights increasement or not
        uint256 delta; // percentage for each valid transaction increaced
        bool active;
    }

    // key was packed by contract address and token Id
    mapping(bytes32 => NFTTokenInfo) public tokenInfo;
    mapping(bytes32 => uint256) public tokenRewardBalance; // for periodic settlement of lottery reward token
    mapping(address => NFTContractInfo) public contractInfo;
    mapping(address => uint256) public poolsWeights;
    mapping(address => uint256) public poolsBalances;

    string public name;
    address public wrapperNativeToken;
    address public stablecoin;
    address public rewardToken;
    address public operator;
    IUniswapV3SwapRouter public router;

    function initialize(string memory _name, address _wrapperNativeToken, address _stablecoin, address _rewardToken, address _owner, IUniswapV3SwapRouter _router, uint256 _redeemableTime) virtual external {}

    function implementation() external view returns (address) {
        return _getImplementation();
    }

    function withdraw(address _to) external override onlyOwner {
        uint256 balance = address(this).balance;

        require(payable(_to).send(balance), "Fail to withdraw");

        emit Withdraw(_to, balance);
    }

    function withdrawWithERC20(address _token, address _to) external override onlyOwner {
        uint256 balance = IERC20(_token).balanceOf(address(this));

        IERC20(_token).transfer(_to, balance);

        emit WithdrawERC20(_token, _to, balance);
    }

    function convertExactWEthToStablecoin(uint256 amountIn, uint256 amountOutMinimum) internal returns (uint256) {
        require(msg.value > 0, "Must pass non 0 ETH amount");
        
        uint256 deadline = block.timestamp + 15; // using 'now' for convenience, for mainnet pass deadline from frontend!
        address tokenIn = wrapperNativeToken;
        address tokenOut = stablecoin;
        uint24 fee = 3000;
        address recipient = address(this);
        uint160 sqrtPriceLimitX96 = 0;

        IUniswapV3SwapRouter.ExactInputSingleParams memory params = IUniswapV3SwapRouter.ExactInputSingleParams(
            tokenIn,
            tokenOut,
            fee,
            recipient,
            deadline,
            amountIn,
            amountOutMinimum,
            sqrtPriceLimitX96
        );
        
        uint256 output = router.exactInputSingle(params);
        return output;
    }

    function _authorizeUpgrade(address newImplementation) internal view override onlyOwner {}

    modifier supportInterface(address _nft) {
        require(IERC721(_nft).supportsInterface(INTERFACE_ID_ERC721), "Address is not ERC1155 or ERC721");
        _;
    }

    event Withdraw(address _to, uint256 balance);
    event WithdrawERC20(address _token, address _to, uint256 balance);
    event Deposit(address _nft, uint256 _tokenId, uint256 _value);
    event Redeem(address _nft, uint256 _tokenId, uint256 _value);
    event RedeemAll(address _pool, uint256 _value);
    event RedeemAllCollection(address _nft, uint256 _value);
}