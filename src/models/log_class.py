from urllib.request import Request, urlopen
import json
import requests
import numpy as np
from func import *
from models.player_class import *

class Log:
    def __init__(self, url: str):
        self.url = url
        self.content = self.get_html()
        self.jcontent = self.get_parsed_json()
        self.pjcontent = self.get_not_parsed_json()
        BossFactory.create_boss(self)

    def get_html(self):        # url convertie en string contenant les infos en javascript
        with requests.Session() as session:
            html_text = session.get(self.url).content.decode("utf-8")
        return html_text

    def get_parsed_json(self):     # javascript converti en json
        java_data_text = self.content.split('var _logData = ')[1].split('var logData = _logData;')[0].rsplit(';', 1)[0].strip()
        json_content = json.loads(java_data_text)
        return json_content
    
    def get_not_parsed_json(self):
        return requests.get(f"https://dps.report/getJson?permalink={self.url}").json()
    
class BossFactory:
    @staticmethod
    def create_boss(log : Log):
        boss = None
        factory = {"vg": VG,
                   "gors": GORS,
                   "sab": SABETHA,   
                                   
                   "sloth": SLOTH,
                   "matt": MATTHIAS,    
                                  
                   "esc": ESCORT,
                   "kc": KC,
                   "xera": XERA,
                   
                   "cairn": CAIRN,
                   "mo": MO,
                   "sam": SAMAROG,
                   "dei": DEIMOS,   
                                   
                   "sh": SH,
                   "dhuum": DHUUM,   
                                   
                   "ca": CA,
                   "twins": LARGOS,
                   "qadim": Q1,      
                   
                   "adina": ADINA,
                   "sabir": SABIR,
                   "qpeer": QTP,
                   
                   "golem": GOLEM}
        
        boss_name = boss_dict.get(log.jcontent['triggerID'])
        if boss_name:
            all_bosses.append(factory[boss_name](log))
                 
        
