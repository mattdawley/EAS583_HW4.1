"""
    We are agnostic about how the students submit their merkle proofs to the on-chain contract
    But if they were to submit using Python, this would be a good way to do it
"""
from web3 import Web3
import json
import os
from eth_account import Account
from web3.middleware import geth_poa_middleware, \
    construct_sign_and_send_raw_middleware  # Necessary for POA chains
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


def generate_primes(n):
    primes = []
    num = 2
    while len(primes) < n:
        for p in primes:
            if num % p == 0:
                break
        else:
            primes.append(num)
        num += 1
    return primes

def build_merkle_tree(leaves):
    tree = []

    leave_level = []
    for l in generate_primes(leaves):
        leave_level.append(l.to_bytes(32, 'big'))
    tree.append(leave_level)

    while len(tree[-1]) > 1:
        level = []
        for i in range(0, len(tree[-1]), 2):
            combined_hash = hashPair(tree[-1][i],  tree[-1][i + 1])
            level.append(combined_hash)
        tree.append(level)

    return tree

def find_sibling_node_index(tree_level, value):
    for node in range(len(tree_level)):
        if tree_level[node] == value:
            if node % 2 == 0:
                return node + 1
            else:
                return node - 1

def build_proof(tree, leaf):
    sibling_index = find_sibling_node_index(tree[0], leaf)
    proof = [tree[0][sibling_index]]

    for level in range (1, len(tree)-1):

        # Find Parent
        parent = sibling_index // 2

        # Find Sibling of Parent
        sibling_index = find_sibling_node_index(tree[level], tree[level][parent])

        # Add Sibling of Parent to Proof List
        proof.append(tree[level][sibling_index])

    return proof

if __name__ == "__main__":
    chain = 'avax'

    with open( "validator.abi", "r" ) as f:
        abi = json.load(f)

    address = "0xb728f421b33399Ae167Ff01Ad6AA8fEFace845F7"

    w3 = connectTo(chain)
    contract = w3.eth.contract( abi=abi, address=address )

    #YOUR CODE HERE
    private_key = "46e2623ed463a8523bbc9aea7c1e732fe9768ae9d1c4b5026fc7196252055a42"
    wallet_address = "0x99ECb0aBBa20B98Cf096496841241ed5e8a90883"

    wallet_account = w3.eth.account.from_key(private_key)
    w3.middleware_onion.add(
        construct_sign_and_send_raw_middleware(wallet_account))
    w3.eth.default_account = wallet_address

    leaves = 8192
    prime_list = generate_primes(leaves)
    merkle_tree = build_merkle_tree(leaves)
    leaf = merkle_tree[0][5197]
    # print("Prime", prime_list[5197], "owned by ",contract.functions.getOwnerByPrime(prime_list[5197]))
    merkle_proof = build_proof(merkle_tree, leaf)

    try:
        output = contract.functions.submit(merkle_proof, leaf).transact()
        print(output)
        print("Proof successfully submitted")
    except Exception as e:
        print(f"Claim not successful: {str(e)}")

