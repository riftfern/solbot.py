import TokensApi
from pubsub import pub
from SolanaRpcApi import SolanaRpcApi
import Globals as globals
import websockets
import json
import asyncio
from datetime import datetime

class RaydiumTokensMonitor:
    def __init__(self, solana_rpc_api: SolanaRpcApi):
        self.token_infos = {}
        self.updated_tokens = set()
        self.solana_rpc_api = solana_rpc_api
        self.wsocket = None

    def get_token_info(self, token_address):
        if token_address in self.token_infos:
            if token_address in self.updated_tokens:
                self._update_price(token_address)
                self.updated_tokens.remove(token_address)
            return self.token_infos[token_address]
        return None

    async def monitor_token(self, token_address: str):
        if token_address not in self.token_infos:
            token_info = TokensApi.get_amm_token_pool_data(token_address)
            if token_info:
                self.token_infos[token_address] = token_info
                pub.sendMessage(globals.topic_token_update_event, arg1=token_address)
            else:
                print(f"Error: Failed to fetch token info for {token_address}")
                return
        if self.wsocket:
            token_info = self.token_infos[token_address]
            request = self.solana_rpc_api.get_account_subscribe_request(
                token_info.token_vault_address, self.solana_rpc_api.next_id()
            )
            await self.wsocket.send(json.dumps(request))

    async def start(self):
        await self._read_socket()

    def _update_price(self, token_address: str):
        if token_address in self.token_infos:
            sol_vault_address = self.token_infos[token_address].sol_vault_address
            sol_balance = self.solana_rpc_api.get_account_balance(sol_vault_address)
            token_info = self.token_infos[token_address]
            if sol_balance and token_info.token_vault_ui_amount > 0:
                sol_balance /= 1e9  # Convert lamports to SOL
                token_info.price = sol_balance / token_info.token_vault_ui_amount

    async def _read_socket(self):
        while True:
            try:
                async with websockets.connect(self.solana_rpc_api.wss_uri) as websocket:
                    self.wsocket = websocket
                    for token_address in self.token_infos.keys():
                        await self.monitor_token(token_address)
                    while True:
                        received = await websocket.recv()
                        jsonData = json.loads(received)
                        self._process(jsonData)
            except Exception as e:
                print(f"WebSocket error: {str(e)}")
                await asyncio.sleep(5)

    def _process(self, data: dict):
        params = data.get('params', None)
        if params:
            parsed_info = params['result']['value']['data']['parsed']['info']
            token_address = parsed_info['mint']
            token_ui_amount = parsed_info['tokenAmount']['uiAmount']
            if token_address in self.token_infos:
                token_info = self.token_infos[token_address]
                token_info.token_vault_ui_amount = token_ui_amount
                self.updated_tokens.add(token_address)
                pub.sendMessage(globals.topic_token_update_event, arg1=token_address)