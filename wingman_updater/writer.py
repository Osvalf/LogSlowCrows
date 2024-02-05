import requests
from time import perf_counter
import re
import pickle
import numpy as np
import concurrent.futures
import json

raid_names = {
    "vg" : "VG",
    "gors" : "GORSEVAL",
    "sab" : "SABETHA",
    
    "sloth" : "SLOTH",
    "matt" : "MATTHIAS",
    
    "esc" : "ESCORT",
    "kc" : "KC",
    "xera" : "XERA",
    
    "cairn" : "CAIRN",
    "mo" : "MO",
    "sam" : "SAMAROG",
    "dei" : "DEIMOS",
    
    "sh" : "SH",
    "dhuum" : "DHUUM",
    
    "ca" : "CA",
    "twins" : "LARGOS",
    "qadim" : "QUOIDIMM",
    
    "adina" : "ADINA",
    "sabir" : "SABIR",
    "qpeer" : "QTP",
}

strike_names = {
    "ice": "COL",
    "kodas": "KODANS",
    "frae": "FRAENIR",
    "bone": "BONESKINNER",
    "woj": "WOJ",
    
    "mai": "AH",
    "ankka": "ANKKA",
    "li": "KO",
    "va": "HT",
    "olc": "OLC",
    "dagda": "DAGDA",
    "cerus": "FEBE"   
}


raids_nm = list(raid_names.keys())
raids_cm = ["kc"]+list(raid_names.keys())[8:]

strikes_nm = list(strike_names.keys())
strikes_cm = list(strike_names.keys())[5:]

modes = {}
nm_raid_bosses = {}
cm_raid_bosses = {}
nm_strike_bosses = {}
cm_strike_bosses = {}

def update_log_times(name, mode, cm):
    if name == "qadim":
        name = "q1"
    if name == "qpeer":
        name = "q2"
    url = f"https://gw2wingman.nevermindcreations.de/content/{mode.lower()}/{name}?"
    url += "onlyMyRecords=AllRecords&"
    url += "noSpeedruns=includeGroupRuns&"
    url += "fromDate=2012-08-28&"
    url += "untilDate=2024-02-03&"
    url += "IncludeEra_24-01=on&"
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
        
    data = assemble_data(html)
    
    if name == "q1":
        name = "qadim"
    if name == "q2":
        name = "qpeer"
    
    if mode == "RAID": 
        if cm:
            cm_raid_bosses[raid_names[name]] = data
        else:
            nm_raid_bosses[raid_names[name]] = data
    if mode == "STRIKE": 
        if cm:
            cm_strike_bosses[strike_names[name]] = data
        else:
            nm_strike_bosses[strike_names[name]] = data
    return

def update_nm_raids():
    print("Updating NM RAIDS")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(update_log_times, name, "RAID", False) for name in raids_nm]
        concurrent.futures.wait(futures)  
    print("parsing NM RAIDS done")
        
def update_cm_raids():
    print("Updating CM RAIDS")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(update_log_times, name, "RAID", True) for name in raids_cm]
        concurrent.futures.wait(futures)  
    print("parsing CM RAIDS done")
    
def update_nm_strikes():
    print("Updating NM STRIKES")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(update_log_times, name, "STRIKE", False) for name in strikes_nm]
        concurrent.futures.wait(futures)  
    print("parsing NM STRIKES done")
    
def update_cm_strikes():
    print("Updating CM STRIKES")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(update_log_times, name, "STRIKE", True) for name in strikes_cm]
        concurrent.futures.wait(futures)  
    print("parsing CM STRIKES done")
    
def find_links(html):
    links = html.split("links = ")[1]
    for i, c in enumerate(links):
        if c == "]":
            links = links[:i+1]
            break      
    links = eval(links)
    for i, link in enumerate(links):
        links[i] = "https://gw2wingman.nevermindcreations.de/log/"+link
    return links

def find_mecas(html):
    scripts = html.split("<script>")
    textsript = scripts[8]
    textsript = textsript.split("var layout = {")[0]
    names = textsript.split("name: '")[1:]

    for i, name in enumerate(names):
        names[i] = name.splitlines()[0][:-2]
    return names

def add_data(mecas,html):
    data = {}
    for meca in mecas:
        data[meca] = eval(html.split(f"'{meca}',")[1].split("y:")[1].split("],")[0]+"]")
    return data

def assemble_data(html):
    links = find_links(html)
    mecas = find_mecas(html)
    data = add_data(mecas,html)
    data["links"] = links
    return data
        
def update_all():
    start = perf_counter()
    update_nm_raids()
    update_cm_raids()
    update_nm_strikes()
    update_cm_strikes()
    modes["RAIDS"] = {"NM": nm_raid_bosses, "CM": cm_raid_bosses}
    modes["STRIKES"] = {"NM": nm_strike_bosses, "CM": cm_strike_bosses}
    with open("WINGMAN_DATA.json", "w") as final:
        json.dump(modes, final)
    end = perf_counter()
    print(f"Done in {end - start:.3f}s")
    
def test():
    with open("wingman_updater/WINGMAN_DATA.json", "r") as final:
        data = json.load(final)
    
    i, bossname,  maxDown = None, None, 0
    for name, boss in data["RAIDS"]["NM"].items():
        if max(boss["Downed"]) > maxDown:
            maxDown = max(boss["Downed"])
            i = boss["Downed"].index(maxDown)
            bossname = name 
    print(bossname, maxDown, i)
    
    
update_all()
#test()

