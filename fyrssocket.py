from fyers_apiv3.FyersWebsocket import data_ws
import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()

def onmessage(message):
    print("Response:", message)

def onerror(message):
    print("Error:", message)

def onclose(message):
    print("Connection closed:", message)

def onopen():
    data_type = "SymbolUpdate"
    symbols = ['NSE:SBIN-EQ', 'NSE:ADANIENT-EQ']
    fyers.subscribe(symbols=symbols, data_type=data_type)
    fyers.keep_running()

access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE3MjU4ODU4OTEsImV4cCI6MTcyNTkyODI1MSwibmJmIjoxNzI1ODg1ODkxLCJhdWQiOlsieDowIiwieDoxIiwiZDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCbTN1M0RMdG8zXzl5Q3Ftc3duWVVvb3FDZ3JyUTFnQUV2bkI1NEtDNlpjYzZRSWdHR1BwdmFSbUtjYWlsSUFIYTJoYm5BWjFIMkxWY0pkNWNjLVVDVEgyTU8wVkdqcUJ5NTRmQVJoYjJMVmJuYkFpUT0iLCJkaXNwbGF5X25hbWUiOiJQUkFTQU5OQSBCSVNFTiIsIm9tcyI6IksxIiwiaHNtX2tleSI6IjFlZWM4NmNhNmI2ZTIxMWVkYmE2ZTFjNDViYjIyMzE2MzQ0MTM3MjgxZTg0Mzc1MWYyYjVjYzVjIiwiZnlfaWQiOiJYUDMzNjU5IiwiYXBwVHlwZSI6MTAwLCJwb2FfZmxhZyI6Ik4ifQ.WBrXx-eaTHGUzNm8Z_Og7Q7Qj20efuDvLp6IyWcyTuk"

fyers = data_ws.FyersDataSocket(
    access_token=access_token,       # Access token in the format "appid:accesstoken"
    log_path="",                     # Path to save logs. Leave empty to auto-create logs in the current directory.
    litemode=False,                  # Lite mode disabled. Set to True if you want a lite response.
    write_to_file=False,              # Save response in a log file instead of printing it.
    reconnect=True,                  # Enable auto-reconnection to WebSocket on disconnection.
    on_connect=onopen,               # Callback function to subscribe to data upon connection.
    on_close=onclose,                # Callback function to handle WebSocket connection close events.
    on_error=onerror,                # Callback function to handle WebSocket errors.
    on_message=onmessage             # Callback function to handle incoming messages from the WebSocket.
)

fyers.connect()