class Boss:  

    name = None
    wing = 0
    boss_id = -1

    def __init__(self, log: Log):
        self.log = log
        self.cm = self.is_cm()
        self.logName = self.get_logName()
        self.mechanics = self.get_mechanics()
        self.duration_ms = self.get_duration_ms() 
        self.start_date = self.get_start_date()
        self.end_date = self.get_end_date()
        self.player_list = self.get_player_list()
        self.wingman_time = self.get_wingman_time()
        self.wingman_percentile = self.get_wingman_percentile()
        for i in self.player_list:
            account = self.get_player_account(i)
            player = all_players.get(account)
            if not player:
                new_player = Player(self, account)
                all_players[account] = new_player
            else:
                player.add_boss(self)
        
    ################################ Fonction pour attribus Boss ################################
    
    def is_cm(self):
        return self.log.pjcontent['isCM']
    
    def get_logName(self):
        return self.log.pjcontent['fightName']
    
    def get_mechanics(self):
        mechs = []
        mechanic_map = self.log.jcontent['mechanicMap']
        for mechanic in mechanic_map:
            is_player_mechanic = mechanic['playerMech']
            if is_player_mechanic:
                mechs.append(mechanic)
                
        return mechs
    
    def get_duration_ms(self):
        return self.log.pjcontent['durationMS']
    
    def get_start_date(self):
        start_date_text = self.log.pjcontent['timeStartStd']
        date_format = "%Y-%m-%d %H:%M:%S %z"
        start_date = datetime.strptime(start_date_text, date_format)
        paris_timezone = timezone(timedelta(hours=1))
        return start_date.astimezone(paris_timezone)
    
    def get_end_date(self):
        end_date_text = self.log.pjcontent['timeEndStd']
        date_format = "%Y-%m-%d %H:%M:%S %z"
        end_date = datetime.strptime(end_date_text, date_format)
        paris_timezone = timezone(timedelta(hours=1))
        return end_date.astimezone(paris_timezone)

    def get_wingman_time(self):
        # return None
        w_boss_id = self.boss_id * (-1) ** self.cm
        url = f"https://gw2wingman.nevermindcreations.de/api/boss?era=latest&bossID={w_boss_id}"
        r = requests.get(url)
        if not r.ok:
            print("wingman faled")
            print(r.status_code)
            print(r.content)
            return None
        data = r.json()
        if data.get("error"):
            print("wingman failed")
            print(data["error"])
            return None
        return [data["duration_med"], data["duration_top"]]
    
    def get_player_list(self):
        real_players = []
        players = self.log.pjcontent['players']
        for i_player, player in enumerate(players):
            if player['group'] < 50 and not self.is_buyer(i_player):
                real_players.append(i_player)
                
        return real_players
    
    def get_wingman_percentile(self):
            log_time_ms = self.duration_ms
            boss_short_name = boss_dict.get(self.boss_id)                  
            if self.cm:
                if cm_dict.get(boss_short_name):
                    all_wingman_boss_times_ms = np.sort(np.array(list(cm_dict[boss_short_name]))*60*1000)[::-1]
                else:
                    return
            else:
                if nm_dict.get(boss_short_name):
                    all_wingman_boss_times_ms = np.sort(np.array(list(nm_dict[boss_short_name]))*60*1000)[::-1]
                else:
                    return               
            all_wingman_boss_times_ms = np.sort(np.append(all_wingman_boss_times_ms, log_time_ms))[::-1]
            i = np.where(all_wingman_boss_times_ms==log_time_ms)[0][0]
            percentile = i/(len(all_wingman_boss_times_ms)-1)*100
            return f"{percentile:.1f}%"
            
    ################################ CONDITIONS ################################
        
    def is_quick(self, i_player: int):
        min_quick_contrib = 20
        player_quick_contrib = self.log.jcontent['phases'][0]['boonGenGroupStats'][i_player]['data'][2]
        return player_quick_contrib[0] >= min_quick_contrib or player_quick_contrib[1] >= min_quick_contrib

    def is_alac(self, i_player: int):
        min_alac_contrib = 20
        player_alac_contrib = self.log.jcontent['phases'][0]['boonGenGroupStats'][i_player]['data'][3]
        return player_alac_contrib[0] >= min_alac_contrib or player_alac_contrib[1] >= min_alac_contrib
    
    def is_support(self, i_player: int):
        return self.is_quick(i_player) or self.is_alac(i_player)
    
    def is_dps(self, i_player: int):
        return not self.is_support(i_player)
    
    def is_tank(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['toughness'] > 0
    
    def is_heal(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['healing'] > 0
    
    def is_dead(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['defenses'][0]['deadCount'] > 0
    
    def is_buyer(self, i_player: int):
        player_name = self.get_player_name(i_player)
        i_death = None
        mechanics = self.log.pjcontent.get('mechanics')
        if mechanics:
            for i_mech, mech in enumerate(mechanics):
                if mech['name'] == "Dead":
                    i_death = i_mech
                    break
            if i_death is not None:
                death_history = mechanics[i_death]['mechanicsData']
                for death in death_history:
                    if death['time'] < 20000 and death['actor'] == player_name:
                        return True
        return False
    
    ################################ DATA JOUEUR ################################
    
    def get_player_name(self, i_player: int):
        return self.log.jcontent['players'][i_player]['name']
    
    def get_player_account(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['account']
    
    def get_pos_player(self, i_player: int , start: int = 0, end: int = None): 
        return self.log.pjcontent['players'][i_player]['combatReplayData']['positions'][start:end]
    
    def get_cc_boss(self, i_player: int):
        return self.log.jcontent['phases'][0]['dpsStatsTargets'][i_player][0][3]
    
    def get_dmg_boss(self, i_player: int):
        return self.log.jcontent['phases'][0]['dpsStatsTargets'][i_player][0][0]
    
    def get_cc_total(self, i_player: int):
        return self.log.jcontent['phases'][0]['dpsStats'][i_player][3]
    
    def get_player_id(self, name: str):
        players = self.log.pjcontent['players'] 
        for i_player, player in enumerate(players):
            if player['name'] == name:
                return i_player
        
        return None
    
    def get_mvp_cc_boss(self, extra_exclude: list[classmethod]=[]):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_boss, exclude=[*extra_exclude])
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1  
        mvp_names = self.players_to_string(i_players)
        cc_ratio = min_cc / total_cc * 100
        number_mvp = len(i_players)  
        if min_cc == 0:
            if number_mvp == 1:
                return f" * *[**MVP** : {mvp_names} n'a pas mis de **CC**]*"
            else:
                return f" * *[**MVP** : {mvp_names} n'ont pas mis de **CC**]*"
        else:
            if number_mvp == 1:
                return f" * *[**MVP** : {mvp_names} n'a mis que **{min_cc:.0f}** de **CC** (**{cc_ratio:.1f}%** de la squad)]*"
            else:
                return f" * *[**MVP** : {mvp_names} n'ont mis que **{min_cc:.0f}** de **CC** (**{cc_ratio:.1f}%** de la squad)]*"
            
    def get_lvp_cc_boss(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_boss)
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].lvps += 1
        lvp_names = self.players_to_string(i_players)
        cc_ratio = max_cc / total_cc * 100
        return f" * *[**LVP** : {lvp_names} merci d'avoir fait **{max_cc:.0f}** de **CC** (**{cc_ratio:.1f}%** de la squad)]*"
    
    def get_mvp_cc_total(self,extra_exclude: list[classmethod]=[]):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_total, exclude=[*extra_exclude])
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1  
        mvp_names = self.players_to_string(i_players)
        cc_ratio = min_cc / total_cc * 100
        number_mvp = len(i_players)  
        if min_cc == 0:
            if number_mvp == 1:
                return f" * *[**MVP** : {mvp_names} n'a pas mis de **CC**]*"
            else:
                return f" * *[**MVP** : {mvp_names} n'ont pas mis de **CC**]*"
        else:
            if number_mvp == 1:
                return f" * *[**MVP** : {mvp_names} n'a mis que **{min_cc:.0f}** de **CC** (**{cc_ratio:.1f}%** de la squad)]*"
            else:
                return f" * *[**MVP** : {mvp_names} n'ont mis que **{min_cc:.0f}** de **CC** (**{cc_ratio:.1f}%** de la squad)]*"
            
    def get_lvp_cc_total(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_total)
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].lvps += 1
        lvp_names = self.players_to_string(i_players)
        cc_ratio = max_cc / total_cc * 100
        return f" * *[**LVP** : {lvp_names} merci d'avoir fait **{max_cc:.0f}** de **CC** (**{cc_ratio:.1f}%** de la squad)]*"
    
    def get_bad_dps(self, extra_exclude: list[classmethod]=[]):
        i_sup, sup_max_dmg, _ = Stats.get_max_value(self, self.get_dmg_boss, exclude=[self.is_dps])
        i_dps, dps_min_dmg, _ = Stats.get_min_value(self, self.get_dmg_boss, exclude=[self.is_support, self.is_dead, *extra_exclude])
        if dps_min_dmg < sup_max_dmg:
            bad_dps = i_dps[0]
            bad_dps_name = self.players_to_string([bad_dps])
            bad_dps_account = self.get_player_account(bad_dps)
            all_players[bad_dps_account].mvps += 1
            sup_name = self.get_player_name(i_sup[0])
            dmg_ratio = (1 - dps_min_dmg / sup_max_dmg) * 100 
            return f" * *[**MVP** : {bad_dps_name} qui en **DPS** n'a fait que **{dps_min_dmg / self.duration_ms :.1f}kdps** soit **{dmg_ratio:.1f}%** de moins que {sup_name} qui joue **support** on le rappelle]*"
        return
    
    def get_lvp_dps(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_boss)
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].lvps += 1
        dmg_ratio = max_dmg / total_dmg * 100
        lvp_dps_name = self.players_to_string(i_players)
        return f" * *[**LVP** : {lvp_dps_name} qui a fait **{max_dmg / self.duration_ms:.1f}kdps** (**{dmg_ratio:.0f}%** de la squad)]*"
    
    ################################ DATA BOSS ################################
    
    def get_pos_boss(self, start: int = 0, end: int = None):
        targets = self.log.pjcontent['targets']
        for target in targets:
            if target['id'] in boss_dict.keys():
                return target['combatReplayData']['positions'][start:end]
        raise ValueError('No Boss in targets')
    
    def get_phase_id(self, target_phase: str):
        phases = self.log.pjcontent['phases']
        for phase in phases:
            if phase['name'] == target_phase:
                start = time_to_index(phase['start'])
                end = time_to_index(phase['end'])
                return start, end
        raise ValueError(f'{target_phase} not found')
    
    def get_mech_value(self, i_player: int, mech_name: str):
        mechs_list = [mech['name'] for mech in self.mechanics]
        if mech_name in mechs_list:
            i_mech = mechs_list.index(mech_name)
            return self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_mech][0]
        return 0
    
    def players_to_string(self, i_players: list[int]):
        return ', '.join([self.get_player_name(i) for i in i_players])
            
    
