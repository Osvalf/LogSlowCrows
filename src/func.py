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

def txt_file_to_list(filepath: str):
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
            
    try:
        assert(len(input_urls)>=19)
    except:
        print(f"Tu as mis seulement {len(input_urls)} logs valides sur les 19\n")
        print("Voici ceux qu'il manque :\n")
        for e in boss_names:
            print(f" - {e.upper()}")
        sys.exit("\nVoilà rajoute les maintenant o7\n")
        
    if escort != None:
        input_urls.append(escort)
    return input_urls
 