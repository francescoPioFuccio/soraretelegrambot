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
    print("🚀 Avvio scan giocatori...", flush=True)
    all_players = get_all_players()
    print(f"Trovati {len(all_players)} giocatori attivi", flush=True)
    report = []

    for idx, p in enumerate(all_players, 1):
        print(f"[{idx}/{len(all_players)}] Controllo {p['full_name']}", flush=True)
        current_cap, _ = calculate_cap(p['id'], include_current_gw=False)
        projected_cap, _ = calculate_cap(p['id'], include_current_gw=True)
        if current_cap is None or projected_cap is None:
            print("  -> Nessun dato valido per questo giocatore", flush=True)
            continue
        variation = projected_cap - current_cap
        print(f"  -> CAP attuale={current_cap}, CAP previsto={projected_cap}, var={variation}", flush=True)
        if variation < 0:
            report.append((p['full_name'], current_cap, projected_cap, variation))

    if report:
        report.sort(key=lambda x: x[3])
        top = report[:5]
        msg = "📉 Migliori variazioni negative CAP:\n"
        for name, current, projected, var in top:
            msg += f"{name}: {current} -> {projected} ({var})\n"
        send_message(msg)
        print("✅ Messaggio inviato al bot Telegram", flush=True)
    else:
        print("✅ Nessuna variazione negativa da segnalare", flush=True)

    print("🛑 Scan completato", flush=True)

if __name__ == "__main__":
    main()
