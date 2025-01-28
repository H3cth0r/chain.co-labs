import hashlib
import json
import time
from datetime import datetime
from typing import Dict, Optional

class Block:
    def __init__(self, index: int, timestamp: str, data: dict, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
    
    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }

class Blockchain:
    def __init__(self):
        self.chain = []
        self.users = {}
        self.peers = set()

        self.load_chain()
        self.load_users()

        if not self.chain: self.create_genesis_block()

    # Old methods
    def create_genesis_block(self):
        genesis_block = Block(0, str(datetime.now()), {"username": "System", "message": "Genesis Block"}, "0")
        self.chain.append(genesis_block)
        self.save_chain()

    def add_block(self, data: dict):
        previous_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            timestamp=str(datetime.now()),
            data=data,
            previous_hash=previous_block.hash
        )
        if self.is_chain_valid():
            self.chain.append(new_block)
            self.save_chain()
        else: raise ValueError("Blockchain is invalid - cannot add new block")

    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash(): return False
            if current_block.previous_hash != previous_block.hash: return False
        return True

    def save_chain(self):
        chain_data = [block.to_dict() for block in self.chain]
        with open("blockchain.json", "w") as f: json.dump(chain_data, f)

    def load_chain(self):
        try:
            with open("blockchain.json", "r") as f:
                chain_data = json.load(f)
                self.chain = [
                    Block(
                        index=block['index'],
                        timestamp=block['timestamp'],
                        data=block['data'],
                        previous_hash=block['previous_hash']
                    ) for block in chain_data
                ]
        except FileNotFoundError: pass

    def save_users(self):
        with open("users.json", "w") as f:
            json.dump(self.users, f)

    def load_users(self):
        try:
            with open("users.json", "r") as f:
                self.users = json.load(f)
        except FileNotFoundError: pass

    def register_user(self, username: str, password: str):
        if username in self.users:
            raise ValueError("Username already exists")
        self.users[username] = hashlib.sha256(password.encode()).hexdigest()
        self.save_users()

    def authenticate_user(self, username: str, password: str) -> bool:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return self.users.get(username) == password_hash

    def get_chat_history(self) -> list: return [block.data for block in self.chain[1:]]  

    # New methods

    def register_peer(self, address: str): self.peers.add(address)

    def broadcast_block(self, block: Block):
        for peer in self.peers: requests.post(f"http://{peer}/add_block", json=block.to_dict())

    def resolve_conflicts(self) -> bool:
        longest_chain = None
        max_length = len(self.chain)

        for peer in self.peers:
            response = requests.get(f"http://{peer}/get_chain")
            if response.status_code == 200:
                peer_chain =  response.json()
                if len(peer_chain) > max_length and self.validate_peer_chain(peer_chain):
                    max_length = len(peer_chain)
                    longest_chain = peer_chain
        if longest_chain:
            self.chain = [Block(**block) for block in longest_chain]
            self.save_chain()
            return True
        return False

    def validate_peer_chain(self, peer_chain: list) -> bool:
        temp_chain = []
        for block_data in peer_chain:
            block = Block(
                    index=block_data['index'],
                    timestamp=block_data['timestamp'],
                    data=block_data['data'],
                    previous_hash=block_data['previous_hash'],
            )
            if block.hash != block_data['hash']: return False
            temp_chain.append(block)
        for i in range(1, len(temp_chain)):
            if temp_chain[i].previous_hash != temp_chain[i-1].hash: return False

        return True
