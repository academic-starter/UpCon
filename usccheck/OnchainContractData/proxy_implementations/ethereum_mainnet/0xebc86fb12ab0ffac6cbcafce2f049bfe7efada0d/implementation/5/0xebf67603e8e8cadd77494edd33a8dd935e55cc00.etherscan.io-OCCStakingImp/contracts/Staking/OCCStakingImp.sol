// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/math/Math.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "./../Ownable.sol";
import "./../interfaces/IGovernanceNFT.sol";
import "./FractionalExponents.sol";

// Staking implementation 
// The proportion of CHAKRA reward is calculated from square root of the stake rather than linearly
// In this version we remove functions related to reward distribution, because now it is taken care of by a separate contract. The main reason is we want to consider the stake across all chain where Occam operates, so it is not possible anymore to have the reward calculation in separate SC instances
contract OCCStakingImp is Ownable, ReentrancyGuard {
    using SafeMath for uint;
    using SafeERC20 for IERC20;

    IERC20 public OCC;
    mapping(address => uint) public stakes; // needs sr version
    uint256 public totalStake; // needs sr version

    uint256[] public checkPoints; // needs sr version
    uint256[] public rewardPerSecond; 
    uint256 public lastUpdateTime;
    uint256 public rewardPerTokenStored; // per 1 OCC, i.e. per 10**18 units // needs sr version, which is already rewardPerTokenStored

    mapping(address => uint256) public userRewardPerTokenPaid; // needs sr version, which is already ChakraUserRewardPerTokenPaid
    mapping(address => uint256) public rewards;

    uint public unstakingFeeRatio;
    uint public newUnstakingFeeRatio;
    uint public unstakingFeeRatioTimelock;
    uint public constant unstakingFeeRatioTimelockPeriod = 600;
    uint public constant unstakingFeeDenominator = 10000;
    uint public constant OCCUnits = 1e18;

    bool public initialized = false;
    uint public startingCheckPoint;

    IGovernanceNFT public governanceNFT;
    uint public minimalStakeForNFT;

    // new variables from the upgrade, need to be last to avoid storage conflict
    // mimic the variables of OCC but for Chakra
    IERC20 public Chakra;
    mapping(address => uint) public exponentiatedStakes;
    // since we cannot update the exponentiated stake for each user individually, the change will be make the first time user interacts with the SC
    // It needs to be call in the updateReward hook, because it is considered for CHAKRA reward calculation
    mapping(address => bool) public exponentiatedStakesAlreadyUpdated;
    uint256 public totalExponentiatedStake;
    uint256[] public ChakraCheckPoints; 
    uint256[] public ChakraRewardPerSecond; 
    uint256 public ChakraRewardPerTokenStored; // per 1 Chakra, i.e. per 10**18 units

    mapping(address => uint256) public ChakraUserRewardPerTokenPaid;
    mapping(address => uint256) public ChakraRewards;
    uint public ChakraStartingCheckPoint;

    uint32 public ChakraExponentNumerator = 1;
    uint32 public ChakraExponentDenominator = 2;
    uint256 public constant ChakraThresholdForReward = 200 * 10 ** 18;

    // we will deploy the fractionalExponents contract separately instead of inherit it to avoid storage conflict during upgrade
    FractionalExponents public fractionalExponents;
    // flag to make sure that owner can only set totalExponentiatedStake once after upgrade
    bool public totalExponentiatedStakeAlreadySet;


    event CreateStake(address indexed caller, uint amount);
    event RemoveStake(address indexed caller, uint amount);
    event TransferStake(address indexed from, address indexed to, uint amount);
    event RewardPaid(address indexed user, uint256 reward);

    constructor(address _owner) Ownable(_owner) {}
    
    function initialize(
        address _OCC,
        uint _unstakingFeeRatio,
        address _owner,
        uint emissionStart,
        uint firstCheckPoint,
        uint _rewardPerSecond,
        address _governanceNFT,
        uint _minimalStakeForNFT
    ) 
        public 
    {
        require(initialized == false, "OCCStakingImp: contract has already been initialized.");
        OCC = IERC20(_OCC);
        unstakingFeeRatio = _unstakingFeeRatio;
        newUnstakingFeeRatio = _unstakingFeeRatio;
        if (checkPoints.length == 0) {
            checkPoints.push(emissionStart);
            checkPoints.push(firstCheckPoint);
            rewardPerSecond.push(_rewardPerSecond);
        }
        owner = _owner;
        governanceNFT = IGovernanceNFT(_governanceNFT);
        minimalStakeForNFT = _minimalStakeForNFT;
        initialized = true;
    }

    function createStake(uint stake) public nonReentrant updateReward(msg.sender) {
        OCC.safeTransferFrom(msg.sender, address(this), stake);
        stakes[msg.sender] = stakes[msg.sender].add(stake);
        totalStake = totalStake.add(stake);

        updateNFTIfNecessary(msg.sender);
        emit CreateStake(msg.sender, stake);
    }

    function createStakeFor(uint stake, address to) public nonReentrant updateReward(to) {
        OCC.safeTransferFrom(msg.sender, address(this), stake);
        stakes[to] = stakes[to].add(stake);
        totalStake = totalStake.add(stake);

        updateNFTIfNecessary(to);
        emit CreateStake(to, stake);
    }

    function getRewardThenStake() public nonReentrant updateReward(msg.sender) {
        uint256 reward = rewards[msg.sender];
        if (reward > 0) {
            require(reward < OCC.balanceOf(address(this)).sub(totalStake), "OCCStaking: not enough tokens to pay out reward.");
            rewards[msg.sender] = 0;
            stakes[msg.sender] = stakes[msg.sender].add(reward);
            totalStake = totalStake.add(reward);

            updateNFTIfNecessary(msg.sender);
            emit CreateStake(msg.sender, reward);
            emit RewardPaid(msg.sender, reward);
        }
    }

    function removeStake(uint stake, uint maximumFee) public nonReentrant updateReward(msg.sender) {
        uint unstakingFee = stake.mul(unstakingFeeRatio).div(unstakingFeeDenominator);
        require(unstakingFee <= maximumFee, "OCCStaking: fee too high.");
        uint stakeWithoutFee = stake.sub(unstakingFee);
        require(stakes[msg.sender] >= stake, "OCCStaking: INSUFFICIENT_STAKE");
        stakes[msg.sender] = stakes[msg.sender].sub(stake);
        totalStake = totalStake.sub(stake);

        OCC.safeTransfer(msg.sender, stakeWithoutFee);
        updateNFTIfNecessary(msg.sender);
        emit RemoveStake(msg.sender, stake);
    }

    function transferStake(address _recipient, uint _amount) public {
        require(_amount <= stakes[msg.sender], "OCCStakingImp: not enough stake to transfer");
        _updateReward(msg.sender);
        _updateReward(_recipient);
        stakes[msg.sender] = stakes[msg.sender].sub(_amount);
        stakes[_recipient] = stakes[_recipient].add(_amount);
        updateNFTIfNecessary(msg.sender);
        updateNFTIfNecessary(_recipient);
        emit RemoveStake(msg.sender, _amount);
        emit CreateStake(_recipient, _amount);
    }

    function getReward() public nonReentrant updateReward(msg.sender) {
        uint256 reward = rewards[msg.sender];
        if (reward > 0) {
            require(reward <= OCC.balanceOf(address(this)).sub(totalStake), "OCCStaking: not enough tokens to pay out reward.");
            rewards[msg.sender] = 0;
            OCC.safeTransfer(msg.sender, reward);
            emit RewardPaid(msg.sender, reward);
        }
    }

    function showPendingReward(address account) public view returns (uint256) {
        uint rewardPerTokenStoredActual;
        if (totalStake != 0) {
            (uint256 totalEmittedTokensSinceLastUpdate, ) = getTotalEmittedTokens(lastUpdateTime, block.timestamp, startingCheckPoint);
            rewardPerTokenStoredActual = rewardPerTokenStored.add(totalEmittedTokensSinceLastUpdate.mul(OCCUnits).div(totalStake));
        } else {
            rewardPerTokenStoredActual = rewardPerTokenStored;
        }
        return rewards[account].add((rewardPerTokenStoredActual.sub(userRewardPerTokenPaid[account])).mul(stakes[account]).div(OCCUnits));
    }

    function _updateReward(address account) internal {
        if (totalStake != 0) {
            (uint256 totalEmittedTokensSinceLastUpdate, uint256 newStartingCheckPoint) = getTotalEmittedTokens(lastUpdateTime, block.timestamp, startingCheckPoint);
            startingCheckPoint = newStartingCheckPoint;
            rewardPerTokenStored = rewardPerTokenStored.add(totalEmittedTokensSinceLastUpdate.mul(OCCUnits).div(totalStake));
        }
        lastUpdateTime = lastTimeRewardApplicable();
        if (account != address(0)) {
            uint256 _rewardPerTokenStored = rewardPerTokenStored;
            rewards[account] = rewards[account].add((_rewardPerTokenStored.sub(userRewardPerTokenPaid[account])).mul(stakes[account]).div(OCCUnits));
            userRewardPerTokenPaid[account] = _rewardPerTokenStored;
        }
    }
    modifier updateReward(address account) {
        _updateReward(account);
        _;
    }

    function getStake(address user) public view returns (uint) {
        return stakes[user];
    }

    function setNewUnstakingFeeRatio(uint _newUnstakingFeeRatio) public onlyOwner {
        require(_newUnstakingFeeRatio <= unstakingFeeDenominator, "OCCStaking: invalid unstaking fee.");
        newUnstakingFeeRatio = _newUnstakingFeeRatio;
        unstakingFeeRatioTimelock = block.timestamp.add(unstakingFeeRatioTimelockPeriod);
    }

    function changeUnstakingFeeRatio() public onlyOwner {
        require(block.timestamp >= unstakingFeeRatioTimelock, "OCCStaking: too early to change unstaking fee.");
        unstakingFeeRatio = newUnstakingFeeRatio;
    }

    function updateSchedule(uint checkPoint, uint _rewardPerSecond) public onlyOwner {
        uint lastCheckPoint = checkPoints[checkPoints.length.sub(1)];
        require(checkPoint > Math.max(lastCheckPoint, block.timestamp), "LM: new checkpoint has to be in the future");
        if (block.timestamp > lastCheckPoint) {
            checkPoints.push(block.timestamp);
            rewardPerSecond.push(0);
        }
        checkPoints.push(checkPoint);
        rewardPerSecond.push(_rewardPerSecond);
    }

    function getCheckPoints() public view returns (uint256[] memory) {
        return checkPoints;
    }

    function getRewardPerSecond() public view returns (uint256[] memory) {
        return rewardPerSecond;
    }

    function lastTimeRewardApplicable() public view returns (uint256) {
        return Math.min(block.timestamp, checkPoints[checkPoints.length.sub(1)]);
    }

    function getTotalEmittedTokens(uint256 _from, uint256 _to, uint256 _startingCheckPoint) public view returns (uint256, uint256) {
        require(_to >= _from, "LM: _to has to be greater than _from.");
        uint256 totalEmittedTokens = 0;
        uint256 workingTime = Math.max(_from, checkPoints[0]);
        if (_to <= workingTime) {
            return (0, _startingCheckPoint);
        }
        uint checkPointsLength = checkPoints.length;
        for (uint256 i = _startingCheckPoint + 1; i < checkPointsLength; ++i) {
            uint256 emissionTime = checkPoints[i];
            uint256 emissionRate = rewardPerSecond[i-1];
            if (_to < emissionTime) {
                totalEmittedTokens = totalEmittedTokens.add(_to.sub(workingTime).mul(emissionRate));
                return (totalEmittedTokens, i-1);
            } else if (workingTime < emissionTime) {
                totalEmittedTokens = totalEmittedTokens.add(emissionTime.sub(workingTime).mul(emissionRate));
                workingTime = emissionTime;
            }
        }
        return (totalEmittedTokens, checkPointsLength.sub(1));
    }


    /**
     * @dev changes the minimum stake required to earn an NFT.
     *   When changing this value, NFT ownership of stakers that are now above or below the threshold is not changed.
     *   THis function is also used after an upgrade because when the initialize function was already called.
     * @param _newMinimalStakeForNFT the new minimum stake required to earn an NFT.
     */
    function changeMinimalStakeForNFT(uint _newMinimalStakeForNFT) public onlyOwner {
        minimalStakeForNFT = _newMinimalStakeForNFT;
    }

    /**
     * @dev changes the address of the governance NFT.
     *   THis function is also used after an upgrade because when the initialize function was already called.
     * @param _newGovernanceNFT new address of the governance NFT.
     */
    function changeGovernanceNFT(address _newGovernanceNFT) public onlyOwner {
        governanceNFT = IGovernanceNFT(_newGovernanceNFT);
    }

    /**
     * @dev Ensure that if and only if the staker has enough OCC staked for a staking tier he/she has a governance NFT.
     * @param stakeOwner Address of the staker to check
     */
    function updateNFTIfNecessary(address stakeOwner) internal {
        if (stakes[stakeOwner] >= minimalStakeForNFT) {
            // mint NFT if the user does not have one already
            if (governanceNFT.balanceOf(stakeOwner) == 0) {
                governanceNFT.mint(stakeOwner);
            }
        } else {
            // burn NFT if the user had one before
            if (governanceNFT.balanceOf(stakeOwner) > 0) {
                governanceNFT.burn(stakeOwner);
            }
        }
        // otherwise the user keeps his NFT
        // NFT traits are changed by the backend server reacting on the Events CreateStake, RemoveStake and TransferStake
    }
}