import hashlib
import json
from time import time

class Blockchain(object):
    def __init__(self):        
        self.current_transactions = []
        self.chain = []
        # create genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self):
        """
        creates new block in the blockchain

        :param proof: <int> proof given by the Proof of Work algorithm
        :param previous_hash: (optional) <str> Hash of previous Block
        :return: <dict> new Block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        # reset current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block
    
    def new_transaction(self):
        """
        adds a transaction to the list and returns the index
        of the block which the transaction will be added to, which is the next one to be mined

        :param sender: <str> Address of sender
        :param recipient: <str> Address of recipient
        :param amount: <int>
        :return: <int> Index of Block that will hold the transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]
    
    @staticmethod
    def hash(block):
        """
        creates a SHA-256 hash of a Block
        :param block: <dict> Block
        :return: <str>
        """
        # orders dictionary to avoid inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    