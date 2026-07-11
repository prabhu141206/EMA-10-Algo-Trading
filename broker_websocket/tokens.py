import requests
import pandas as pd

url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"



data = requests.get(url).json()
df = pd.DataFrame(data)

