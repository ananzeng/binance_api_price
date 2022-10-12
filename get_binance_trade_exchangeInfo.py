import requests

def create_symbols_list(filter='USDT'):
    base_url = 'https://api.binance.com/api/v3/exchangeInfo'
    info = requests.get(base_url).json()
    pairs_data = info['symbols']
    full_data_dic = {s['symbol']: s for s in pairs_data if filter in s['symbol']}
    return full_data_dic.keys()
def write_txt():
    all_trade_exchange_info = create_symbols_list('USDT')
    path = 'output.txt'
    with open(path, 'w') as f:
        for i in all_trade_exchange_info:
            if i[-4:] == "USDT":
                f.write(i)
                f.write('\n')
