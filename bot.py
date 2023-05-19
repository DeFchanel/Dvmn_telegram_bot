import requests
import os
from dotenv import load_dotenv
import telegram
import time

if __name__ == '__main__':
    load_dotenv()
    reconnect_delay = 10
    dvmn_token = os.getenv('DVMN_TOKEN')
    tg_bot_token = os.getenv('TG_BOT_TOKEN')
    chat_id = os.getenv('TG_CHAT_ID')
    bot = telegram.Bot(token=tg_bot_token)
    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'Token {dvmn_token}'
    }
    params = None
    while True:
        try:
            response = requests.get(url, headers=headers,params=params)
            response.raise_for_status()
            check_result = response.json()
            if check_result['status'] == 'timeout':
                params = {
                    'timestamp': check_result['timestamp_to_request']
                }
                continue
            else:
                bot.send_message(chat_id=chat_id, text=f"У вас проверили работу '{check_result['new_attempts'][0]['lesson_title']}'.")
                if check_result['new_attempts'][0]['is_negative']:
                    bot.send_message(chat_id=chat_id, text=f"К сожалению в работе нашлись ошибки.")
                else:
                    bot.send_message(chat_id=chat_id, text="Все верно! Можно приступать к следующему уроку!.")
                bot.send_message(chat_id=chat_id, text=f"Ссылка на урок: {check_result['new_attempts'][0]['lesson_url']}.")
                params = {
                    'timestamp': check_result['new_attempts'][0]['timestamp']
                }
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            time.sleep(reconnect_delay)
            continue
        
