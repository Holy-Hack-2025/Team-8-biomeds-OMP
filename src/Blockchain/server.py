from flask import Flask, jsonify, request
import hashlib
import time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

app = Flask(__name__)


class Block:
    def __init__(self, index, prev_hash, data, owner, read_access, write_access):
        self.index = index
        self.prev_hash = prev_hash
        self.timestamp = time.time()
        self.data = data
        self.owner = owner  # Store public key string
        self.read_access = read_access
        self.write_access = write_access
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_str = f"{self.index}{self.prev_hash}{self.timestamp}{self.data}{self.owner}"
        return hashlib.sha256(block_str.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        # Pre-configured genesis block with initial permissions
        return Block(0, "0", "GENESIS", "system",
                     ["alice_pubkey", "bob_pubkey"],  # Initial read access
                     ["alice_pubkey"])  # Initial write access

    def add_block(self, new_block):
        # Simple validation (expand this in real implementation)
        self.chain.append(new_block)
        return new_block


blockchain = Blockchain()


@app.route('/chain', methods=['GET'])
def get_chain():
    public_key = request.args.get('public_key')
    filtered_chain = []

    for block in blockchain.chain:
        if public_key in block.read_access:
            filtered_chain.append({
                'index': block.index,
                'data': block.data,
                'owner': block.owner,
                'timestamp': block.timestamp
            })
    return jsonify(filtered_chain)


@app.route('/add', methods=['POST'])
def add_block():
    data = request.json
    last_block = blockchain.chain[-1]

    # Convert string back to public key
    try:
        public_key = serialization.load_pem_public_key(
            data['public_key'].encode()
        )
    except:
        return jsonify({"error": "Invalid public key"}), 400

    # Verify write permission
    if data['public_key'] not in last_block.write_access:
        return jsonify({"error": "Write permission denied"}), 403

    # Create new block
    new_block = Block(
        index=len(blockchain.chain),
        prev_hash=last_block.hash,
        data=data['data'],
        owner=data['public_key'],
        read_access=data.get('read_access', [data['public_key']]),
        write_access=data.get('write_access', [data['public_key']])
    )

    blockchain.add_block(new_block)
    return jsonify({
        "status": "Block added",
        "index": new_block.index,
        "hash": new_block.hash
    }), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)