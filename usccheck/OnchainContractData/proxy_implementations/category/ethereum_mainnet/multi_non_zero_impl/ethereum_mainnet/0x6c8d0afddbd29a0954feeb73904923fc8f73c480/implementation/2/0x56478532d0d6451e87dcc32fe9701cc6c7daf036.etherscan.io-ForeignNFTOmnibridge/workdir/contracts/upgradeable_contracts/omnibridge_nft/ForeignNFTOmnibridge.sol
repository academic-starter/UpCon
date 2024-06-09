pragma solidity 0.7.5;
// solhint-disable-next-line compiler-version
pragma abicoder v2;

import "./BasicNFTOmnibridge.sol";
import "./components/common/GasLimitManager.sol";

/**
 * @title ForeignNFTOmnibridge
 * @dev Foreign side implementation for multi-token ERC721 mediator intended to work on top of AMB bridge.
 * It is designed to be used as an implementation contract of EternalStorageProxy contract.
 */
contract ForeignNFTOmnibridge is BasicNFTOmnibridge, GasLimitManager {
    constructor(string memory _suffix) BasicNFTOmnibridge(_suffix) {}

    /**
     * @dev Stores the initial parameters of the mediator.
     * @param _bridgeContract the address of the AMB bridge contract.
     * @param _mediatorContract the address of the mediator contract on the other network.
     * @param _requestGasLimit the gas limit for the message execution.
     * @param _owner address of the owner of the mediator contract.
     * @param _imageERC721 address of the ERC721 token image.
     * @param _imageERC1155 address of the ERC1155 token image.
     */
    function initialize(
        address _bridgeContract,
        address _mediatorContract,
        uint256 _requestGasLimit,
        address _owner,
        address _imageERC721,
        address _imageERC1155
    ) external onlyRelevantSender returns (bool) {
        require(!isInitialized());

        _setBridgeContract(_bridgeContract);
        _setMediatorContractOnOtherSide(_mediatorContract);
        _setRequestGasLimit(_requestGasLimit);
        _setOwner(_owner);
        _setTokenImageERC721(_imageERC721);
        _setTokenImageERC1155(_imageERC1155);

        setInitialize();

        return isInitialized();
    }

    /**
     * @dev Internal function for sending an AMB message to the mediator on the other side.
     * @param _data data to be sent to the other side of the bridge.
     * @param _useOracleLane always true, not used on this side of the bridge.
     * @return id of the sent message.
     */
    function _passMessage(bytes memory _data, bool _useOracleLane) internal override returns (bytes32) {
        (_useOracleLane);

        return bridgeContract().requireToPassMessage(mediatorContractOnOtherSide(), _data, requestGasLimit());
    }
    
    // Selector: 0x7f083f69
    function migrationTo3_0_0() external {
        bytes32 migratedTo3_0_0Storage = 0xd8ad6d205355cc8dd4d88d650469f4d3230596fa9345b86d1d97034a771009ba; // keccak256(abi.encodePacked("migrationTo3_0_020210530"))
        require(!boolStorage[migratedTo3_0_0Storage]);
        
        _setTokenImageERC721(0x8b9E7c13F98291fe90b38E020BcB046f4A4Dd21d);
        _setTokenImageERC1155(0xF714C3aA632ecE07Eeba241803b26f806EA17908);
        
        boolStorage[migratedTo3_0_0Storage] = true;
    }

    
}