class Stats:
    @staticmethod
    def get_max_value(boss : Boss,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):

        value_max = -1
        value_tot = 0
        i_maxs = []
        for i in boss.player_list:
            value = fnc(i)
            value_tot += value
            for filtre in exclude:
                if filtre(i):
                    break
            else:
                if value > value_max:
                    value_max = value
                    i_maxs = [i]
                elif value == value_max:
                    i_maxs.append(i)
        if value_max == 0:
            return [] , value_max , value_tot
        return i_maxs, value_max, value_tot
    
    @staticmethod
    def get_min_value(boss : Boss,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):

        value_min = BIG
        value_tot = 0
        i_mins = []
        for i in boss.player_list:
            value = fnc(i)
            value_tot += value
            for filtre in exclude:
                if filtre(i):
                    break
            else:
                if value < value_min:
                    value_min = value
                    i_mins = [i]
                elif value == value_min:
                    i_mins.append(i)
        return i_mins, value_min, value_tot

    @staticmethod
    def get_tot_value(boss : Boss,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):
                
        value_tot = 0
        for i in boss.player_list:
            for filtre in exclude:
                if filtre(i):
                    break
            value_tot += fnc(i)
        return value_tot
    
################################ VG ################################

class VG(Boss):
    
    last = None
    name = "VG"
    wing = 1
    boss_id = 15438
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        VG.last = self
        
    def get_mvp(self):
        msg_bleu = self.mvp_bleu()
        if msg_bleu:
            return msg_bleu
        return    
    
    def get_lvp(self):
        return
        
    ################################ MVP ################################   
    
    def mvp_bleu(self):
        i_players, max_bleu, _ = Stats.get_max_value(self, self.get_bleu)
        mvp_names = self.players_to_string(i_players)
        
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        if len(i_players) == 1:
            return f" * *[**MVP** : {mvp_names} s'est pris **{max_bleu}** **bleues**]*"
        if len(i_players) > 1:
            return f" * *[**MVP** : {mvp_names} se sont tous les {len(i_players)} pris **{max_bleu}** **bleues**]*"         
        return
    
    ################################ LVP ################################
    


    ################################ CONDITIONS ###############################
    
    
    
    ################################ DATA MECHAS ################################
    
    def get_bleu(self, i_player: int):
        bleu_split = self.get_mech_value(i_player, "Green Guard TP")
        bleu_boss = self.get_mech_value(i_player, "Boss TP")
        return bleu_boss + bleu_split

