import requests
import pandas as pd



class TokenResolver:



    def __init__(self):
        self.url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        self.data = requests.get(self.url).json()
        self.df = pd.DataFrame(self.data)

    def get_token(self, symbol):

        #symbol = "NIFTY14JUL2624050CE"
        token = self.df[self.df['symbol'] == symbol]['token'].values[0]
        return token

token_resolver = TokenResolver()

