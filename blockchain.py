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

    def proof_of_work(self, last_proof):
        """
        Very simple PoW algorithm:
        - find number p' such that hash(pp') contains leading 4 zeroes, where p is
        - p is the previous proof, and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof
    
    @staticmethod
    def valid_proof(last_proof, proof):
        """
        validates the proof: does hash(last_proof, proof) contain 4 leading zeros?
        :param last_proof: <int> previous proof
        :param proof: <int> current proof
        :return: <bool> true if correct, false if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

# todo: setup python flask
# /transactions/new -> creates new transaction to a block
    
# instantiate new node    
app = Flask(__name__)
# generate globally unique address for the node
node_identifier = str(uuid4()).replace('-', '')

# instantiate blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # reward for finding proof
    # sender is "0" to signify that this node has mined a new coin
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # forge new block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # check that required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400
    
    # create a new transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# /mine             -> tells server to mine a new block
# /chain            -> returns full Blockchain