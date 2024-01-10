import math
from datetime import datetime, timedelta, timezone
from const import*
import sys

def time_to_index(time: int): #time in millisecond
    return int(time/150)

def get_dist(pos1: list[float,float], pos2: list[float,float]):
    return math.sqrt((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)

def disp_time(td: timedelta):
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if(days==0 and hours==0 and minutes==0):
        time = f"{seconds}s"
    elif(days==0 and hours==0):
        time = f"{minutes}m{seconds:02}s"
    elif(days==0):
        time = f"{hours}h{minutes:02}m{seconds:02}s"
    else:
        time = f"{days}d{hours:02}h{minutes:02}m{seconds:02}s"
    return time

def txt_file_to_list(filepath: str, reward=False):
    with open(filepath, 'r') as file:
        lines = file.readlines()

    input_lines = [line.strip() for line in lines]

    boss_names = list(boss_dict.values())
    input_urls=[]
    escort = None
    for i in range(len(input_lines)):
        if ("https://" in input_lines[i]) and (input_lines[i].split("_")[1] in boss_names):
            if input_lines[i][-3:] == "esc":
                escort = input_lines[i]
            else:
                input_urls.append(input_lines[i])
            boss_names.remove(input_lines[i].split("_")[1])
    
    if reward and len(input_urls) < 19: 
        print(f"Tu as mis seulement {len(input_urls)} logs valides sur les 19\n")
        print("Voici ceux qu'il manque :\n")
        for e in boss_names:
            print(f" - {e.upper()}")
        sys.exit("\nVoilà rajoute les maintenant o7\n")
        
    if escort:
        input_urls.append(escort)
    return input_urls

def get_message_reward(logs: list, dict_mvp: dict, dict_lvp: dict, titre="Run"):
    if not logs:
        print("No boss found")
        return []
    mvp_scores = dict_mvp.values()
    lvp_scores = dict_lvp.values()
    if len(mvp_scores) > 1:
        score_max_mvp = max(dict_mvp.values())
        mvps = [k for k, v in dict_mvp.items() if v == score_max_mvp]
    if len(lvp_scores) > 1:
        score_max_lvp = max(dict_lvp.values()) 
        lvps = [k for k, v in dict_lvp.items() if v == score_max_lvp]
    
    w1, w2, w3, w4, w5, w6, w7 = [], [], [], [], [], [], []
    for e in logs:
        wing = e.wing
        match wing:
            case 1:
                w1.append(e)
            case 2:
                w2.append(e)
            case 3:
                w3.append(e)
            case 4:
                w4.append(e)
            case 5:
                w5.append(e)
            case 6:
                w6.append(e)
            case 7:
                w7.append(e)
    
    temp_wings = [w1,w2,w3,w4,w5,w6,w7]     
    wings = []
    for e in temp_wings:
        if e:
            wings.append(e)
    wings.sort(key=lambda x: x[0].start_date, reverse=False)
    first_log = all_bosses[0]
    last_log = all_bosses[-1]
    reward_date = first_log.start_date.strftime("%d/%m/%Y")
    reward_duration = disp_time(last_log.end_date - first_log.start_date)
    if len(all_bosses)>1:
        reward = f"# {titre} du {reward_date}\n"
    else:
        reward = ""
    escort = False
    split_message = []
    for i in wings:
        current_wing_n = i[0].wing
        current_wing_duration = disp_time(i[-1].end_date - i[0].start_date)
        match current_wing_n:
            case 1:
                reward += f"## W1 - *{current_wing_duration}* (sans pre-VG)\n"
            case 3:
                for e in i:
                    if e.name == "ESCORT":
                        escort = True
                        break
                if escort:
                    reward += f"## W3 - *{current_wing_duration}*\n"
                else:
                    reward += f"## W3 - *{current_wing_duration}* (sans escort)\n"
            case 7:
                reward += f"## W7 - *{current_wing_duration}* (sans gate)\n"
            case _:
                reward += f"## W{current_wing_n} - *{current_wing_duration}*\n"
        for j in i:
            current_boss_name = j.name
            if j.cm:
                current_boss_name += " CM"
            current_boss_duration = disp_time(timedelta(seconds=j.duration_ms / 1000))
            current_boss_url = j.log.url
            reward += f"* {current_boss_duration} : **[{current_boss_name}]({current_boss_url})**\n"
            if j.wingman_time:
                med = disp_time(timedelta(seconds=j.wingman_time[0] / 1000))
                top = disp_time(timedelta(seconds=j.wingman_time[1] / 1000))
                reward += f"\t:wingman: med. {med} top. {top}\n"
            if j.mvp:
                reward += j.mvp + "\n"
            if j.lvp:
                reward += j.lvp + "\n"
        reward += "\n"
        if len(reward) >= 1150:
            split_message.append(reward)
            reward = ""
    if len(all_bosses) > 1 and len(all_mvp) > 1 and len(all_lvp) > 1 and len(wings) > 1:
        reward += f"# [GRAND MVP : {', '.join(mvps)} avec {score_max_mvp} titres]\n"
        reward += f"# [GRAND LVP : {', '.join(lvps)} avec {score_max_lvp} titres]\n"
        reward += f"# Temps total : {reward_duration}"
    split_message.append(reward)
    all_bosses.clear()
    all_mvp.clear()
    all_lvp.clear()
    return split_message
