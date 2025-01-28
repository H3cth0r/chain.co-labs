from flask import Flask, request, jsonify
import requests

from chatblockchain import Blockchain, Block

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/add_block', methods=['POST'])
def add_block():
    block_data = request.get_json()
    new_block = Block(
        index=block_data['index'],
        timestamp=block_data['timestamp'],
        data=block_data['data'],
        previous_hash=block_data['previous_hash']
    )
    
    if blockchain.is_chain_valid() and new_block.previous_hash == blockchain.chain[-1].hash:
        blockchain.chain.append(new_block)
        blockchain.save_chain()
        blockchain.broadcast_block(new_block)
        return "Block added", 200
    return "Invalid block", 400

@app.route('/get_chain', methods=['GET'])
def get_chain():
    return jsonify([block.to_dict() for block in blockchain.chain]), 200

@app.route('/register_peer', methods=['POST'])
def register_peer():
    peer_address = request.json.get('address')
    if not peer_address:
        return "Invalid address", 400
    
    blockchain.register_peer(peer_address)
    return "Peer registered", 200

@app.route('/register_node', methods=['POST'])
def register_node():
    new_node_address = request.json.get('address')
    if not new_node_address:
        return "Invalid address", 400

    # Register with existing network
    for peer in blockchain.peers:
        try:
            requests.post(f"http://{peer}/register_peer", json={'address': new_node_address})
        except requests.exceptions.RequestException:
            continue

    blockchain.register_peer(new_node_address)
    return "Node registered with network", 200

@app.route('/sync_chain', methods=['GET'])
def sync_chain():
    replaced = blockchain.resolve_conflicts()
    return jsonify({'message': 'Chain replaced' if replaced else 'Chain is authoritative'}), 200



if __name__ == '__main__':
    from argparse import ArgumentParser
    
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int)
    parser.add_argument('-n', '--nodes', nargs='*', help="Bootstrap nodes")
    args = parser.parse_args()

    port = args.port
    nodes = args.nodes or []

    # Register with existing network
    for node in nodes:
        try:
            requests.post(f"http://{node}/register_node", json={'address': f'localhost:{port}'})
        except requests.exceptions.RequestException:
            continue

    app.run(host='0.0.0.0', port=port)
