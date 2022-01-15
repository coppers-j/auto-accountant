from dataclasses import dataclass
import requests
import pprint
import json
from datetime import datetime, date

api_key = open("access.conf", "r").read().strip()
HEADER = {"Authorization": f"Bearer {api_key}"}
BASE_URL = "https://api.up.com.au/api/v1/" 

@dataclass
class Transaction:
    """CLass for storing transaction object"""
    id: str
    timestamp: object
    upCategory: str
    upParentCategory: str
    value: int # in 'base units' i.e. AUD cents
    rawText: str
    message: str
    description: str
    account: str

    def get_value(self) -> float:
        return self.value/100


def get_txs(url, until=None):
    response = requests.get(url, headers=HEADER) 
    body = json.loads(response.text)
    next_url = body['links']['next']
    txs = []
    for item in body['data']:
        attributes = item['attributes']
        category = item['relationships']['category']['data']
        parentCategory = item['relationships']['parentCategory']['data']
        account = item['relationships']['account']['data']['id']
        timestamp = datetime.fromisoformat(attributes['createdAt'])
        if (until is not None) and (timestamp < until):
            return txs 
        if category is not None:
            category = category['id']
            parentCategory = parentCategory['id']
        tx = Transaction(
                id=item['id'],
                timestamp = timestamp,
                upCategory=category,
                upParentCategory=parentCategory,
                value=attributes['amount']['valueInBaseUnits'],
                rawText=attributes['rawText'],
                message=attributes['message'],
                description=attributes['description'],
                account=account)
        txs.append(tx)
    if next_url is not None:
        txs.extend(get_txs(next_url, until))
    return txs


txs = get_txs(f"{BASE_URL}transactions", until=datetime.fromisoformat('2021-12-30T00:00:00.000+11:00'))
_ = [print(tx) for tx in txs]
