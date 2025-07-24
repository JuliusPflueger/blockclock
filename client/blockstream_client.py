import requests

def get_block_hash(block_height):
    return requests.get(f"https://blockstream.info/api/block-height/{block_height}").text.strip()

def get_block_details(block_hash: str):
    return requests.get(f"https://blockstream.info/api/block/{block_hash}").json()