################################ GORS ################################

class GORS(Boss):
    
    last = None
    name = "GORS"
    wing = 1
    boss_id = 15429
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        GORS.last = self
        
    def get_mvp(self):
        return self.mvp_dmg_split()
    
    def get_lvp(self):
        return self.lvp_dmg_split()
        
    ################################ MVP ################################
    
    def mvp_dmg_split(self):
        i_players, min_dmg, total_dmg = Stats.get_min_value(self, self.get_dmg_split, exclude=[self.is_support])
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        mvp_names = self.players_to_string(i_players)
        dmg_ratio = min_dmg / total_dmg * 100
        return f" * *[**MVP** : {mvp_names} avec seulement **{dmg_ratio:.1f}%** des degats sur **split** en **DPS**]*"
    
    ################################ LVP ################################
    
    def lvp_dmg_split(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_split)
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].lvps += 1
        lvp_names = self.players_to_string(i_players)
        dmg_ratio = max_dmg / total_dmg * 100
        return f" * *[**LVP** : {lvp_names} avec **{dmg_ratio:.1f}%** des degats sur **split** en **DPS**]*"

    ################################ CONDITIONS ###############################
    
    
    
    ################################ DATA MECHAS ################################
        
    def get_dmg_split(self, i_player: int):
        dmg_split = 0
        dmg_split_1 = self.log.jcontent['phases'][3]['dpsStatsTargets'][i_player]
        dmg_split_2 = self.log.jcontent['phases'][6]['dpsStatsTargets'][i_player]
        for add_split1, add_split2 in zip(dmg_split_1,dmg_split_2):
            dmg_split += add_split1[0] + add_split2[0]
        return dmg_split
    
################################ SABETHA ################################

class SABETHA(Boss):
    
    last = None
    name = "SABETHA"
    wing = 1
    boss_id = 15375
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SABETHA.last = self
        
    def get_mvp(self):
        return self.mvp_dmg_split()
    
    def get_lvp(self):
        return self.lvp_dmg_split()
    
    ################################ MVP ################################
    
    def mvp_dmg_split(self):
        i_players, min_dmg, total_dmg = Stats.get_min_value(self, self.get_dmg_split, exclude=[self.is_support,self.is_cannon])
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        dmg_ratio = min_dmg / total_dmg * 100
        mvp_names = self.players_to_string(i_players)
        return f" * *[**MVP** : {mvp_names} avec seulement **{dmg_ratio:.1f}%** des degats sur **split** sans faire de **canon**]*"
    
    ################################ LVP ################################
    
    def lvp_dmg_split(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_split)
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].lvps += 1
        lvp_names = self.players_to_string(i_players)
        dmg_ratio = max_dmg / total_dmg * 100
        return f" * *[**LVP** : {lvp_names} avec **{dmg_ratio:.1f}%** des degats sur **split** en **DPS**]*"

    ################################ CONDITIONS ###############################
    
    def is_cannon(self, i_player: int, n: int=0):
        pos_player = self.get_pos_player(i_player)
        match n:
            case 0: 
                canon_pos = [pos_canon1, pos_canon2, pos_canon3, pos_canon4]
            case 1:
                canon_pos = [pos_canon1]
            case 2:
                canon_pos = [pos_canon2]
            case 3:
                canon_pos = [pos_canon3]
            case 4:
                canon_pos = [pos_canon4]
            case _:
                canon_pos = []
        for pos in pos_player:
            for canon in canon_pos:
                if get_dist(pos, canon) <= canon_detect_radius:
                    return True
        return False
    
    ################################ DATA MECHAS ################################
        
    def get_dmg_split(self,i_player: int):
        dmg_kernan = self.log.jcontent['phases'][2]['dpsStatsTargets'][i_player][0][0]
        dmg_mornifle = self.log.jcontent['phases'][5]['dpsStatsTargets'][i_player][0][0]
        dmg_karde = self.log.jcontent['phases'][7]['dpsStatsTargets'][i_player][0][0]
        return dmg_kernan + dmg_mornifle + dmg_karde  

################################ SLOTH ################################

class SLOTH(Boss):
    
    last = None
    name = "SLOTH"
    wing = 2
    boss_id = 16123
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SLOTH.last = self
        
    def get_mvp(self):
        return self.mvp_cc_sloth()    
        
    def get_lvp(self):
        return self.get_lvp_cc_boss()
        
    ################################ MVP ################################
    
    def mvp_cc_sloth(self):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_boss, exclude=[self.is_shroom])
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        cc_ratio = min_cc / total_cc * 100
        mvp_names = self.players_to_string(i_players)
        if min_cc == 0:
            if len(i_players) > 1:
                return f" * *[**MVP** : {mvp_names} qui n'ont même pas **CC** sans manger de **shroom**]*"
            return f" * *[**MVP** : {mvp_names} qui n'a même pas **CC** sans manger de **shroom**]*"
        if len(i_players) > 1:
            return f" * *[**MVP** : {mvp_names} qui ont fait seulement **{min_cc:.0f}** de **CC** (**{cc_ratio:.1f}%** du total) sans manger de **shroom**]*"
        return f" * *[**MVP** : {mvp_names} qui a fait seulement **{min_cc:.0f}** de **CC** (**{cc_ratio:.1f}%** du total) sans manger de **shroom**]*"
    
    ################################ LVP ################################
    
    

    ################################ CONDITIONS ###############################
    
    def is_shroom(self, i_player: int):
        return self.get_mech_value(i_player, "Slub Transform") > 0
    
    ################################ DATA MECHAS ################################
    


