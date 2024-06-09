/*
  Copyright 2019-2023 StarkWare Industries Ltd.

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
pragma solidity ^0.8.0;

/**
  StorageSlots holds the arbitrary storage slots used throughout the Proxy pattern.
  Storage address slots are a mechanism to define an arbitrary location, that will not be
  overlapped by the logical contracts.
*/
contract StorageSlots {
    // Storage slot with the address of the current implementation.
    // We need to keep this variable stored outside of the commonly used space,
    // so that it's not overrun by the logical implementation (the proxied contract).
    // Web3.keccak(text="StarkWare2019.implemntation-slot").
    bytes32 internal constant IMPLEMENTATION_SLOT =
        0x177667240aeeea7e35eabe3a35e18306f336219e1386f7710a6bf8783f761b24;

    // Storage slot with the address of the call-proxy current implementation.
    // We need to keep this variable stored outside of the commonly used space.
    // so that it's not overrun by the logical implementation (the proxied contract).
    // Web3.keccak(text="StarkWare2020.CallProxy.Implemntation.Slot").
    bytes32 internal constant CALL_PROXY_IMPL_SLOT =
        0x7184681641399eb4ad2fdb92114857ee6ff239f94ad635a1779978947b8843be;

    // This storage slot stores the finalization flag.
    // Once the value stored in this slot is set to non-zero
    // the proxy blocks implementation upgrades.
    // The current implementation is then referred to as Finalized.
    // Web3.keccak(text="StarkWare2019.finalization-flag-slot").
    bytes32 internal constant FINALIZED_STATE_SLOT =
        0x7d433c6f837e8f93009937c466c82efbb5ba621fae36886d0cac433c5d0aa7d2;

    // Storage slot to hold the upgrade delay (time-lock).
    // The intention of this slot is to allow modification using an EIC.
    // Web3.keccak(text="StarkWare.Upgradibility.Delay.Slot").
    bytes32 public constant UPGRADE_DELAY_SLOT =
        0xc21dbb3089fcb2c4f4c6a67854ab4db2b0f233ea4b21b21f912d52d18fc5db1f;

    // Storage slot to hold the upgrade eanbled duration in seconds.
    // The intention of this slot is to allow modification using an EIC.
    // Web3.keccak(text="StarkWare.Upgradibility.EnableWindowDuration.Slot").
    bytes32 public constant ENABLE_WINDOW_DURATION_SLOT =
        0xb00a6109e73dbe7bbf8d3f18fb9221d2d024dc2671e3d5ff02532ccc40590738;
}
