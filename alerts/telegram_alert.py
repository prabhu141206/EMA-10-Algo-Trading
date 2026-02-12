import requests
from config.settings import TELEGRAM_CHAT_ID, TELEGRAM_TOKEN


class TelegramAlertEngine:

    def send(self, message):  

        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:  
            print("[TELEGRAM] Missing credentials")  
            return  

        try:  
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"  

            data = {  
                "chat_id": TELEGRAM_CHAT_ID,  
                "text": message,  
                "parse_mode": "HTML"  
            }  
            
            try :

                r = requests.post(url, data=data, timeout=5)  
                if r.status_code != 200:
                    print("[TELEGRAM FAILED]", r.text)
                    
            except Exception as e :
                print("[TELEGRAM ERROR]", e)

        except Exception as e:  
            print("[TELEGRAM ERROR]", e)

telegram_alert = TelegramAlertEngine()