################################ MATTHIAS ################################

class MATTHIAS(Boss):
    
    last = None
    name = "MATTHIAS"
    wing = 2
    boss_id = 16115
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        MATTHIAS.last = self
        
    def get_mvp(self):
        return self.mvp_cc_matthias()
        
    def get_lvp(self):
        return self.lvp_cc_matthias()
          
    ################################ MVP ################################
    
    def mvp_cc_matthias(self):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_total, exclude=[self.is_sac])
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        cc_ratio = min_cc / total_cc * 100
        mvp_names = self.players_to_string(i_players)
        if min_cc == 0:
            return f" * *[**MVP** : {mvp_names} avec aucun **CC** sans s'être **sacrifié**]*"
        else:
            return f" * *[**MVP** : {mvp_names} avec seulement **{min_cc:.0f}** de **CC** (**{cc_ratio:.1f}%** du total) sans s'être sacrifié]*"
        
    ################################ LVP ################################
            
    def lvp_cc_matthias(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_total)       
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].lvps += 1
        cc_ratio = max_cc / total_cc * 100
        lvp_names = self.players_to_string(i_players)
        return f" * *[**LVP** : {lvp_names} merci d'avoir mis **{max_cc:.0f}** de **CC** (**{cc_ratio:.1f}%** de la squad)]*"

    ################################ CONDITIONS ###############################
    
    def is_sac(self, i_player: int):
        return self.get_nb_sac(i_player) > 0
    
    ################################ DATA MECHAS ################################    
    
    def get_nb_sac(self, i_player: int):
        return self.get_mech_value(i_player, "Sacrifice")

################################ ESCORT ################################

class ESCORT(Boss):
    
    last = None
    name = "ESCORT"
    wing = 3
    boss_id = 16253
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        ESCORT.last = self 
        
    def get_mvp(self):
        msg_mine = self.mvp_mine()
        if msg_mine:
            return msg_mine
        return
       
    def get_lvp(self):
        return self.lvp_glenna()
    
    ################################ MVP ################################
    
    def mvp_mine(self):
        i_players = self.get_mined_players()
        if i_players:
            for i in i_players:

                account = self.get_player_account(i)
                all_players[account].mvps += 1
            mvp_names = self.players_to_string(i_players)
            if len(i_players) == 1:
                return f" * *[**MVP** : {mvp_names} qui a bien **profité** de l'escort en prenant une **mine**]*"
            else:
                return f" * *[**MVP** : {mvp_names} qui ont bien **profité** de l'escort en prenant une **mine**]*"
        return
    
    ################################ LVP ################################
    
    def lvp_glenna(self):
        i_players, max_call, _ = Stats.get_max_value(self, self.get_glenna_call)
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].lvps += 1
        lvp_names = self.players_to_string(i_players)
        return f" * *[**LVP** : {lvp_names}, merci d'avoir **call** glenna **{max_call}** fois]*"
    
    ################################ CONDITIONS ################################
    
    def is_mined(self, i_player: int):
        return self.get_mech_value(i_player, "Mine Detonation Hit") > 0
    
    ################################ DATA MECHAS ################################
    
    def get_mined_players(self):
        p = []
        for i in self.player_list:
            if self.is_mined(i):
                p.append(i)
        return p
    
    def get_glenna_call(self, i_player: int):
        return self.get_mech_value(i_player, "Over Here! Cast")

################################ KC ################################

class KC(Boss):
    
    last = None
    name = "KC"
    wing = 3
    boss_id = 16235
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        KC.last = self  
        
    def get_mvp(self):
        return self.mvp_orb_kc()
    
    def get_lvp(self):
        return 
        
    ################################ MVP ################################
            
    def mvp_orb_kc(self):
        i_players, min_orb, _ = Stats.get_min_value(self, self.get_good_orb)
        mvp_names = self.players_to_string(i_players)
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        if min_orb == 0:
            return f" * *[**MVP** : {mvp_names} avec aucune **orbe** collectée sur tout le fight]*"
        else:
            return f" * *[**MVP** : {mvp_names} avec seulement **{min_orb}** orbes collectées sur tout le fight]*"
            
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    def get_good_orb(self, i_player: int):
        red_orbs = self.get_mech_value(i_player, 'Good Red Orb')
        white_orbs = self.get_mech_value(i_player, 'Good White Orb')
        return red_orbs + white_orbs

################################ XERA ################################

