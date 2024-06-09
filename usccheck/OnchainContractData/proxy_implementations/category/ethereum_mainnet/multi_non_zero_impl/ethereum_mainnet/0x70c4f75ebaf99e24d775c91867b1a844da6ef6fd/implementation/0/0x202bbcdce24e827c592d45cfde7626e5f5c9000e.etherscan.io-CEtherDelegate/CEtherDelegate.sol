// SPDX-License-Identifier: BSD-3-Clause
pragma solidity 0.8.23;

import "CEther.sol";

contract CEtherDelegate is CEther, CDelegateInterface {
    /**
     * @notice Construct an empty delegate
     */
    constructor(IWeth weth_) CEther(weth_) {}

    /**
     * @notice Called by the delegator on a delegate to initialize it for duty
     * @param data The encoded bytes data for any initialization
     */
    function _becomeImplementation(bytes memory data) virtual override public {
        // Shh -- currently unused
        data;

        // Shh -- we don't ever want this hook to be marked pure
        if (false) {
            implementation = address(0);
        }

        if (msg.sender != admin) {
            revert Unauthorized();
        }
    }

    /**
     * @notice Called by the delegator on a delegate to forfeit its responsibility
     */
    function _resignImplementation() virtual override public {
        // Shh -- we don't ever want this hook to be marked pure
        if (false) {
            implementation = address(0);
        }

        if (msg.sender != admin) {
            revert Unauthorized();
        }
    }
}
