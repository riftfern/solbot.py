from jsonrpcclient import request as jsonrpc_request, parse, Ok, Error
import requests

class SolanaRpcApi:
    def __init__(self, rpc_uri, wss_uri):
        self.rpc_uri = rpc_uri
        self.wss_uri = wss_uri
        self.subscription_id = 0

    def run_rpc_method(self, request_name: str, params):
        json_request = jsonrpc_request(request_name, params=params)
        response = requests.post(self.rpc_uri, json=json_request)
        parsed = parse(response.json())
        if isinstance(parsed, Error):
            return None
        return parsed.result

    def get_account_balance(self, account_address: str) -> float:
        response = self.run_rpc_method("getBalance", [account_address])
        return response['value'] if response else None

    @staticmethod
    def get_account_subscribe_request(account_address: str, sub_id: int):
        return {
            "jsonrpc": "2.0",
            "id": sub_id,
            "method": "accountSubscribe",
            "params": [account_address, {"encoding": "jsonParsed", "commitment": "finalized"}]
        }

    def next_id(self):
        self.subscription_id += 1
        return self.subscription_id