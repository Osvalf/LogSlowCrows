import requests
from time import perf_counter
import re
import pickle
import numpy as np
import concurrent.futures
import json
from datetime import date

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

n_boss_raid_nm = len(raids_nm)
n_boss_raid_cm = len(raids_cm)
n_boss_strike_nm = len(strikes_nm)
n_boss_strike_cm = len(strikes_cm)

boss_raid_nm_count = 0
boss_raid_cm_count = 0
boss_strike_nm_count = 0
boss_strike_cm_count = 0

modes = {}
nm_raid_bosses = {}
cm_raid_bosses = {}
nm_strike_bosses = {}
cm_strike_bosses = {}

def get_patch_value():
    with requests.Session() as session:
        html = session.get("https://gw2wingman.nevermindcreations.de/vg").content.decode("utf-8")
    patch_value = html.split('<option value="')[1].split('"')[0]
    patch_name = html.split(f'<option value="{patch_value}">')[1].split("</option>")[0]
    return patch_value, patch_name

patch_value, patch_name = get_patch_value()

def get_bar(p, length=40):
    
    plain = "█"
    empty = "▒"
    n_plain = round(p*length)
    n_empty = length - n_plain
    return plain*n_plain + empty*n_empty

def update_log_times(name, mode, cm):
    if name == "qadim":
        name = "q1"
    if name == "qpeer":
        name = "q2"
    url = f"https://gw2wingman.nevermindcreations.de/content/{mode.lower()}/{name}?"
    url += "onlyMyRecords=AllRecords&"
    url += "noSpeedruns=includeGroupRuns&"
    url += "fromDate=2012-08-28&"
    url += f"untilDate={date.today()}&"
    url += f"IncludeEra_{patch_value}=on&"
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
            global boss_raid_cm_count
            boss_raid_cm_count += 1
            print(f"{get_bar(boss_raid_cm_count/(n_boss_raid_cm))} {boss_raid_cm_count/n_boss_raid_cm*100:.2f}%",end="\r")
        else:
            nm_raid_bosses[raid_names[name]] = data
            global boss_raid_nm_count
            boss_raid_nm_count += 1
            print(f"{get_bar(boss_raid_nm_count/(n_boss_raid_nm))} {boss_raid_nm_count/n_boss_raid_nm*100:.2f}%",end="\r")
    if mode == "STRIKE": 
        if cm:
            cm_strike_bosses[strike_names[name]] = data
            global boss_strike_cm_count
            boss_strike_cm_count += 1
            print(f"{get_bar(boss_strike_cm_count/(n_boss_strike_cm))} {boss_strike_cm_count/n_boss_strike_cm*100:.2f}%",end="\r")
        else:
            nm_strike_bosses[strike_names[name]] = data
            global boss_strike_nm_count
            boss_strike_nm_count += 1
            print(f"{get_bar(boss_strike_nm_count/(n_boss_strike_nm))} {boss_strike_nm_count/n_boss_strike_nm*100:.2f}%",end="\r")
    return

def update_nm_raids():
    print("Updating NM RAIDS")
    print(f"{get_bar(0)} 0.00%",end="\r")  
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(update_log_times, name, "RAID", False) for name in raids_nm]
        concurrent.futures.wait(futures)
    print(f"{get_bar(1)} 100.00%",end="\r")    
    print("\nparsing NM RAIDS done")
        
def update_cm_raids():
    print("Updating CM RAIDS")
    print(f"{get_bar(0)} 0.00%",end="\r") 
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(update_log_times, name, "RAID", True) for name in raids_cm]
        concurrent.futures.wait(futures)
    print(f"{get_bar(1)}100.00%",end="\r")  
    print("\nparsing CM RAIDS done")
    
def update_nm_strikes():
    print("Updating NM STRIKES")
    print(f"{get_bar(0)} 0.00%",end="\r") 
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(update_log_times, name, "STRIKE", False) for name in strikes_nm]
        concurrent.futures.wait(futures)
    print(f"{get_bar(1)} 100.00%",end="\r")    
    print("\nparsing NM STRIKES done")
    
def update_cm_strikes():
    print("Updating CM STRIKES")
    print(f"{get_bar(0)} 0.00%",end="\r") 
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(update_log_times, name, "STRIKE", True) for name in strikes_cm]
        concurrent.futures.wait(futures)
    print(f"{get_bar(1)} 100.00%",end="\r")    
    print("\nparsing CM STRIKES done")
    
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
    print(f"Updating for : {patch_name}\n")
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

    mode_name, cmnm, boss_name, i_max, Max = None, None, None, None, 0
    meca = "Downed"
    for Mode_name, Mode in data.items():
        if True:
            for CmNm, Bosses in Mode.items():
                for Boss_name, Boss in Bosses.items():
                    if Boss_name not in ["KO","HT","OLC"]:
                        for i_val, val in enumerate(Boss[meca]):
                            if val > Max:
                                mode_name, cmnm, boss_name, i_max, Max = Mode_name, CmNm, Boss_name, i_val, val

    print(f"{meca} = {Max} : {data[mode_name][cmnm][boss_name]['links'][i_max]}")
        
    
    
update_all()
#test()


