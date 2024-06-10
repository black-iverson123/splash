import requests


def get_latest_prices(CMC_API_KEY, limit=None, convert='USD'):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        
    params = {
            'start': 1,
            'limit': limit,
            'convert': convert
        }
        
    headers = {
            'X-CMC_PRO_API_KEY': CMC_API_KEY
        }
        
    try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            coins_data = data['data']
            
            coins = []
            
            
            for coin in coins_data:
                coins.append(                {
                    'name': coin['name'],
                    'symbol': coin['symbol'],
                    'price': round(float(coin['quote'][convert]['price']), 2),
                    'circulating_supply': round(float(coin['circulating_supply'])),
                    '24h_volume': round(float(coin['quote'][convert]['volume_24h'])),
                    'volume_change_in_24h': float(coin['quote'][convert]['volume_change_24h']),
                    'percent_change_in_1h': round(float(coin['quote'][convert]['percent_change_1h']), 2),
                    'percent_change_in_24h': round(float(coin['quote'][convert]['percent_change_24h']), 2),
                    'percent_change_in_7d': round(float(coin['quote'][convert]['percent_change_7d']), 2)
                })
                
            
           
            return coins
        
            
    except requests.exceptions.RequestException as e:
            return {'error': 'Failed to fetch data'}
