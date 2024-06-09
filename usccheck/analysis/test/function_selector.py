from eth_utils import keccak


def compute_function_selector(signature):
    # Hash the function signature using Keccak-256
    hash_bytes = keccak(text=signature)

    # Extract the first 4 bytes (function selector)
    function_selector = hash_bytes[:4]

    # Convert bytes to hexadecimal string
    selector_hex = function_selector.hex()

    return selector_hex


# Example usage:
function_signature = "initialize()"
selector = compute_function_selector(function_signature)
print("Function selector:", selector)
