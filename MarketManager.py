import TokensApi
from SolanaRpcApi import SolanaRpcApi
from RaydiumTokensMonitor import RaydiumTokensMonitor
from pubsub import pub
import Globals as globals
from datetime import datetime

#ANSI color codes 
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

class MarketManager:
    def __init__(self, solana_rpc_api: SolanaRpcApi):
        self.ray_pool_monitor = RaydiumTokensMonitor(solana_rpc_api)
        self.last_prices = {} #store last updated price 
        topic = globals.topic_token_update_event
        listener = self._handle_token_update
        pub.subscribe(listener, topic)

    def get_price(self, token_address: str):
        token_info = self.ray_pool_monitor.get_token_info(token_address)
        return token_info.price if token_info else 0

    async def monitor_token(self, token_address: str):
        try:
            await self.ray_pool_monitor.monitor_token(token_address)
        except Exception as e:
            print(f"Error monitoring {token_address}: {str(e)}")

    def _handle_token_update(self, arg1: str):
        try:
            price = self.get_price(arg1)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            short_addr = f"{arg1[:6]}...{arg1[-6]}"
            color = ""
            change_string = ""
            if arg1 in self.last_prices:
                change = (price - self.last_prices[arg1]) / self.last_prices[arg1] * 100
                change_string = f"{change:+.2f}%"
                color = GREEN if price > self.last_prices[arg1] else RED if price < self.last_prices[arg1] else ""
            self.last_prices[arg1] = price
            output = f"{timestamp} | {short_addr} | Price: {price:.8f} {change_string}"
            print(f"{color}{output}{RESET}" if color else output)
        except Exception as e:
            print(f"Error updating {arg1}: {str(e)}") 