
## Run
```
# Start the shell
nix-shell

# Start the application
flask run

```

## Test
```
python test.py
```

Output test:
```
[nix-shell:~/Documents/chain.co-labs/wallet-blockchain]$ python test.py 
Registered users with IDs: [1, 2, 3]

Added 100 to user 1: Transaction added to pending
Added 200 to user 2: Transaction added to pending
Added 300 to user 3: Transaction added to pending

Mining block to process add transactions...
Mined block 2 with transactions: [{'amount': 100, 'timestamp': '2025-03-11 23:01:53.704810', 'type': 'add', 'user_id': 1}, {'amount': 200, 'timestamp': '2025-03-11 23:01:53.706130', 'type': 'add', 'user_id': 2}, {'amount': 300, 'timestamp': '2025-03-11 23:01:53.707418', 'type': 'add', 'user_id': 3}]

Balances after adding funds:
User 1: 100
User 2: 200
User 3: 300

Withdrew 50 from user 1: Transaction added to pending
Withdrew 100 from user 2: Transaction added to pending
Withdrew 150 from user 3: Transaction added to pending

Mining block to process withdrawal transactions...
Mined block 3 with transactions: [{'amount': 50, 'timestamp': '2025-03-11 23:01:53.754478', 'type': 'withdraw', 'user_id': 1}, {'amount': 100, 'timestamp': '2025-03-11 23:01:53.755754', 'type': 'withdraw', 'user_id': 2}, {'amount': 150, 'timestamp': '2025-03-11 23:01:53.757082', 'type': 'withdraw', 'user_id': 3}]

Balances after withdrawals:
User 1: 50
User 2: 100
User 3: 150

Blockchain details:
Chain length: 3 blocks

Block 1:
Timestamp: 2025-03-11 23:00:45.990990
Transactions: 0 transactions
Previous Hash: 0
Hash: 915e2cc479ee676f1044a4a6d04939efd153cc97b2265792b6ac5cea7caf1fc1

Block 2:
Timestamp: 2025-03-11 23:01:53.748488
Transactions: 3 transactions
Previous Hash: 785958bc5653d51172c5682fb8c2fa43b57ae70b278605855aef8fde2eae6416
Hash: bdfddec1379b9021b00e5bb4805940b95e0b7c112177f6a4cbfe87989d1288cd

Block 3:
Timestamp: 2025-03-11 23:01:53.771416
Transactions: 3 transactions
Previous Hash: 7f7452be128c06b3d9380f19a9bcb5c38cc4717660ba965eb1231edcef9afa9b
Hash: 436e0546ddcb170c9e4461137ad63afa128d0dc41fc83d5ff1f85132ef76b5ca
```
