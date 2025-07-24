import requests

def get_block_height():
    return requests.get("https://mempool.space/api/blocks/tip/height").json()

def get_difficulty_information():
    return requests.get("https://mempool.space/api/v1/difficulty-adjustment").json()

def get_mining_data():
    return requests.get("https://mempool.space/api/v1/mining/hashrate/1m").json()

def get_mempool_details():
    return requests.get(f"https://mempool.space/api/mempool").json()

def get_transactions(block_hash):
    return requests.get(f"https://mempool.space/api/block/{block_hash}/txs").json()

def get_price():
    return requests.get(f"https://mempool.space/api/v1/prices").json()
