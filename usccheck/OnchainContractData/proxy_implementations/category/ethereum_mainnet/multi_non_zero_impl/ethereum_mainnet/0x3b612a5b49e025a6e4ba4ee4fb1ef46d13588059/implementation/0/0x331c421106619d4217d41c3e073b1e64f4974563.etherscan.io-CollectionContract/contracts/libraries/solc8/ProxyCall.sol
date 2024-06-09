// SPDX-License-Identifier: MIT OR Apache-2.0

pragma solidity ^0.8.0;

import "@openzeppelin/contracts-solc-8/utils/Address.sol";
import "../../interfaces/solc8/IProxyCall.sol";

/**
 * @notice Forwards arbitrary calls to an external contract to be processed.
 * @dev This is used so that the from address of the calling contract does not have
 * any special permissions (e.g. ERC-20 transfer).
 */
library ProxyCall {
  using Address for address payable;

  /**
   * @dev Used by other mixins to make external calls through the proxy contract.
   * This will fail if the proxyCall address is address(0).
   */
  function proxyCallAndReturnContractAddress(
    IProxyCall proxyCall,
    address externalContract,
    bytes memory callData
  ) internal returns (address payable result) {
    result = proxyCall.proxyCallAndReturnAddress(externalContract, callData);
    require(result.isContract(), "ProxyCall: address returned is not a contract");
  }
}
