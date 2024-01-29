import requests
from time import perf_counter
import re
import pickle
import numpy as np
import concurrent.futures
import json

boss_dict = {
    15438 : "vg",
    15429 : "gors",
    15375 : "sab",
    16123 : "sloth",
    16115 : "matt",
    16253 : "esc",
    16235 : "kc",
    16246 : "xera",
    17194 : "cairn",
    17172 : "mo",
    17188 : "sam",
    17154 : "dei",
    19767 : "sh",
    19450 : "dhuum",
    43974 : "ca",
    21105 : "twins",
    20934 : "qadim",
    22006 : "adina",
    21964 : "sabir",
    22000 : "qpeer"}


boss_nm = list(boss_dict.values())
boss_cm = ["kc"]+list(boss_dict.values())[8:]

timers = {}
timers_nm = {}
timers_cm = {}

def update_log_times(name, cm):
    if name == "qadim":
        name = "q1"
    if name == "qpeer":
        name = "q2"
    url = f"https://gw2wingman.nevermindcreations.de/content/raid/{name}?"
    url += "onlyMyRecords=AllRecords&"
    url += "noSpeedruns=includeGroupRuns&"
    url += "fromDate=2012-08-28&"
    url += "untilDate=2024-01-09&"
    url += "IncludeEra_23-11=on&"
    url += "sampleSize=-1&"
    url += "onlyKills=OnlyKills&"
    url += "minimumPlayers=10&"
    url += "maximumPlayers=10&"
    url += "maxBossHP=100&"
    if cm:
        url += "onlyCM=onlyCM&"
    else:
        url += "onlyCM=onlyNM&"
    url += "minEmboldened=0&"
    url += "maxEmboldened=0&"
    url += "logPercentile=0&"
    url += "IncludeEnglishLogs=on&"
    url += "IncludeFrenchLogs=on&"
    url += "IncludeGermanLogs=on&"
    url += "IncludeSpanishLogs=on&"
    url += "currentGraph=AllRoles"
            
    with requests.Session() as session:
        html = session.get(url).content.decode("utf-8")
        
    pattern = r'durationPoints\.push\((\d+\.\d+)\);'
    matches = re.findall(pattern, html)
    values = [float(match) for match in matches].sort()
    
    if name == "q1":
        name = "qadim"
    if name == "q2":
        name = "qpeer"
    
    if cm:
        timers_cm[name] = values
    else:
        timers_nm[name] = values
    return

def update_nm():
    print("Updating NM")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(update_log_times, name, False) for name in boss_nm]
        concurrent.futures.wait(futures)
        
    print("parsing NM done")
    
    timers['nm_times'] = timers_nm
    
    with open("nm_times.json", "w") as final:
        json.dump(timers_nm, final)
        
def update_cm():
    print("Updating CM")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(update_log_times, name, True) for name in boss_cm]
        concurrent.futures.wait(futures)
        
    print("parsing CM done")
    
    with open("cm_times.json", "w") as final:
        json.dump(timers_cm, final)
        
def main():
    start = perf_counter()
    update_nm()
    update_cm()
    end = perf_counter()
    print(f"Done in {end - start:.3f}s")
    
main()


