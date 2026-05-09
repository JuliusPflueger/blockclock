from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Union

import utils
import client.mempool_client as mempool_client
import client.blockstream_client as blockstream_client


@dataclass(frozen=True)
class Snapshot:
    block_height: int
    block_details: dict
    difficulty_information: dict
    mining_data: dict
    tx_count_in_mempool: Union[int, str]
    total_fees_in_mempool: Union[int, float, str]
    halving_progress: float
    blocks_until_halving: int
    total_fees_btc: float
    total_fees_usd: float

    def details(self) -> List[Tuple[str, str]]:
        return [
            ("Difficulty",      f"Difficulty: {self.block_details.get('difficulty', 0) / 1e12:.2f} T"),
            ("Halving",         f"Halving: {self.halving_progress:.2f}% ({self.blocks_until_halving})"),
            ("Next Adjustment", f"Next Adj.: {self.difficulty_information.get('progressPercent', 0):.2f}% ({self.difficulty_information.get('remainingBlocks', 0)})"),
            ("Tx Count",        f"Tx's: {self.block_details.get('tx_count', 'N/A')}"),
            ("Txs (Mempool)",   f"Tx's(MP): {self.tx_count_in_mempool}"),
            ("Block Fees",      f"Fees: {self.total_fees_btc:.4f} BTC (${self.total_fees_usd:.2f})"),
            ("Mempool Fees",    f"Total Fees(MP): {float(self.total_fees_in_mempool) / 1e8:.4f} BTC" if self.total_fees_in_mempool not in ("N/A", None) else "Total Fees(MP): N/A"),
            ("Hashrate",        f"Hashrate: {self.mining_data.get('currentHashrate', 0) / 1e18:.2f} EH/s"),
        ]

    def visible_detail_texts(self, enabled_names: List[str]) -> List[str]:
        return [text for name, text in self.details() if name in enabled_names]


class DataUpdater:
    def fetch(self) -> Snapshot:
        block_height = mempool_client.get_block_height()
        halving_progress, blocks_until_halving = utils.get_halving_progress(block_height)

        block_hash = blockstream_client.get_block_hash(block_height)
        block_details = blockstream_client.get_block_details(block_hash)

        difficulty_information = mempool_client.get_difficulty_information()
        mining_data = mempool_client.get_mining_data()
        mempool_details = mempool_client.get_mempool_details()

        tx_count_in_mempool = mempool_details.get("count", "N/A")
        total_fees_in_mempool = mempool_details.get("total_fee", "N/A")

        transactions = mempool_client.get_transactions(block_hash)
        coinbase_tx = transactions[0]
        total_block_reward = sum(output["value"] for output in coinbase_tx["vout"]) / 1e8

        block_subsidy = utils.calculate_block_subsidy(block_height)
        total_fees_btc = total_block_reward - block_subsidy
        total_fees_usd = mempool_client.get_price().get("USD") * total_fees_btc

        return Snapshot(
            block_height=block_height,
            block_details=block_details,
            difficulty_information=difficulty_information,
            mining_data=mining_data,
            tx_count_in_mempool=tx_count_in_mempool,
            total_fees_in_mempool=total_fees_in_mempool,
            halving_progress=halving_progress,
            blocks_until_halving=blocks_until_halving,
            total_fees_btc=total_fees_btc,
            total_fees_usd=total_fees_usd,
        )
