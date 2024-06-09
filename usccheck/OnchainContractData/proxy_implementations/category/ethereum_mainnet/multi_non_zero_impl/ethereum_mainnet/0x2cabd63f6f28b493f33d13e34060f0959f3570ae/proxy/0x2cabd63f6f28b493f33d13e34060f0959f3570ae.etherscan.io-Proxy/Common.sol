/*
  Copyright 2019-2021 StarkWare Industries Ltd.

  Licensed under the Apache License, Version 2.0 (the "License").
  You may not use this file except in compliance with the License.
  You may obtain a copy of the License at

  https://www.starkware.co/open-source-license/

  Unless required by applicable law or agreed to in writing,
  software distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions
  and limitations under the License.
*/
// SPDX-License-Identifier: Apache-2.0.
pragma solidity ^0.6.11;

/*
  Common Utility librarries.
  I. Addresses (extending address).
*/
library Addresses {
    function isContract(address account) internal view returns (bool) {
        uint256 size;
        assembly {
            size := extcodesize(account)
        }
        return size > 0;
    }

    function performEthTransfer(address recipient, uint256 amount) internal {
        (bool success, ) = recipient.call{value: amount}(""); 
        require(success, "ETH_TRANSFER_FAILED");
    }

    /*
      Safe wrapper around ERC20/ERC721 calls.
      This is required because many deployed ERC20 contracts don't return a value.
      See https://github.com/ethereum/solidity/issues/4116.
    */
    function safeTokenContractCall(address tokenAddress, bytes memory callData) internal {
        require(isContract(tokenAddress), "BAD_TOKEN_ADDRESS");
        
        (bool success, bytes memory returndata) = tokenAddress.call(callData);
        require(success, string(returndata));

        if (returndata.length > 0) {
            require(abi.decode(returndata, (bool)), "TOKEN_OPERATION_FAILED");
        }
    }

    /*
      Similar to safeTokenContractCall, but always ignores the return value.

      Assumes some other method is used to detect the failures
      (e.g. balance is checked before and after the call).
    */
    function uncheckedTokenContractCall(address tokenAddress, bytes memory callData) internal {
        
        (bool success, bytes memory returndata) = tokenAddress.call(callData);
        require(success, string(returndata));
    }

}

library UintArray {
    function hashSubArray(uint256[] memory array, uint256 subArrayStart, uint256 subArraySize)
        internal pure
        returns(bytes32 subArrayHash)
    {
        require(array.length >= subArrayStart + subArraySize, "ILLEGAL_SUBARRAY_DIMENSIONS");
        uint256 startOffsetBytes = 0x20 * (1 + subArrayStart);
        uint256 dataSizeBytes = 0x20 * subArraySize;
        assembly {
            subArrayHash := keccak256(add(array, startOffsetBytes), dataSizeBytes)
        }
    }

    /*
      Returns the address of a cell in offset within a uint256[] array.
      This allows assigning new variable of dynamic unit256[] pointing to a sub_array
      with a layout of serialied uint256[] (i.e. length+content).
    */
    function extractSerializedUintArray(uint256[] memory programOutput, uint256 offset)
        internal pure
        returns (uint256[] memory addr)
    {
        uint256 memOffset = 0x20 * (offset + 1);
        assembly {
            addr := add(programOutput, memOffset)
        }
    }

}

/*
  II. StarkExTypes - Common data types.
*/
library StarkExTypes {

    // Structure representing a list of verifiers (validity/availability).
    // A statement is valid only if all the verifiers in the list agree on it.
    // Adding a verifier to the list is immediate - this is used for fast resolution of
    // any soundness issues.
    // Removing from the list is time-locked, to ensure that any user of the system
    // not content with the announced removal has ample time to leave the system before it is
    // removed.
    struct ApprovalChainData {
        address[] list;
        // Represents the time after which the verifier with the given address can be removed.
        // Removal of the verifier with address A is allowed only in the case the value
        // of unlockedForRemovalTime[A] != 0 and unlockedForRemovalTime[A] < (current time).
        mapping (address => uint256) unlockedForRemovalTime;
    }
}
