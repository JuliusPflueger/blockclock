def calculate_block_subsidy(block_height):
    halvings_count = block_height // 210000
    initial_subsidy = 50
    subsidy = initial_subsidy / (2 ** halvings_count)
    return subsidy

def get_halving_progress(block_height):
    last_halving = (block_height // 210000) * 210000
    blocks_until_halving = last_halving + 210000 - block_height
    progress = (block_height - last_halving) / 210000 * 100

    return progress, blocks_until_halving