class XERA(Boss):
    
    last = None
    name = "XERA"
    wing = 3
    boss_id = 16246

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        XERA.last = self  
        
    def get_mvp(self):
        msg_fdp = self.mvp_fdp_xera()
        if msg_fdp:
            return msg_fdp
        msg_glide = self.mvp_glide()
        if msg_glide:
            return msg_glide
        return self.get_mvp_cc_boss()
    
    def get_lvp(self):
        msg_minijeu = self.lvp_minijeu()
        if msg_minijeu:
            return msg_minijeu
        return self.get_lvp_cc_boss()    
        
    ################################ MVP ################################
    
    def mvp_fdp_xera(self):
        i_fdp = self.get_fdp()
        fdp_names = self.players_to_string(i_fdp)
        for i in i_fdp:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        if len(i_fdp) == 1:
            return f" * *[**MVP** : oui {fdp_names} a vraiment **skip** un **mini-jeu**]*"
        if len(i_fdp) > 1:
            return f" * *[**MVP** : oui {fdp_names} ont vraiment **skip** un **mini-jeu**]*"
        return
    
    def mvp_glide(self):
        i_glide = self.get_gliding_death()
        glide_names = self.players_to_string(i_glide)
        for i in i_glide:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        if len(i_glide) == 1:
            return f" * *[**MVP** : {glide_names} champion **mort** pendant le **glide**]*"
        if len(i_glide) > 1:
            return f" * *[**MVP** : {glide_names} champions **morts** pendant le **glide**]*"
        return
    
    ################################ LVP ################################
    
    def lvp_minijeu(self):
        i_players, max_minijeu, _ = Stats.get_max_value(self, self.get_tp_back, exclude=[self.is_fdp])
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].lvps += 1
        lvp_names = self.players_to_string(i_players)
        if max_minijeu == 2:
            return f" * *[**LVP** : {lvp_names} merci d'avoir tanké **2** mini-jeu sans les skip]*"
        return
    
    ################################ CONDITIONS ################################
    
    def is_fdp(self, i_player: int):
        return i_player in self.get_fdp()
    
    ################################ DATA MECHAS ################################

    def get_tp_out(self, i_player: int):
        return self.get_mech_value(i_player, 'TP')
    
    def get_tp_back(self, i_player: int):
        return self.get_mech_value(i_player, 'TP back')
    
    def get_fdp(self): # fdp = skip mini jeu XERA
        mecha_data = self.log.pjcontent['mechanics']
        tp_data = None
        for e in mecha_data:
            if e['name'] == "TP Out":
                tp_data = e['mechanicsData']
                break
        fdp = []
        delta = 10000
        i_delta = time_to_index(delta)
        for e in tp_data:
            tp_time = e['time']
            player_name = e['actor']
            i_player = self.get_player_id(player_name)
            tp_time += 1000  # 1s de delais pour etre sur
            i_time = time_to_index(tp_time)
            pos_player = self.get_pos_player(i_player, i_time, i_time + i_delta)
            for p in pos_player:
                if get_dist(p, xera_centre) <= xera_centre_radius:
                    fdp.append(i_player)
                    break
        return fdp
    
    def get_gliding_death(self):
        dead = []
        for i in self.player_list:
            if self.log.pjcontent['players'][i]['defenses'][5]['deadCount'] > 0:
                dead.append(i)
        return dead     

################################ CAIRN ################################

class CAIRN(Boss):
    
    last = None
    name = "CAIRN"
    wing = 4
    boss_id = 17194
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        CAIRN.last = self
        
    def get_mvp(self):
        return self.get_bad_dps()          
    
    def get_lvp(self):
        return self.get_lvp_dps()
      
    ################################ MVP ################################
    
    
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

################################ MO ################################

class MO(Boss):
    
    last = None
    name = "MO"
    wing = 4
    boss_id = 17172
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        MO.last = self
        
    def get_mvp(self):
        return self.get_bad_dps()
    
    def get_lvp(self):
        return self.get_lvp_dps()   
        
    ################################ MVP ################################
    
    
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

      

################################ SAMAROG ################################

class SAMAROG(Boss):
    
    last = None
    name = "SAMAROG"
    wing = 4
    boss_id = 17188
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SAMAROG.last = self
        
    def get_mvp(self):
        msg_impaled = self.mvp_impaled()
        if msg_impaled:
            return msg_impaled
        return self.get_mvp_cc_boss()
    
    def get_lvp(self):
        return self.get_lvp_cc_boss()
    
    ################################ MVP ################################ 
    
    def mvp_impaled(self):
        i_players = self.get_impaled()
        mvp_names = self.players_to_string(i_players)
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        if len(i_players) == 1:
            return f" * *[**MVP** : {mvp_names} s'est fait **empaler**, gros respect]*" 
        if len(i_players) > 1:
            return f" * *[**MVP** : {mvp_names} se sont fait **empaler**, gros respect]*"
        return  
    
    ################################ LVP ################################ 
    
    
    
    ################################ CONDITIONS ################################
    
    def is_impaled(self, i_player: int):
        if self.is_dead(i_player):
            last_pos = self.get_pos_player(i_player)[-1]
            #TOP WALL condition
            a, b, c = self.get_sama_cartesian(sama_top_left_corn, sama_top_right_corn)
            top = a * last_pos[0] + b * last_pos[1] + c < 0
            #BOT WALL condition
            a, b, c = self.get_sama_cartesian(sama_bot_left_corn, sama_bot_right_corn)
            bot = a * last_pos[0] + b * last_pos[1] + c > 0
            #LEFT WALL condition
            a, b, c = self.get_sama_cartesian(sama_top_left_corn, sama_bot_left_corn)
            left = a * last_pos[0] + b * last_pos[1] + c > 0
            #RIGHT WALL condition
            a, b, c = self.get_sama_cartesian(sama_top_right_corn, sama_bot_right_corn)
            right = a * last_pos[0] + b * last_pos[1] + c < 0
            return top or bot or left or right
        return False
    
    ################################ DATA MECHAS ################################

    @staticmethod
    def get_sama_cartesian(corner1: list[float,float], corner2: list[float,float]):
        a = corner2[1] - corner1[1]
        b = corner1[0] - corner2[0]
        c = - a * corner1[0] - b * corner1[1]
        return a, b, c  
    
    def get_impaled(self):
        i_players = []
        for i in self.player_list:
            if self.is_impaled(i):
                  i_players.append(i)
        return i_players

