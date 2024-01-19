import math
from datetime import datetime, timedelta, timezone
from const import*

class InsufficientLogsError(Exception):
    pass

def time_to_index(time: int): #time in millisecond
    return int(time/150)

def get_dist(pos1: list[float], pos2: list[float]):
    x1, y1 = pos1[0], pos1[1]
    x2, y2 = pos2[0], pos2[1]
    return math.hypot(x1 - x2, y1 - y2)

def disp_time(td: timedelta):
    days, seconds = td.days, td.seconds
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if days == 0:
        if hours == 0:
            time = f"{minutes}m{seconds:02}s" if minutes > 0 else f"{seconds}s"
        else:
            time = f"{hours}h{minutes:02}m{seconds:02}s"
    else:
        time = f"{days}d{hours:02}h{minutes:02}m{seconds:02}s"
    return time
    
def txt_file_to_list(filepath: str, reward_mode=False):
    try:
        with open(filepath, 'r') as file:
            input_text = file.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return []
    input_lines = [line.strip() for line in input_text]
    input_urls = []
    boss_names = list(boss_dict.values())
    escort_url = None
    for line in input_lines:
        if is_valid_url(line):
            if line.endswith("esc"):
                escort_url = line
            else:
                input_urls.append(line)
            boss_names.remove(line.split("_")[1])
    number_urls = len(input_urls)
    if reward_mode and number_urls < 19:
        print(f"You only provided {number_urls} valid logs out of 19\n")
        print("The following logs are missing:\n")
        for boss_name in boss_names:
            print(f" - {boss_name.upper()}")
        raise InsufficientLogsError("\nPlease add the missing logs now. o7\n")
    if escort_url:
        input_urls.append(escort_url)
    return input_urls

def is_valid_url(line):
    parts = line.split("_")
    if "https://dps.report/" in line and parts[1] in boss_dict.values() and parts[0].split("-")[1].isdigit() and parts[0].split("-")[2].isdigit():
        return True
    return False

def get_message_reward(logs: list, all_players: dict, titre="Run"):
    if not logs:
        print("No boss found")
        return []
    mvp = []
    lvp = []
    max_mvp_score = 1
    max_lvp_score = 1
    for player in all_players.values():
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
    
    w1, w2, w3, w4, w5, w6, w7 = [], [], [], [], [], [], []
    for log in logs:
        wing = log.wing
        match wing:
            case 1:
                w1.append(log)
            case 2:
                w2.append(log)
            case 3:
                w3.append(log)
            case 4:
                w4.append(log)
            case 5:
                w5.append(log)
            case 6:
                w6.append(log)
            case 7:
                w7.append(log)
    
    all_wings = [w1,w2,w3,w4,w5,w6,w7]     
    wings = []
    for wing in all_wings:
        if wing:
            wings.append(wing)
    wings.sort(key=lambda wing: wing[0].start_date, reverse=False)
    first_log = all_bosses[0]
    last_log = all_bosses[-1]
    run_date = first_log.start_date.strftime("%d/%m/%Y")
    run_duration = disp_time(last_log.end_date - first_log.start_date)
    number_boss = len(all_bosses)
    if number_boss > 1:
        run_message = f"# {titre} du {run_date}\n"
    else:
        run_message = ""
    escort_in_run = False
    split_message = []
    for wing in wings:
        wing_number = wing[0].wing
        wing_first_log = wing[0]
        wing_last_log = wing[-1]
        wing_duration = disp_time(wing_last_log.end_date - wing_first_log.start_date)
        match wing_number:
            case 1:
                run_message += f"## W1 - *{wing_duration}* (sans pre-VG)\n"
            case 3:
                for boss in wing:
                    if boss.name == "ESCORT":
                        escort_in_run = True
                        break
                if escort_in_run:
                    run_message += f"## W3 - *{wing_duration}*\n"
                else:
                    run_message += f"## W3 - *{wing_duration}* (sans escort)\n"
            case 7:
                run_message += f"## W7 - *{wing_duration}* (sans gate)\n"
            case _:
                run_message += f"## W{wing_number} - *{wing_duration}*\n"
        for boss in wing:
            boss_name = boss.name
            if boss.cm:
                boss_name += " CM"
            boss_duration = disp_time(timedelta(seconds=boss.duration_ms / 1000))
            boss_url = boss.log.url
            boss_percentil = boss.wingman_percentile
            run_message += f"* **[{boss_name}]({boss_url})** **{boss_duration} ({boss_percentil}{emote_wingman})**\n"
            if boss.mvp:
                run_message += boss.mvp + "\n"
            if boss.lvp:
                run_message += boss.lvp + "\n"
        run_message += "\n"
        cutting_text_limit = 1050
        run_message_length = len(run_message)
        if run_message_length >= cutting_text_limit:
            split_message.append(run_message)
            run_message = ""
    if number_boss > 1 and len(wings) > 1:
        run_message += f"# [GRAND MVP : {', '.join(mvp_names)} avec {max_mvp_score} titres]\n"
        run_message += f"# [GRAND LVP : {', '.join(lvp_names)} avec {max_lvp_score} titres]\n"
        run_message += f"# Temps total : {run_duration}"
    split_message.append(run_message)
    all_bosses.clear()
    all_players.clear()
    return split_message
