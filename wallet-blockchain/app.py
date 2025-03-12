import hashlib
import json
from datetime import datetime
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.balances = {}
        self.nodes = set()
        self.create_block(proof=1, previous_hash='0')  # Genesis block

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.now()),
            'transactions': self.pending_transactions,
            'proof': proof,
            'previous_hash': previous_hash,
        }
        block['hash'] = self.hash(block)
        self.pending_transactions = []
        self.chain.append(block)
        self.process_transactions(block['transactions'])
        return block

    def process_transactions(self, transactions):
        for tx in transactions:
            user_id = tx['user_id']
            amount = tx['amount']
            if tx['type'] == 'add':
                self.balances[user_id] = self.balances.get(user_id, 0) + amount
            elif tx['type'] == 'withdraw':
                self.balances[user_id] = self.balances.get(user_id, 0) - amount

    def add_transaction(self, user_id, amount, tx_type):
        self.pending_transactions.append({
            'user_id': user_id,
            'amount': amount,
            'type': tx_type,
            'timestamp': str(datetime.now())
        })

    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash.startswith('0000')

    def valid_chain(self, chain):
        previous_block = chain[0]
        for block in chain[1:]:
            if block['previous_hash'] != self.hash(previous_block):
                return False
            if not self.valid_proof(previous_block['proof'], block['proof']):
                return False
            previous_block = block
        return True

    def resolve_conflicts(self):
        longest_chain = None
        max_length = len(self.chain)
        for node in self.nodes:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain:
            self.chain = longest_chain
            self.balances = {}
            for block in self.chain:
                self.process_transactions(block['transactions'])
            return True
        return False

blockchain = Blockchain()
users = {}
current_user_id = 0



# ====================================
# ====================================


@app.route('/users', methods=['POST'])
def register_user():
    global current_user_id
    current_user_id += 1
    user_id = current_user_id
    users[user_id] = {'id': user_id}
    return jsonify({'user_id': user_id}), 201

@app.route('/users/list', methods=['POST'])
def print_users():
    print("Hi")
    return jsonify({'users': users}), 200

@app.route('/transactions/add', methods=['POST'])
def add_funds():
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount')
    if user_id not in users or amount <= 0:
        return jsonify({'message': 'Invalid user or amount'}), 400
    blockchain.add_transaction(user_id, amount, 'add')
    return jsonify({'message': 'Transaction added to pending'}), 201

@app.route('/transactions/withdraw', methods=['POST'])
def withdraw_funds():
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount')
    if user_id not in users or amount <= 0:
        return jsonify({'message': 'Invalid user or amount'}), 400

    confirmed_balance = blockchain.balances.get(user_id, 0)
    pending_adds = sum(tx['amount'] for tx in blockchain.pending_transactions 
                      if tx['user_id'] == user_id and tx['type'] == 'add')
    pending_withdrawals = sum(tx['amount'] for tx in blockchain.pending_transactions 
                            if tx['user_id'] == user_id and tx['type'] == 'withdraw')
    available_balance = confirmed_balance + pending_adds - pending_withdrawals

    if available_balance < amount:
        return jsonify({'message': 'Insufficient funds'}), 400

    blockchain.add_transaction(user_id, amount, 'withdraw')
    return jsonify({'message': 'Transaction added to pending'}), 201

@app.route('/mine', methods=['POST'])
def mine_block():
    last_block = blockchain.chain[-1]
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    previous_hash = blockchain.hash(last_block)
    block = blockchain.create_block(proof, previous_hash)
    return jsonify({
        'message': 'New block mined',
        'index': block['index'],
        'transactions': block['transactions'],
        'previous_hash': block['previous_hash']
    }), 200

@app.route('/users/<int:user_id>/balance', methods=['GET'])
def get_balance(user_id):
    if user_id not in users:
        return jsonify({'message': 'User not found'}), 404
    balance = blockchain.balances.get(user_id, 0)
    return jsonify({'user_id': user_id, 'balance': balance}), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify({
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }), 200

@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    data = request.get_json()
    nodes = data.get('nodes', [])
    if not nodes:
        return jsonify({'message': 'Please provide a list of nodes'}), 400
    for node in nodes:
        blockchain.nodes.add(node)
    return jsonify({
        'message': 'Nodes added',
        'total_nodes': list(blockchain.nodes)
    }), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {'message': 'Chain replaced', 'new_chain': blockchain.chain}
    else:
        response = {'message': 'Chain authoritative', 'chain': blockchain.chain}
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
