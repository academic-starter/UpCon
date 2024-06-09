/*
  Copyright 2019-2024 StarkWare Industries Ltd.

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
pragma solidity ^0.8.20;

// Starknet L1 handler selectors.
uint256 constant HANDLE_DEPOSIT_SELECTOR = 1285101517810983806491589552491143496277809242732141897358598292095611420389;
uint256 constant HANDLE_TOKEN_DEPOSIT_SELECTOR = 774397379524139446221206168840917193112228400237242521560346153613428128537;

uint256 constant HANDLE_DEPOSIT_WITH_MESSAGE_SELECTOR = 247015267890530308727663503380700973440961674638638362173641612402089762826;

uint256 constant HANDLE_TOKEN_DEPLOYMENT_SELECTOR = 1737780302748468118210503507461757847859991634169290761669750067796330642876;

uint256 constant TRANSFER_FROM_STARKNET = 0;
uint256 constant UINT256_PART_SIZE_BITS = 128;
uint256 constant UINT256_PART_SIZE = 2**UINT256_PART_SIZE_BITS;
uint256 constant MAX_PENDING_DURATION = 5 days;
address constant BLOCKED_TOKEN = address(0x1);

// Cairo felt252 value (short string) of 'ETH'
address constant ETH = address(0x455448);
