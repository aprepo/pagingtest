from app.aiven import cache, headers
from app.settings import BASEURL


def get_accounts(token):
    session = cache.get_private_session(token)
    response = session.get('https://api.aiven.io/v1/account', headers=headers.get_headers(token))
    accounts = []
    for account in response.json().get('accounts', []):
        account['url'] = f"{BASEURL}/accounts/{account.get('account_id', None)}/"
        accounts.append(account)
    return accounts, response.from_cache


def get_account(token, account_id):
    session = cache.get_private_session(token)
    response = session.get('https://api.aiven.io/v1/account/{account_id}', headers=headers.get_headers(token))
    return response.json(), response.from_cache
