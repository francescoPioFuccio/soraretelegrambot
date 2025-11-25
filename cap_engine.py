from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
from datetime import datetime, timedelta
import pandas as pd

SEASON = "2025-26"

def sorare_score(row):
    pts = row.get('PTS', 0)
    reb = row.get('REB', 0)
    ast = row.get('AST', 0)
    blk = row.get('BLK', 0)
    stl = row.get('STL', 0)
    to = row.get('TOV', 0)
    fg3m = row.get('FG3M', 0)

    score = pts*1 + reb*1.2 + ast*1.5 + blk*3 + stl*3 + to*-2 + fg3m*1
    double_count = sum([pts>=10, reb>=10, ast>=10, blk>=10, stl>=10])
    if double_count >= 2: score += 1
    if double_count >= 3: score += 1

    print(f"DEBUG: PTS={pts}, REB={reb}, AST={ast}, BLK={blk}, STL={stl}, TOV={to}, FG3M={fg3m}, Score={score}", flush=True)
    return score

def get_gw_start(today=None):
    if today is None:
        today = datetime.today()
    weekday = today.weekday()
    if weekday <= 3:
        gw_start = today - timedelta(days=weekday)
    else:
        gw_start = today - timedelta(days=weekday-4)
    return datetime(gw_start.year, gw_start.month, gw_start.day)

def calculate_cap(player_id, include_current_gw=True):
    try:
        gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=SEASON, season_type_all_star='Regular Season')
        df = gamelog.get_data_frames()[0]
    except Exception as e:
        print(f"Errore recupero game log per player {player_id}: {e}", flush=True)
        return None, []

    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    gw_start = get_gw_start()

    if include_current_gw:
        past_games = df
    else:
        past_games = df[df['GAME_DATE'] < gw_start]

    if past_games.empty:
        return None, []

    scores = past_games.apply(sorare_score, axis=1)
    last_10_scores = scores.head(10).tolist()
    cap_raw = sum(last_10_scores)/len(last_10_scores)
    cap = int(cap_raw + 0.5)
    print(f"DEBUG: player_id={player_id}, cap_raw={cap_raw}, cap={cap}", flush=True)
    return cap, last_10_scores

def get_all_players():
    print("Recupero lista giocatori attivi...", flush=True)
    return players.get_active_players()
