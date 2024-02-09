from eth_account.messages import encode_defunct
from web3 import Web3
import eth_account
import os

def sign_challenge(challenge):
    """
        Takes a challenge (string)
        Returns addr, sig
        where addr is an ethereum address (in hex)
        and sig is a signature (in hex)
    """

    ####
    #YOUR CODE HERE
    ####
    private_key = "46e2623ed463a8523bbc9aea7c1e732fe9768ae9d1c4b5026fc7196252055a42"
    wallet_address = "0x99ECb0aBBa20B98Cf096496841241ed5e8a90883"

    w3 = Web3()
    w3.eth.default_account = wallet_address
    wallet_account = w3.eth.account.from_key(private_key)
    addr = wallet_account.address

    #msg = eth_account.messages.encode_defunct(challenge)
    sig = eth_account.Account.sign_message(encode_defunct(text=challenge), private_key=private_key)

    #return sig, acct #acct contains the private key
    return addr, sig.signature.hex()


if __name__ == "__main__":
    """
        This may help you test the signing functionality of your code
    """
    import random 
    import string

    letters = string.ascii_letters
    challenge = ''.join(random.choice(string.ascii_letters) for i in range(32)) 

    addr, sig = sign_challenge(challenge)

    eth_encoded_msg = eth_account.messages.encode_defunct(text=challenge)

    if eth_account.Account.recover_message(eth_encoded_msg,signature=sig) == addr:
        print( f"Success: signed the challenge {challenge} using address {addr}!")
    else:
        print( f"Failure: The signature does not verify!" )
        print( f"signature = {sig}" )
        print( f"address = {addr}" )
        print( f"challenge = {challenge}" )

