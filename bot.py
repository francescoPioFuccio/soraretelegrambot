import os
import telegram
from cap_engine import get_all_players, calculate_cap
import time

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']

bot = telegram.Bot(token=TELEGRAM_TOKEN)

def send_message(text):
    bot.send_message(chat_id=CHAT_ID, text=text)

def main():
    all_players = get_all_players()
    report = []

    for p in all_players:
        current_cap, _ = calculate_cap(p['id'], include_current_gw=False)
        projected_cap, _ = calculate_cap(p['id'], include_current_gw=True)
        if current_cap is None or projected_cap is None:
            continue
        variation = projected_cap - current_cap
        if variation < 0:
            report.append((p['full_name'], current_cap, projected_cap, variation))

    # Ordina per peggior variazione
    report.sort(key=lambda x: x[3])
    top = report[:5]  # top 5 peggiori variazioni

    msg = "📉 Migliori variazioni negative CAP:\n"
    for name, current, projected, var in top:
        msg += f"{name}: {current} -> {projected} ({var})\n"

    send_message(msg)

if __name__ == "__main__":
    main()
