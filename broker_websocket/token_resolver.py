import requests
import pandas as pd
import time


class TokenResolver:



    def __init__(self):
        self.url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"

        while True:

            try:

                self.data = requests.get(self.url).json()

                if(self.data is not None):
                    break
                
            except Exception as e :
                print("Error :", e)
                print("Retrying it agian......")
                time.sleep(6)
                continue

        self.df = pd.DataFrame(self.data)

    def get_token(self, symbol):

        #symbol = "NIFTY14JUL2624050CE"
        token = self.df[self.df['symbol'] == symbol]['token'].values[0]
        return token

token_resolver = TokenResolver()

