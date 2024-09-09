
import datetime
import time
import pandas as pd
from fyers_apiv3 import fyersModel
import mibian

# Fyers API authentication
client_id = "your_client_id"
secret_key = "your_secret_key"
redirect_uri = "your_redirect_uri"
response_type = "code"
grant_type = "authorization_code"

session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type=response_type,
    grant_type = "authorization_code"  
)
fyers = fyersModel.FyersModel(client_id=client_id, 
                              token="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE3MjU4ODU4OTEsImV4cCI6MTcyNTkyODI1MSwibmJmIjoxNzI1ODg1ODkxLCJhdWQiOlsieDowIiwieDoxIiwiZDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCbTN1M0RMdG8zXzl5Q3Ftc3duWVVvb3FDZ3JyUTFnQUV2bkI1NEtDNlpjYzZRSWdHR1BwdmFSbUtjYWlsSUFIYTJoYm5BWjFIMkxWY0pkNWNjLVVDVEgyTU8wVkdqcUJ5NTRmQVJoYjJMVmJuYkFpUT0iLCJkaXNwbGF5X25hbWUiOiJQUkFTQU5OQSBCSVNFTiIsIm9tcyI6IksxIiwiaHNtX2tleSI6IjFlZWM4NmNhNmI2ZTIxMWVkYmE2ZTFjNDViYjIyMzE2MzQ0MTM3MjgxZTg0Mzc1MWYyYjVjYzVjIiwiZnlfaWQiOiJYUDMzNjU5IiwiYXBwVHlwZSI6MTAwLCJwb2FfZmxhZyI6Ik4ifQ.WBrXx-eaTHGUzNm8Z_Og7Q7Qj20efuDvLp6IyWcyTuk", 
                              log_path="/path/to/logs")

def get_current_nifty_price():
    nifty_data = fyers.quotes({"symbols": "NSE:NIFTY50-INDEX"})
    return nifty_data['d'][0]['v']['lp']

def get_option_chain(expiry_date):
    nifty_price = get_current_nifty_price()
    atm_strike = round(nifty_price / 50) * 50
    strike_prices = [atm_strike - 250, atm_strike - 200, atm_strike - 150, atm_strike - 100, atm_strike - 50, atm_strike]
    
    options_data = []
    for strike in strike_prices:
        for option_type in ['CE', 'PE']:
            symbol = f"NSE:NIFTY{expiry_date.strftime('%y%m%d')}{strike}{option_type}"
            try:
                data = fyers.quotes({"symbols": symbol})
                last_price = data['d'][0]['v']['lp']
                options_data.append({
                    'symbol': symbol,
                    'strike': strike,
                    'type': option_type,
                    'price': last_price,
                    'expiry': expiry_date
                })
            except Exception as e:
                print(f"Failed to fetch data for {symbol}: {str(e)}")
    return pd.DataFrame(options_data)

def calculate_greeks(option_data, spot, interest_rate=0):
    for i, row in option_data.iterrows():
        days_to_expiry = (row['expiry'] - datetime.datetime.now()).days
        if row['type'] == 'CE':
            c = mibian.BS([spot, row['strike'], interest_rate, days_to_expiry], callPrice=row['price'])
            option_data.loc[i, 'Delta'] = c.callDelta
            option_data.loc[i, 'Vega'] = c.vega
            option_data.loc[i, 'Theta'] = c.callTheta
        elif row['type'] == 'PE':
            p = mibian.BS([spot, row['strike'], interest_rate, days_to_expiry], putPrice=row['price'])
            option_data.loc[i, 'Delta'] = p.putDelta
            option_data.loc[i, 'Vega'] = p.vega
            option_data.loc[i, 'Theta'] = p.putTheta
    return option_data

def track_greeks_and_deltas():
    expiry_dates = [datetime.datetime.now() + datetime.timedelta(weeks=i) for i in range(3)]
    market_open_data = pd.DataFrame()
    
    # Fetch market open data
    for expiry in expiry_dates:
        option_chain = get_option_chain(expiry)
        market_open_data = pd.concat([market_open_data, option_chain])
    
    spot_price = get_current_nifty_price()
    market_open_data = calculate_greeks(market_open_data, spot_price)
    
    while True:
        current_data = pd.DataFrame()
        for expiry in expiry_dates:
            current_option_chain = get_option_chain(expiry)
            current_data = pd.concat([current_data, current_option_chain])
        
        spot_price = get_current_nifty_price()
        current_data = calculate_greeks(current_data, spot_price)
        
        # Calculate deltas and custom columns
        for greek in ['Delta', 'Vega', 'Theta']:
            current_data[f'{greek} Change'] = current_data[greek] - market_open_data[greek]
        
        current_data['Delta-Vega'] = current_data['Delta'] * current_data['Vega']
        current_data['Delta-Theta'] = current_data['Delta'] * current_data['Theta']
        
        # Aggregate deltas across all options and weeks
        aggregated_deltas = current_data[[f'{greek} Change' for greek in ['Delta', 'Vega', 'Theta']]].sum()
        
        print("Aggregated Deltas:")
        print(aggregated_deltas)
        print("\nCurrent Option Chain:")
        print(current_data[['symbol', 'strike', 'type', 'price', 'Delta', 'Vega', 'Theta', 'Delta Change', 'Vega Change', 'Theta Change', 'Delta-Vega', 'Delta-Theta']])
        
        time.sleep(1)  # Update interval

if __name__ == '__main__':
    track_greeks_and_deltas()
