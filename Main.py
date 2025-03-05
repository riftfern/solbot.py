from MarketManager import MarketManager
from SolanaRpcApi import SolanaRpcApi
import asyncio
from aioconsole import ainput

async def main():
    http_uri = "https://mainnet.helius-rpc.com/?api-key=5ed3094b-47d3-4a2a-8e97-bc6c0ac41a5f"
    wss_uri = "wss://mainnet.helius-rpc.com/?api-key=5ed3094b-47d3-4a2a-8e97-bc6c0ac41a5f"

    try:
        solana_rpc_api = SolanaRpcApi(http_uri, wss_uri)
        market_manager = MarketManager(solana_rpc_api)

        user_input = await ainput("Enter a token address to monitor: ")
        print(f"Starting monitoring for: {user_input}")

        await market_manager.monitor_token(user_input)
        await market_manager.ray_pool_monitor.start()
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        print("Monitoring stopped.")

if __name__ == "__main__":
    asyncio.run(main())