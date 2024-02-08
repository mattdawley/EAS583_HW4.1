"""
    We are agnostic about how the students submit their merkle proofs to the on-chain contract
    But if they were to submit using Python, this would be a good way to do it
"""
from web3 import Web3
import json
import os
from eth_account import Account
from web3.middleware import geth_poa_middleware #Necessary for POA chains
import sys
import random
from hexbytes import HexBytes

def hashPair( a,b ):
    """
        The OpenZeppelin Merkle Tree Validator we use sorts the leaves
        https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/cryptography/MerkleProof.sol#L217
        So you must sort the leaves as well

        Also, hash functions like keccak are very sensitive to input encoding, so the solidity_keccak function is the function to use

        Another potential gotcha, if you have a prime number (as an int) bytes(prime) will *not* give you the byte representation of the integer prime
        Instead, you must call int.from_bytes(prime,'big').

        This function will hash leaves in a Merkle Tree in a way that is compatible with the way the on-chain validator hashes leaves
    """
    if a < b:
        return Web3.solidity_keccak( ['bytes32','bytes32'], [a,b] )
    else:
        return Web3.solidity_keccak( ['bytes32','bytes32'], [b,a] )

def connectTo(chain):
    if chain == 'avax':
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc" #AVAX C-chain testnet

    if chain == 'bsc':
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/" #BSC testnet

    if chain in ['avax','bsc']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the poa compatibility middleware to the innermost layer
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3


if __name__ == "__main__":
    chain = 'avax'

    with open( "contract_info.json", "r" ) as f:
        abi = json.load(f)

    address = "0xb728f421b33399Ae167Ff01Ad6AA8fEFace845F7"

    w3 = connectTo(chain)
    contract = w3.eth.contract( abi=abi, address=address )

    ###
    #YOUR CODE HERE
    ###
