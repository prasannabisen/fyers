from fyers_apiv3 import fyersModel

client_id = "GWIYQXYDUI-100"
secret_key = "ZS0R3TLDZN"
redirect_uri = "http://127.0.0.1:5173/"
response_type = "code"  
state = "sample_state"

session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type=response_type
)

responseUrl = session.generate_authcode()
print(responseUrl)