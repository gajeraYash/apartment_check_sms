from twilio.rest import Client
from decouple import config
from datetime import datetime
import logging
logging.basicConfig(
    format="%(name)s - %(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("{0}_{1}.log".format(config('SMSLOGS'),datetime.now().strftime('%Y%m%d'))),
        logging.StreamHandler()
    ])
logger=logging.getLogger() 
if config("DEBUG",cast=bool):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

def alert(info):
    account_sid=config('TWILIO_ACCOUNT_SID')
    auth_token=config('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            to=config('RECIEVER'),
            from_=config('SENDER'),
            body=info,
            )
        logging.info(message.sid)
        logging.info(f"TO:{config('RECIEVER')} FROM:{config('SENDER')} \nMESSAGE:\n{info}")
    except Exception as e:
        logging.error(e)

if __name__ == "__main__":
    alert("TEST MESSAGE\nPYTHON SCRIPT\n\n------")