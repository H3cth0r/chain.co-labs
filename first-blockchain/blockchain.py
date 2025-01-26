import hashlib
import time
import json

class Block:
    def __init__(self, index, previous_hash, data, timestamp, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.data = data
        self.timestamp = timestamp
        self.nonce = nonce
        self.hash = self.calculate_hash()
    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "data": self.data,
            "timestamp": self.timestamp,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        print(block_string)
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty):
        while not self.hash.startswith('0' * difficulty):
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    def __init__(self):
        self.chain = []
        self.difficulty = 4
        self.balances = {
                'Alice': 1000,
                'Bob': 500,
        }
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, "0", "Genesis Block", time.time())
        genesis.mine_block(self.difficulty)
        self.chain.append(genesis)

    def add_block(self, transactions):
        if not self.validate_transactions(transactions):
            print("Invalid transactions - block rejected")
            return False

        last_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            previous_hash=last_block.hash,
            data=transactions,
            timestamp=time.time()
        )
        new_block.mine_block(self.difficulty)
        self.execute_transactions(transactions)
        self.chain.append(new_block)
        return True

    def validate_transactions(self, transactions):
        temp_balances = self.balances.copy()
        for tx in transactions:
            if tx['amount'] <= 0:
                return False
            if temp_balances.get(tx['sender'], 0) < tx['amount']:
                return False
            temp_balances[tx['sender']] -= tx['amount']
            temp_balances[tx['receiver']] = temp_balances.get(tx['receiver'], 0) + tx['amount']
        return True
    
    def execute_transactions(self, transactions):
        for tx in transactions:
            self.balances[tx['sender']] -= tx['amount']
            self.balances[tx['receiver']] = self.balances.get(tx['receiver'], 0) + tx['amount']

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]

            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def print_chain(self):
        for block in self.chain:
            print(f"\nBlock {block.index}:")
            print(f"Hash: {block.hash}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Nonce: {block.nonce}")
            print("Transactions:")
            if isinstance(block.data, list):
                for tx in block.data: print(f"  {tx['sender']} -> {tx['receiver']}: {tx['amount']}")
            else: print(f"  {block.data}")
            print("-" * 50)

if __name__ == "__main__":
    blockchain = Blockchain()

    print("Initial balances:")
    print("Alice: ", blockchain.balances["Alice"])
    print("Bob: ", blockchain.balances["Bob"])

    transactions1 = [
        {'sender': 'Alice', 'receiver': 'Bob', 'amount': 100},
        {'sender': 'Bob', 'receiver': 'Alice', 'amount': 50}
    ]

    print("\nAdding block 1...")
    blockchain.add_block(transactions1)
    print("Alice:", blockchain.balances['Alice'])
    print("Bob:", blockchain.balances['Bob'])

    transactions2 = [
        {'sender': 'Alice', 'receiver': 'Bob', 'amount': 2000}
    ]
    
    print("\nAttempting to add block 2...")
    blockchain.add_block(transactions2)
    print("Balances remain unchanged:")
    print("Alice:", blockchain.balances['Alice'])
    print("Bob:", blockchain.balances['Bob'])

    print("\nBlockchain valid?", blockchain.is_chain_valid())

    print("\nBlockchain structure:")
    blockchain.print_chain()
