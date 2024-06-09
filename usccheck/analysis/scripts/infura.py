from eth_utils import keccak
import os
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()
API_KEY = os.getenv("API_KEY")
web3s = dict()

infura_url_map = {
    "ethereum": {
        "mainnet": f"https://mainnet.infura.io/v3/{API_KEY}",
        "goerli": f"https://goerli.infura.io/v3/{API_KEY}",
        "sepolia": f"https://sepolia.infura.io/v3/{API_KEY}"
    },
    "linea": {
        "mainnet": f"https://linea-mainnet.infura.io/v3/{API_KEY}",
        "goerli": f"https://linea-goerli.infura.io/v3/{API_KEY}"
    },
    "polygon": {
        "mainnet": f"https://polygon-mainnet.infura.io/v3/{API_KEY}",
        "amoy": f"https://polygon-amoy.infura.io/v3/{API_KEY}",
        "mumbai": f"https://polygon-mumbai.infura.io/v3/{API_KEY}"
    },
    "optimism": {
        "mainnet": f"https://optimism-mainnet.infura.io/v3/{API_KEY}",
        "sepolia": f"https://optimism-sepolia.infura.io/v3/{API_KEY}"
    },
    "arbitrum": {
        "mainnet": f"https://arbitrum-mainnet.infura.io/v3/{API_KEY}",
        "sepolia": f"https://arbitrum-sepolia.infura.io/v3/{API_KEY}"
    },
    "palm": {
        "mainnet": f"https://palm-mainnet.infura.io/v3/{API_KEY}",
        "testnet": f"https://palm-testnet.infura.io/v3/{API_KEY}"
    },
    "avalanche": {
        "fuji": f"https://avalanche-fuji.infura.io/v3/{API_KEY}",
        "mainnet": f"https://avalanche-mainnet.infura.io/v3/{API_KEY}"
    },
    "starknet": {
        "fuji": f"https://starknet-goerli.infura.io/v3/{API_KEY}",
        "mainnet": f"https://starknet-mainnet.infura.io/v3/{API_KEY}",
        "sepolia": f"https://starknet-sepolia.infura.io/v3/{API_KEY}"
    },
    "starknet": {
        "alfajores": f"https://celo-alfajores.infura.io/v3/{API_KEY}",
        "mainnet": f"https://celo-mainnet.infura.io/v3/{API_KEY}"
    },
}


def compute_function_selector(signature):
    # Hash the function signature using Keccak-256
    hash_bytes = keccak(text=signature)

    # Extract the first 4 bytes (function selector)
    function_selector = hash_bytes[:4]

    # Convert bytes to hexadecimal string
    selector_hex = function_selector.hex()

    return selector_hex


def get_latest_block(chain, network):
    infura_url = infura_url_map[chain][network]
    if infura_url in web3s:
        web3 = web3s[infura_url]
    else:
        web3 = Web3(Web3.HTTPProvider(infura_url))
        web3s[infura_url] = web3
    result = web3.eth.get_block_number()
    return result


def get_implementation(chain, network, address, block=None):
    infura_url = infura_url_map[chain][network]
    if infura_url in web3s:
        web3 = web3s[infura_url]
    else:
        web3 = Web3(Web3.HTTPProvider(infura_url))
        web3s[infura_url] = web3
    if block is None:
        block = get_latest_block(chain=chain, network=network)

    result = web3.eth.call({
        "to": Web3.to_checksum_address(address),
        "data": "0x5c60da1b"
    }, block_identifier=block
    )
    return result[-20:].hex(), block


def func_call(address, func_abi_without_parameters, chain="ethereum", network="mainnet", block=None):
    infura_url = infura_url_map[chain][network]
    if infura_url in web3s:
        web3 = web3s[infura_url]
    else:
        web3 = Web3(Web3.HTTPProvider(infura_url))
        web3s[infura_url] = web3
    if block is None:
        block = get_latest_block(chain=chain, network=network)

    func_signature_str = func_abi_without_parameters["name"] + "(" + ",".join(
        [item["type"] for item in func_abi_without_parameters["inputs"]]) + ")"

    func_signature = compute_function_selector(func_signature_str)
    print(func_signature, func_signature_str)

    result = web3.eth.call({
        "to": Web3.to_checksum_address(address),
        "data": func_signature
    }, block_identifier=block
    )
    return result[-20:].hex(), block


def code_exists(address, chain="ethereum", network="mainnet", block=None):
    infura_url = infura_url_map[chain][network]
    if infura_url in web3s:
        web3 = web3s[infura_url]
    else:
        web3 = Web3(Web3.HTTPProvider(infura_url))
        web3s[infura_url] = web3
    if block is None:
        block = get_latest_block(chain=chain, network=network)
    try:
        code = web3.eth.get_code(account=Web3.to_checksum_address(
            address), block_identifier=block)
        # print(code, code.hex())
        if code is None or code.hex() == "0x":
            return False
        else:
            return True
    except:
        # import traceback
        # traceback.print_exc()
        return False


def test_function_call():
    latest_block = get_latest_block(chain="ethereum", network="mainnet")
    address = "0xa9f731e5122953791b69180978edf3a03d285771"
    func_abi = {'constant': False, 'inputs': [], 'name': 'initialize', 'outputs': [
    ], 'payable': False, 'stateMutability': 'nonpayable', 'type': 'function'}
    result = func_call(chain="ethereum", network="mainnet",
                       address=address, func_abi_without_parameters=func_abi, block=latest_block)
    print(result)


def test_get_implementation():
    latest_block = get_latest_block(chain="ethereum", network="mainnet")
    print(latest_block)
    result = get_implementation(chain="ethereum", network="mainnet",
                                address="0x25200235ca7113c2541e70de737c41f5e9acd1f6", block=latest_block)
    print(result)


if __name__ == "__main__":
    # test_function_call()
    result = code_exists("0xd02732b7383fd0c3617dc406cf9250bb7e6517f7")
    print(result)
