import math
from datetime import datetime, timedelta, timezone
from const import *
from languages import *


def time_to_index(time: int):  # time in millisecond
    return int(time / 150)


def get_dist(pos1: list[float], pos2: list[float]):
    x1, y1 = pos1[0], pos1[1]
    x2, y2 = pos2[0], pos2[1]
    return math.hypot(x1 - x2, y1 - y2)


def disp_time(td: timedelta):
    days, seconds = td.days, td.seconds
    hours = seconds // 3600
    minutes = (seconds // 60) % 60
    seconds = seconds % 60
    if days:
        return f"{days}d{hours:02}h{minutes:02}m{seconds:02}s"
    elif hours:
        return f"{hours}h{minutes:02}m{seconds:02}s"
    elif minutes:
        return f"{minutes}m{seconds:02}s"
    else:
        return f"{seconds}s"


def txt_file_to_lines(filepath: str):
    try:
        with open(filepath, 'r') as file:
            return file.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return []


def lines_to_urls(lines: list[str], reward_mode=False):

    input_urls = []
    boss_names = list(boss_dict.values())
    escort_url = None

    for line in lines:
        line = line.strip()
        if is_valid_url(line):
            if line.endswith("esc"):
                escort_url = line
            else:
                input_urls.append(line)
            boss_names.remove(line.split("_")[1])

    number_urls = len(input_urls)

    if reward_mode and number_urls < 19:
        error_message = ""
        error_message += f"Tu as mis seulement **{len(input_urls)}** logs valides sur les **19**\n"
        error_message += "Voici ceux qu'il manque pour compléter la reward :saluting_face:\n"
        for e in boss_names:
            error_message += f"- {e.upper()}\n"
        return error_message, True

    if escort_url:
        input_urls.append(escort_url)

    return input_urls, False


def is_valid_url(line):
    parts = line.split("_")
    if "https://dps.report/" in line and parts[1] in boss_dict.values() and parts[0].split("-")[1].isdigit() and parts[0].split("-")[2].isdigit():
        return True
    return False


def get_message_reward(logs: list, players: dict, titre="Run"):
    if not logs:
        print("No boss found")
        return []

    def cut_text(text):
        run_message_length = len(text)
        if run_message_length >= cutting_text_limit:
            split_message.append(text)
            return ""
        return text

    cutting_text_limit = 1800

    mvp = []
    lvp = []
    max_mvp_score = 1
    max_lvp_score = 1

    for player in players.values():
        if player.mvps > max_mvp_score:
            max_mvp_score = player.mvps
            mvp = [player]
        elif player.mvps == max_mvp_score:
            mvp.append(player)
        if player.lvps > max_lvp_score:
            max_lvp_score = player.lvps
            lvp = [player]
        elif player.lvps == max_lvp_score:
            lvp.append(player)

    mvp_names = [player.name for player in mvp]
    lvp_names = [player.name for player in lvp]

    wings = [[] for _ in range(7)]
    for log in logs:
        wings[log.wing - 1].append(log)

    wings = [wing for wing in wings if wing]

    wings.sort(key=lambda wing: wing[0].start_date, reverse=False)

    run_date = logs[0].start_date.strftime("%d/%m/%Y")
    run_duration = disp_time(logs[-1].end_date - logs[0].start_date)
    number_boss = len(logs)

    run_message = langues["selected_language"]["TITRE RUN"].format(titre=titre, run_date=run_date) if number_boss > 1 else ""

    split_message = []
    total_wingman_score = 0
    for wing in wings:
        wing_number = wing[0].wing
        wing_first_log = wing[0]
        wing_last_log = wing[-1]
        wing_duration = disp_time(wing_last_log.end_date - wing_first_log.start_date)

        if wing_number == 1:
            run_message += langues["selected_language"]["W1"].format(wing_duration=wing_duration)
        elif wing_number == 3:
            escort_in_run = any(boss.name == "ESCORT" for boss in wing)
            if escort_in_run:
                run_message += f"## W3 - *{wing_duration}*\n"
            else:
                run_message += langues["selected_language"]["W3"].format(wing_duration=wing_duration)
        elif wing_number == 7:
            run_message += langues["selected_language"]["W7"].format(wing_duration=wing_duration)
        else:
            run_message += f"## W{wing_number} - *{wing_duration}*\n"

        for boss in wing:
            boss_name = boss.name + (" CM" if boss.cm else "")
            boss_duration = disp_time(timedelta(seconds=boss.duration_ms / 1000))
            boss_url = boss.log.url
            boss_percentil = boss.wingman_percentile
            total_wingman_score += boss_percentil

            run_message += f"* **[{boss_name}]({boss_url})** **{boss_duration} ({boss_percentil:.1f}%{emote_wingman})**\n"
            run_message = cut_text(run_message)

            if boss.mvp:
                run_message += boss.mvp + "\n"
                run_message = cut_text(run_message)
            if boss.lvp:
                run_message += boss.lvp + "\n"
                run_message = cut_text(run_message)

        run_message += "\n"

    if number_boss > 1 and len(wings) > 1:
        mvps = ', '.join(mvp_names)
        lvps = ', '.join(lvp_names)
        note_wingman = total_wingman_score / number_boss
        run_message += langues["selected_language"]["MVP"].format(mvps=mvps, max_mvp_score=max_mvp_score)
        run_message += langues["selected_language"]["LVP"].format(lvps=lvps, max_lvp_score=max_lvp_score)
        run_message += langues["selected_language"]["TIME"].format(run_duration=run_duration)
        run_message += langues["selected_language"]["WINGMAN"].format(note_wingman=note_wingman, emote_wingman=emote_wingman)

    player_rankings = list(filter(
        lambda x: x[1] is not None,
        [(player.account, player.get_mark()) for player in players.values()]
    ))
    player_rankings.sort(key=lambda r: r[1], reverse=True)
    for r in player_rankings:
        run_message += f"{r[0]} a la note moyenne de {r[1]:0.2f}/20 en dps\n"
    split_message.append(run_message)

    logs.clear()
    players.clear()

    return split_message
