import requests
import time

# Base URL of the Flask app
BASE_URL = 'http://127.0.0.1:5000'

def simulate_transactions():
    # Register three users
    user_ids = []
    for _ in range(3):
        response = requests.post(f'{BASE_URL}/users')
        user_id = response.json()['user_id']
        user_ids.append(user_id)
    print(f"Registered users with IDs: {user_ids}\n")

    # Add funds for each user
    add_amounts = [100, 200, 300]
    for user_id, amount in zip(user_ids, add_amounts):
        data = {'user_id': user_id, 'amount': amount}
        response = requests.post(f'{BASE_URL}/transactions/add', json=data)
        print(f"Added {amount} to user {user_id}: {response.json()['message']}")

    # Mine a block to process the add transactions
    print("\nMining block to process add transactions...")
    response = requests.post(f'{BASE_URL}/mine')
    mined_block = response.json()
    print(f"Mined block {mined_block['index']} with transactions: {mined_block['transactions']}\n")

    # Check balances after adding funds
    print("Balances after adding funds:")
    for user_id in user_ids:
        response = requests.get(f'{BASE_URL}/users/{user_id}/balance')
        balance = response.json()['balance']
        print(f"User {user_id}: {balance}")
    print()

    # Withdraw funds for each user
    withdraw_amounts = [50, 100, 150]
    for user_id, amount in zip(user_ids, withdraw_amounts):
        data = {'user_id': user_id, 'amount': amount}
        response = requests.post(f'{BASE_URL}/transactions/withdraw', json=data)
        print(f"Withdrew {amount} from user {user_id}: {response.json()['message']}")

    # Mine another block to process withdrawals
    print("\nMining block to process withdrawal transactions...")
    response = requests.post(f'{BASE_URL}/mine')
    mined_block = response.json()
    print(f"Mined block {mined_block['index']} with transactions: {mined_block['transactions']}\n")

    # Check balances after withdrawals
    print("Balances after withdrawals:")
    for user_id in user_ids:
        response = requests.get(f'{BASE_URL}/users/{user_id}/balance')
        balance = response.json()['balance']
        print(f"User {user_id}: {balance}")
    print()

    # Retrieve and print the blockchain details
    response = requests.get(f'{BASE_URL}/chain')
    chain = response.json()['chain']
    print("Blockchain details:")
    print(f"Chain length: {len(chain)} blocks")
    for block in chain:
        print(f"\nBlock {block['index']}:")
        print(f"Timestamp: {block['timestamp']}")
        print(f"Transactions: {len(block['transactions'])} transactions")
        print(f"Previous Hash: {block['previous_hash']}")
        print(f"Hash: {block['hash']}")

if __name__ == '__main__':
    simulate_transactions()
