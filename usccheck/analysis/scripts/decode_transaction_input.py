from web3 import Web3
import json
import traceback
# Initialize a Web3 provider (e.g., Infura, local node)
w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YourInfuraProjectId'))


def convert_bytes_hexstring(val):
    if isinstance(val, bytes):
        return "0x" + val.hex()
    else:
        if isinstance(val, list):
            val = [convert_bytes_hexstring(sub_val) for sub_val in val]
            return val
        elif isinstance(val, dict):
            for key, _val in val.items():
                val[key] = convert_bytes_hexstring(_val)
            return val
        else:
            return val


def decode_transaction_input(contract_abi, input_data):
    # Decode input data using contract ABI
    try:
        decoded_input = w3.eth.contract(
            abi=contract_abi).decode_function_input(input_data)

        func = decoded_input[0].abi
    except:
        return None
    try:
        inputs = decoded_input[1]
        for variable in inputs:
            inputs[variable] = convert_bytes_hexstring(inputs[variable])
        decoded_input = dict(func=func, inputs=inputs)
        # decoded_input_str = json.dumps(decoded_input)
        return decoded_input
    except:
        print("wrong input:", decoded_input)
        return None


def test():
    # Example usage
    contract_abi = [
        {
            "constant": False,
            "inputs": [
                {
                    "name": "x",
                    "type": "uint256"
                }
            ],
            "name": "set",
            "outputs": [],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "constant": True,
            "inputs": [],
            "name": "get",
            "outputs": [
                {
                    "name": "",
                    "type": "uint256"
                }
            ],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        }
    ]

    input_data = '0x60fe47b10000000000000000000000000000000000000000000000000000000000000003e8'
    # input_data = '0x60fe47b20000000000000000000000000000000000000000000000000000000000000003e8'

    decoded_input = decode_transaction_input(contract_abi, input_data)

    print("Decoded input:")
    print(decoded_input)


test()