################################ DEIMOS ################################

class DEIMOS(Boss):
    
    last = None
    name = "DEIMOS"
    wing = 4
    boss_id = 17154
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        DEIMOS.last = self
        
    def get_mvp(self):
        msg_black = self.mvp_black()
        if msg_black:
            return msg_black
        return
    
    def get_lvp(self):
        msg_tears = self.lvp_tears()
        if msg_tears:
            return msg_tears
        return

    ################################ MVP ################################
    
    def mvp_black(self):
        i_players, max_black, _ = Stats.get_max_value(self, self.get_black_trigger)
        mvp_names = self.players_to_string(i_players)
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        if len(i_players) == 1:
            return f" * *[**MVP** : {mvp_names} merci à ce **champion** d'avoir trigger **{max_black} black**]*"
        if len(i_players) > 1:
            return f" * *[**MVP** : {mvp_names} merci à ces **champions** d'avoir tous les {len(i_players)} trigger **{max_black} black**]*"
        return
    
    ################################ LVP ################################ 
    
    def lvp_tears(self):
        i_players, max_tears, _ = Stats.get_max_value(self, self.get_tears)
        lvp_names = self.players_to_string(i_players)
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].lvps += 1
        if i_players and max_tears > 2:
            return f" * *[**LVP** : {lvp_names} merci d'avoir ramassé **{max_tears} tears**]*"
        return
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    def get_black_trigger(self, i_player: int):
        return self.get_mech_value(i_player, "Black Oil Trigger")
    
    def get_tears(self, i_player: int):
        return self.get_mech_value(i_player, "Tear")

################################ SH ################################

class SH(Boss):
    
    last = None
    name = "SH"
    wing = 5
    boss_id = 19767
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SH.last = self
        
    def get_mvp(self):
        return self.get_mvp_cc_boss()
    
    def get_lvp(self):
        return self.get_lvp_cc_boss()
        
    ################################ MVP ################################
    
    
    
    ################################ MVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

################################ DHUUM ################################

class DHUUM(Boss):
    
    last = None
    name = "DHUUM"
    wing = 5
    boss_id = 19450
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        DHUUM.last = self
        
    def get_mvp(self):
        msg_cracks = self.mvp_cracks()
        if msg_cracks:
            return msg_cracks
        return
    
    def get_lvp(self):
        return
   
    ################################ MVP ################################
    
    def mvp_cracks(self):
        i_players, max_cracks, _ = Stats.get_max_value(self, self.get_cracks)
        mvp_names = self.players_to_string(i_players)
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        if len(i_players) == 1:
            return f" * *[**MVP** : {mvp_names} s'est pris **{max_cracks} cracks**]*"
        if len(i_players) > 1:
            return f" * *[**MVP** : {mvp_names} se sont pris **{max_cracks} cracks**]*"
        return 
    
    ################################ LVP ################################
    
     
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    def get_cracks(self, i_player: int):
        return self.get_mech_value(i_player, "Cracks")    

################################ CA ################################

class CA(Boss):
    
    last = None
    name = "CA"
    wing = 6
    boss_id = 43974

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        CA.last = self
        
    def get_mvp(self):
        return self.get_bad_dps()
    
    def get_lvp(self):
        return self.get_lvp_dps()
  
    ################################ MVP ################################
    
    
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

################################ LARGOS ################################

class LARGOS(Boss):
    
    last = None
    name = "LARGOS"
    wing = 6
    boss_id = 21105

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        LARGOS.last = self
        
    def get_mvp(self):
        msg_dash = self.mvp_dash()
        if msg_dash:
            return msg_dash
        return
    
    def get_lvp(self):
        return self.get_lvp_cc_total()

    ################################ MVP ################################
        
    def mvp_dash(self):
        i_players, max_dash, _ = Stats.get_max_value(self, self.get_dash, exclude=[self.is_heal, self.is_tank])
        mvp_names = self.players_to_string(i_players)
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        if len(i_players) == 1:
            return f" * *[**MVP** : {mvp_names} s'est pris **{max_dash} dash**]*"
        if len(i_players) > 1:
            return f" * *[**MVP** : {mvp_names} se sont pris **{max_dash} dash**]*"
        return
    
    ################################ LVP ################################ 
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    def get_dash(self, i_player: int):
        return self.get_mech_value(i_player, "Vapor Rush Charge") 

################################ QADIM ################################

