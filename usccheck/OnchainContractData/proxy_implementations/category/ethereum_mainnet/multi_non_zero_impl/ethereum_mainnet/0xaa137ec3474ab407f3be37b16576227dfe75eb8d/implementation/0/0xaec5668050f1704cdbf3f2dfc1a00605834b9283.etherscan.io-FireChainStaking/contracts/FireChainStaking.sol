// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import "hardhat/console.sol";

contract FireChainStaking is ReentrancyGuardUpgradeable {
    struct Stake {
        uint128 amount;
        uint128 unlockTime; // 45 days
        uint128 depositTime;
        uint128 claimedReward;
        bool claimed;
    }

    mapping(address => Stake) public userStake;
    mapping(address => uint128) public pendingReward;

    address public firechainToken;
    address public rewardWallet;
    address public owner;

    uint128 public totalStakes;
    uint128 private totalRewards;

    uint128 public lockInPeriod;
    uint64 public rewardRate;

    mapping(address => uint128) private withdrawTime;

    event Staked(
        address indexed user,
        uint128 amount,
        uint128 unlockTime,
        uint128 depositTime
    );
    
    event Withdrawn(address indexed user, uint128 amount, uint256 reward);
    event RewardRate(uint64 rewardRate);
    event LockinTime(uint128 lockinTime);
    event RewardStaked(uint256 amount);
    event ClaimedFireChainReward(address indexed user, uint256 amount);

    error ZeroAmount();
    error NoStakesFound();
    error LockinPeriodNotEnded(uint256 time);
    error LockinPeriodOver(uint256 time);
    error ZeroLockinPeriod(uint256 period);
    error ZeroAddress();
    error RewardWalletEmpty();

    constructor() {
        _disableInitializers();
    }

    function initialize(address _fireChainToken, address _rewardWallet) external  initializer() {
        if (_fireChainToken == address(0)) {
            revert ZeroAddress();
        }
        if (_rewardWallet == address(0)) {
            revert ZeroAddress();
        }
        owner = msg.sender;
        firechainToken = _fireChainToken;
        // lockInPeriod = 90 seconds;
        lockInPeriod = 45 days;
        rewardRate = 1200;    // 12% reward increase
        rewardWallet = _rewardWallet;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function.");
        _;
    }

    function stake(uint128 _amount) external nonReentrant {
        Stake storage userStakeData = userStake[msg.sender];
        if (_amount == 0) {
            revert ZeroAmount();
        }
       
        userStakeData.unlockTime = uint128(block.timestamp + lockInPeriod);
        uint256 reward = _calculateReward(msg.sender, userStakeData.amount);
        pendingReward[msg.sender] = pendingReward[msg.sender] + uint128(reward);

        userStakeData.amount += _amount;
        userStakeData.depositTime = uint128(block.timestamp);

        // userStake[msg.sender] = userStakeData;
        totalStakes += _amount;
        IERC20(firechainToken).transferFrom(msg.sender, address(this), _amount);
        if(userStakeData.claimed) userStakeData.claimed = false;
        emit Staked(
            msg.sender,
            _amount,
            userStakeData.unlockTime,
            userStakeData.depositTime
        );
    }

    function withdraw(uint128 _amount) public nonReentrant {
        Stake storage userStakeData = userStake[msg.sender];
        uint256 reward;
        if(userStakeData.amount <= 0 && _amount <= userStakeData.amount){
            revert NoStakesFound();
        }
        if (block.timestamp < userStakeData.unlockTime) {
            revert LockinPeriodNotEnded(block.timestamp);
        }
        uint128 pendingRewardAmount = pendingReward[msg.sender];
        uint128 amount = userStakeData.amount;
        
            reward = _calculateReward(msg.sender, amount);
            totalRewards += uint128(reward) + pendingRewardAmount;
            if (
                IERC20(firechainToken).balanceOf(rewardWallet) <=
                reward + pendingRewardAmount
            ) {
                revert RewardWalletEmpty();
            }
            totalStakes -= _amount;
            pendingReward[msg.sender] = 0;
            IERC20(firechainToken).transfer(msg.sender, _amount);
            IERC20(firechainToken).transferFrom(
                rewardWallet,
                msg.sender,
                reward + pendingRewardAmount
            );
            // userStakeData = Stake(
            //     amount - _amount,
            //     0,
            //     0,
            //     userStakeData.claimedReward +
            //         uint128(reward + pendingRewardAmount)
            // );
            userStake[msg.sender].amount = amount - _amount;
            userStake[msg.sender].claimedReward = userStakeData.claimedReward +
                    uint128(reward + pendingRewardAmount);
            pendingRewardAmount = 0;
            // userStake[msg.sender] = userStakeData;
            emit Withdrawn(msg.sender, _amount, reward);      
   
    }

    function stakeFireTokenReward() external nonReentrant {
        Stake storage userStakeData = userStake[msg.sender];
        uint256 currentReward = _calculateReward(
            msg.sender,
            userStakeData.amount
        );
        if (currentReward == 0) {
            revert ZeroAmount();
        }
        uint128 pendingRewardAmount = pendingReward[msg.sender];
        totalStakes += uint128(currentReward + pendingRewardAmount);

        userStakeData.amount =
            userStakeData.amount +
            uint128(currentReward + pendingRewardAmount);
        userStakeData.depositTime = uint128(block.timestamp);

        // userStake[msg.sender] = userStakeData;
        pendingReward[msg.sender] = 0;
        if (
            IERC20(firechainToken).balanceOf(rewardWallet) <
            currentReward + pendingRewardAmount
        ) {
            revert RewardWalletEmpty();
        }
        IERC20(firechainToken).transferFrom(
            rewardWallet,
            address(this),
            currentReward + pendingRewardAmount
        );
        emit RewardStaked(currentReward);
    }

    function claimReward() external nonReentrant {
        Stake storage userStakeData = userStake[msg.sender];
        uint256 reward;
        uint128 pendingRewardAmount = pendingReward[msg.sender];

        if (userStakeData.amount <= 0) {
            revert NoStakesFound();
        }
        reward = _calculateReward(msg.sender, userStakeData.amount);
        if (reward <= 0) {
            revert ZeroAmount();
        }
        totalRewards += uint128(reward + pendingRewardAmount);

        userStakeData.depositTime = uint128(block.timestamp);
        userStakeData.claimedReward =
            userStakeData.claimedReward +
            uint128(reward + pendingRewardAmount);

        pendingReward[msg.sender] = 0;
        // userStake[msg.sender] = userStakeData;
        if (
            IERC20(firechainToken).balanceOf(rewardWallet) <
            reward + pendingRewardAmount
        ) {
            revert RewardWalletEmpty();
        }
        IERC20(firechainToken).transferFrom(
            rewardWallet,
            msg.sender,
            reward + pendingRewardAmount
        );
        emit ClaimedFireChainReward(msg.sender, reward);
    }

    function changeRewardWallet(address _newRewrdWallet) external onlyOwner {
        rewardWallet = _newRewrdWallet;
    }

    function setLockInPeriod(uint128 period) external onlyOwner {
        lockInPeriod = period;
        emit LockinTime(lockInPeriod);
    }

    function changeOwner(address _address) external onlyOwner {
        if (_address == address(0)) {
            revert ZeroAddress();
        }
        owner = _address;
    }

    function calculateReward(
        address user,
        uint128 _amount
    ) internal view returns (uint256 reward) {
        if(userStake[user].unlockTime > block.timestamp){
          uint256 time = (block.timestamp - userStake[user].depositTime);
        reward = (_amount * rewardRate * time) / (365 days * 100 * 100);
        }else if(!userStake[user].claimed) {
        reward = (_amount * rewardRate * lockInPeriod) / (365 days * 100 * 100);
        }
        return reward;
    }

    function _calculateReward(
        address user,
        uint128 _amount
    ) internal returns (uint256 reward) {
        if(userStake[user].unlockTime > block.timestamp){
          uint256 time = (block.timestamp - userStake[user].depositTime);
        reward = (_amount * rewardRate * time) / (365 days * 100 * 100);
        }else if(!userStake[user].claimed) {
        reward = (_amount * rewardRate * lockInPeriod) / (365 days * 100 * 100);
        userStake[user].claimed = true;
        }
        return reward;
    }

    function getTotalStakes() external view returns (uint128) {
        return totalStakes;
    }

    function getTotalRewards() external view returns (uint128) {
        return totalRewards;
    }

    function getUserReward(
        address _add
    ) external view returns (uint256 _reward) {
        _reward = calculateReward(_add, userStake[_add].amount);
    }
}