class Q1(Boss):
    
    last = None
    name = "QUOIDIMM"
    wing = 6
    boss_id = 20934

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        Q1.last = self
        
    def get_mvp(self):
        msg_fdp = self.mvp_fdp()
        if msg_fdp:
            return msg_fdp
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        msg_wave = self.mvp_wave()
        if msg_wave:
            return msg_wave
        return
    
    def get_lvp(self):
        return 
        
    ################################ MVP ################################
    
    def mvp_fdp(self):
        i_players = self.get_fdp()
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        fdp_names = self.players_to_string(i_players)
        if len(i_players) == 1:
            return f" * *[**MVP** : {fdp_names} n'est pas allé taper le **pyre**]*"
        if len(i_players) > 1:
            return f" * *[**MVP** : {fdp_names} ne sont pas allé taper le **pyre**]*"
    
    def mvp_wave(self):
        i_players, max_waves, _ = Stats.get_max_value(self, self.get_wave)
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        mvp_names = self.players_to_string(i_players)
        if len(i_players) == 1:
            return f" * *[**MVP** : {mvp_names} s'est pris **{max_waves} shockwave**]*"
        if len(i_players) > 1:
            return f" * *[**MVP** : {mvp_names} se sont pris **{max_waves} shockwave**]*"
        return
    
    ################################ LVP ################################ 
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    def get_fdp(self):
        fdp = []
        start_p1, end_p1 = self.get_phase_id("Qadim P1")
        start_p2, end_p2 = self.get_phase_id("Qadim P2")
        for i in self.player_list:
            if not self.is_tank(i):
                add_fdp = True
                pos_p1 = self.get_pos_player(i, start=start_p1, end=end_p1)
                pos_p2 = self.get_pos_player(i, start=start_p2, end=end_p2)
                for pos in pos_p1:
                    dist = get_dist(pos, qadim_center)
                    if dist > qadim_fdp_radius:
                        add_fdp = False
                        break        
                for pos in pos_p2:
                    dist = get_dist(pos, qadim_center)
                    if dist > qadim_fdp_radius:
                        add_fdp = False
                        break 
                if add_fdp:
                    fdp.append(i)
        return fdp
    
    def get_wave(self, i_player: int):
        return self.get_mech_value(i_player, "Mace Shockwave")

################################ ADINA ################################

class ADINA(Boss):
    
    last = None
    name = "ADINA"
    wing = 7
    boss_id = 22006
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        ADINA.last = self
        
    def get_mvp(self):
        return self.mvp_dmg_split()
    
    def get_lvp(self):
        return self.lvp_dmg_split()
        
    ################################ MVP ################################

    def mvp_dmg_split(self):
        i_players, min_dmg, total_dmg = Stats.get_min_value(self, self.get_dmg_split, exclude=[self.is_support])
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
        mvp_names = self.players_to_string(i_players)
        dmg_ratio = min_dmg / total_dmg * 100
        return f" * *[**MVP** : {mvp_names} n'a fait que **{dmg_ratio:.1f}%** des dégats sur split]*"
    
    ################################ LVP ################################    
    
    def lvp_dmg_split(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_split)
        for i in i_players:
            account = self.get_player_account(i)
            all_players[account].lvps += 1
        lvp_names = self.players_to_string(i_players)
        dmg_ratio = max_dmg / total_dmg * 100
        return f" * *[**LVP** : {lvp_names} merci d'avoir fait **{dmg_ratio:.1f}%** des dégats sur split]*"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################
    
    def get_dmg_split(self, i_player: int):
        dmg_split1 = self.log.jcontent['phases'][2]['dpsStats'][i_player][0]
        dmg_split2 = self.log.jcontent['phases'][4]['dpsStats'][i_player][0]
        dmg_split3 = self.log.jcontent['phases'][6]['dpsStats'][i_player][0]
        return dmg_split1 + dmg_split2 + dmg_split3
        

################################ SABIR ################################

class SABIR(Boss):
    
    last = None
    name = "SABIR"
    wing = 7
    boss_id = 21964
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SABIR.last = self
        
    def get_mvp(self):
        return self.get_mvp_cc_boss()
    
    def get_lvp(self):
        return self.get_lvp_cc_boss()

    ################################ MVP ################################
    
    
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

################################ QTP ################################

class QTP(Boss):
    
    last = None
    name = "QTP"
    wing = 7
    boss_id = 22000

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        QTP.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_pylon])
        if msg_bad_dps:
            return msg_bad_dps
        return self.get_mvp_cc_boss(extra_exclude=[self.is_pylon])
    
    def get_lvp(self):
        return self.get_lvp_dps() 
 
    ################################ MVP ################################
    
    
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    def is_pylon(self, i_player: int):
        return self.get_orb_caught(i_player) > 1
    
    ################################ DATA MECHAS ################################

    def get_orb_caught(self, i_player: int):
        return self.get_mech_value(i_player, "Critical Mass")
    
################################ GOLEM CHAT STANDARD ################################

class GOLEM(Boss):
    
    last = None
    name = "GOLEM CHAT STANDARD"
    boss_id = 16199
    
    def __init__(self, log: Log):
        super().__init__(log)
        GOLEM.last = self
