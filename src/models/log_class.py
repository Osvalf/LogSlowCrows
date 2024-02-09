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
        
        boss_name = boss_dict.get(log.jcontent['triggerID']) or extra_boss_dict.get(log.jcontent['triggerID'])
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
        boss_name = self.name
        if self.cm:
            raids = wingman_data.get("RAIDS")
            cms = raids.get("CM")
            boss_data = cms.get(boss_name)
            all_wingman_boss_times_ms = np.array(boss_data.get("Duration", []))*60000
        else:
            raids = wingman_data.get("RAIDS")
            nms = raids.get("NM")
            boss_data = nms.get(boss_name)
            all_wingman_boss_times_ms = np.array(boss_data.get("Duration", []))*60000
        all_wingman_boss_times_ms = np.sort(np.append(all_wingman_boss_times_ms, log_time_ms))[::-1]
        i = np.where(all_wingman_boss_times_ms == log_time_ms)[0][0]
        percentile = i / (len(all_wingman_boss_times_ms) - 1) * 100
        return percentile
            
    ################################ CONDITIONS ################################
        
    def is_quick(self, i_player: int):
        min_quick_contrib = 30
        phases = self.log.jcontent['phases']
        for phase in phases:
            player_quick_contrib = phase['boonGenGroupStats'][i_player]['data'][2]
            if player_quick_contrib[0] >= min_quick_contrib or player_quick_contrib[1] >= min_quick_contrib:
                return True
        return False

    def is_alac(self, i_player: int):
        min_alac_contrib = 30
        phases = self.log.jcontent['phases']
        for phase in phases:
            player_alac_contrib = phase['boonGenGroupStats'][i_player]['data'][3]
            if player_alac_contrib[0] >= min_alac_contrib or player_alac_contrib[1] >= min_alac_contrib:
                return True
        return False
    
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
        mechanics = self.log.pjcontent.get('mechanics')
        if mechanics:
            death_history = [death for mech in mechanics if mech['name'] == "Dead" for death in mech['mechanicsData']]
            for death in death_history:
                if death['time'] < 20000 and death['actor'] == player_name:
                    return True
        return False
    
    def is_buff_up(self, i_player: int, target_time: int, buff_name: str):
        buffmap = self.log.pjcontent['buffMap']
        buff_id = None
        for id, buff in buffmap.items():
            if buff['name'] == buff_name:
                buff_id = int(id[1:])
                break
        if buff_id is None:
            return False
        buffs = self.log.pjcontent['players'][i_player]['buffUptimes']
        for buff in buffs:
            if buff['id'] == buff_id:
                buffplot = buff['states']
                break
        xbuffplot = [pos[0] for pos in buffplot]
        ybuffplot = [pos[1] for pos in buffplot]
        
        left_value = None
        for time in xbuffplot:
            if time <= target_time:
                left_value = time
            else:
                break
        left_index = xbuffplot.index(left_value)
        if ybuffplot[left_index]:
            return True
        return False
    
    def is_dead_instant(self, i_player: int):
        downs_deaths = self.get_player_mech_history(i_player, ["Downed", "Dead"])
        if downs_deaths:
            if downs_deaths[-1]['name'] == "Dead":
                if len(downs_deaths) == 1:
                    return True
                if len(downs_deaths) > 1:
                    if downs_deaths[-2]['time'] < downs_deaths[-1]['time']-8000:
                        return True
        return False
    
    def is_condi(self, i_player: int):
        power_dmg = self.log.pjcontent['players'][i_player]['dpsAll'][0]['powerDamage']
        condi_dmg = self.log.pjcontent['players'][i_player]['dpsAll'][0]['condiDamage']
        return condi_dmg > power_dmg
    
    def is_power(self, i_player: int):
        return not self.is_condi(i_player)
    
    ################################ DATA JOUEUR ################################
    
    def get_player_name(self, i_player: int):
        return self.log.jcontent['players'][i_player]['name']
    
    def get_player_account(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['account']
    
    def get_player_pos(self, i_player: int , start: int = 0, end: int = None):
        return self.log.pjcontent['players'][i_player]['combatReplayData']['positions'][start:end]
    
    def get_cc_boss(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['dpsTargets'][0][0]['breakbarDamage']
    
    def get_dmg_boss(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['dpsTargets'][0][0]['damage']
    
    def get_cc_total(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['dpsAll'][0]['breakbarDamage']
    
    def get_player_id(self, name: str):
        players = self.log.pjcontent['players'] 
        for i_player, player in enumerate(players):
            if player['name'] == name:
                return i_player
        return None
    
    def get_player_mech_history(self, i_player: int, mechs: list[str] = []):
        history = []
        player_name = self.get_player_name(i_player)
        mech_history = self.log.pjcontent['mechanics']
        for mech in mech_history:
            for data in mech['mechanicsData']:
                if data['actor'] == player_name:
                    if mechs:
                        if mech['name'] in mechs:
                            history.append({"name": mech['name'], "time": data['time']})
                    else:
                        history.append({"name": mech['name'], "time": data['time']})
        history.sort(key=lambda mech: mech["time"], reverse=False)
        return history
    
    def players_to_string(self, i_players: list[int]):
        return "__"+'__ / __'.join([self.get_player_name(i) for i in i_players])+"__"
    
    def get_player_death_timer(self, i_player: int):
        if self.is_dead(i_player):
            mech_history = self.get_player_mech_history(i_player, ["Dead"])
            if mech_history:
                return mech_history[-1]['time']
        return
    
    def get_player_rotation(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['rotation']
    
    def time_entered_area(self, i_player: int, center: list[float], radius: float):
        poses = self.get_player_pos(i_player)
        for i, pos in enumerate(poses):
            if get_dist(pos, center) < radius:
                return i*150
        return
    
    def time_exited_area(self, i_player, center: list[float], radius: float):
        time_enter = self.time_entered_area(i_player, center, radius)
        if time_enter:
            i_enter = int(time_enter/150)
            poses = self.get_player_pos(i_player)[i_enter:]
            for i, pos in enumerate(poses):
                if get_dist(pos, center) > radius:
                    return (i+i_enter) * 150
        return
    
    def add_mvps(self, players: int):
        for i in players:
            account = self.get_player_account(i)
            all_players[account].mvps += 1
                
    def add_lvps(self, players: int):
        for i in players:
            account = self.get_player_account(i)
            all_players[account].lvps += 1
            
    
    ################################ MVP ################################
    
    def get_mvp_cc_boss(self, extra_exclude: list[classmethod]=[]):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_boss, exclude=[*extra_exclude])
        if total_cc == 0:
            return
        self.add_mvps(i_players)  
        mvp_names = self.players_to_string(i_players)
        cc_ratio = min_cc / total_cc * 100
        number_mvp = len(i_players)  
        if min_cc == 0:
            if number_mvp == 1:
                return langues["selected_language"]["MVP BOSS 0 CC S"].format(mvp_names=mvp_names)
            else:
                return langues["selected_language"]["MVP BOSS 0 CC P"].format(mvp_names=mvp_names)
        else:
            if number_mvp == 1:
                return langues["selected_language"]["MVP BOSS CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            else:
                return langues["selected_language"]["MVP BOSS CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
    
    def get_mvp_cc_total(self,extra_exclude: list[classmethod]=[]):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_total, exclude=[*extra_exclude])
        if total_cc == 0:
            return
        self.add_mvps(i_players)  
        mvp_names = self.players_to_string(i_players)
        cc_ratio = min_cc / total_cc * 100
        number_mvp = len(i_players)  
        if min_cc == 0:
            if number_mvp == 1:
                return langues["selected_language"]["MVP TOTAL 0 CC S"].format(mvp_names=mvp_names)
            else:
                return langues["selected_language"]["MVP TOTAL 0 CC P"].format(mvp_names=mvp_names)
        else:
            if number_mvp == 1:
                return langues["selected_language"]["MVP TOTAL CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            else:
                return langues["selected_language"]["MVP TOTAL CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
    
    def get_bad_dps(self, extra_exclude: list[classmethod]=[]):
        i_sup, sup_max_dmg, _ = Stats.get_max_value(self, self.get_dmg_boss, exclude=[self.is_dps])
        sup_name = self.players_to_string(i_sup)
        bad_dps = []
        for i in self.player_list:   
            if any(filter_func(i) for filter_func in extra_exclude) or self.is_dead(i) or self.is_support(i):
                continue
            dps = self.get_dmg_boss(i)
            if dps < sup_max_dmg:
                bad_dps.append(i)
        if bad_dps:
            self.add_mvps(bad_dps)
            bad_dps_name = self.players_to_string(bad_dps)
            if len(bad_dps) == 1:
                return langues["selected_language"]["MVP BAD DPS S"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)
            else:
                return langues["selected_language"]["MVP BAD DPS P"].format(bad_dps_name=bad_dps_name, sup_name=sup_name)
    
    ################################ LVP ################################
    
    def get_lvp_cc_boss(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_boss)
        if total_cc == 0:
            return
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        cc_ratio = max_cc / total_cc * 100
        return langues["selected_language"]["LVP BOSS CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)
    
    def get_lvp_cc_total(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_total)
        if total_cc == 0:
            return
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        cc_ratio = max_cc / total_cc * 100
        return langues["selected_language"]["LVP TOTAL CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)
    
    def get_lvp_dps(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_boss)
        self.add_lvps(i_players)
        dmg_ratio = max_dmg / total_dmg * 100
        lvp_dps_name = self.players_to_string(i_players)
        dps = max_dmg / self.duration_ms
        return langues["selected_language"]["LVP DPS"].format(lvp_dps_name=lvp_dps_name, max_dmg=max_dmg, dmg_ratio=dmg_ratio, dps=dps)
    
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
    
    def bosshp_to_time(self, hp: float):
        hp_percents = self.log.pjcontent['targets'][0]['healthPercents']
        for timer in hp_percents:
            if timer[1] < hp:
                return timer[0]
        return
    
    def get_mechanic_history(self, name: str):
        mechanics = self.log.pjcontent['mechanics']
        for mech in mechanics:
            if mech['fullName'] == name:
                return mech['mechanicsData']
        return
        
            
    
class Stats:
    @staticmethod
    def get_max_value(boss : Boss,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):  
        if exclude is None:
            exclude = []
        value_max = -1
        value_tot = 0
        i_maxs = []
        for i in boss.player_list:
            value = fnc(i)
            value_tot += value
            if any(filter_func(i) for filter_func in exclude):
                continue
            if value > value_max:
                value_max = value
                i_maxs = [i]
            elif value == value_max:
                i_maxs.append(i)
        if value_max == 0:
            return [], value_max, value_tot
        return i_maxs, value_max, value_tot
        
    @staticmethod
    def get_min_value(boss : Boss,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):

        if exclude is None:
            exclude = []
        value_min = BIG
        value_tot = 0
        i_mins = []
        for i in boss.player_list:
            value = fnc(i)
            value_tot += value
            if any(filter_func(i) for filter_func in exclude):
                continue
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
                
        if exclude is None:
            exclude = []
        value_tot = 0
        for i in boss.player_list:
            if any(filter_func(i) for filter_func in exclude):
                continue
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
        msg_bad_dps = self.get_bad_dps(extra_exclude=[self.is_condi])
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
        
    ################################ MVP ################################   
    
    def mvp_bleu(self):
        i_players, max_bleu, _ = Stats.get_max_value(self, self.get_bleu)
        mvp_names = self.players_to_string(i_players)
        if max_bleu > 1:
            self.add_mvps(i_players)
            nb_players = len(i_players)
            if nb_players == 1:
                return langues["selected_language"]["VG MVP BLEU S"].format(mvp_names=mvp_names, max_bleu=max_bleu)
            if nb_players > 1:
                return langues["selected_language"]["VG MVP BLEU P"].format(mvp_names=mvp_names, nb_players=nb_players, max_bleu=max_bleu)
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
    name = "GORSEVAL"
    wing = 1
    boss_id = 15429
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        GORS.last = self
        
    def get_mvp(self):
        msg_egg = self.mvp_egg()
        if msg_egg:
            return msg_egg
        
        msg_dmg_split = self.mvp_dmg_split()
        if msg_dmg_split:
            return msg_dmg_split
        
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps     
        return
    
    def get_lvp(self):
        return self.lvp_dmg_split()
        
    ################################ MVP ################################
    
    def mvp_dmg_split(self):
        i_players, min_dmg, total_dmg = Stats.get_min_value(self, self.get_dmg_split, exclude=[self.is_support])
        dps_total_dmg = Stats.get_tot_value(self, self.get_dmg_split, exclude=[self.is_support])
        if min_dmg/dps_total_dmg < 1/6*0.75:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            dmg_ratio = min_dmg / total_dmg * 100
            return langues["selected_language"]["GORS MVP SPLIT"].format(mvp_names=mvp_names, min_dmg=min_dmg, dmg_ratio=dmg_ratio)
    
    def mvp_egg(self):
        i_players = self.get_egged()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) == 1:
                return langues["selected_language"]["GORS MVP EGG S"].format(mvp_names=mvp_names)
            if len(i_players) > 1:
                return langues["selected_language"]["GORS MVP EGG P"].format(mvp_names=mvp_names)
        return 
    
    ################################ LVP ################################
    
    def lvp_dmg_split(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_split)
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        dmg_ratio = max_dmg / total_dmg * 100
        return langues["selected_language"]["GORS LVP SPLIT"].format(lvp_names=lvp_names, max_dmg=max_dmg, dmg_ratio=dmg_ratio)

    ################################ CONDITIONS ###############################
    
    def got_egged(self, i_player: int):
        return self.get_mech_value(i_player, "Egged") > 0
    
    ################################ DATA MECHAS ################################
        
    def get_dmg_split(self, i_player: int):
        dmg_split = 0
        dmg_split_1 = self.log.jcontent['phases'][3]['dpsStatsTargets'][i_player]
        dmg_split_2 = self.log.jcontent['phases'][6]['dpsStatsTargets'][i_player]
        for add_split1, add_split2 in zip(dmg_split_1,dmg_split_2):
            dmg_split += add_split1[0] + add_split2[0]
        return dmg_split
    
    def get_egged(self):
        egged = []
        for i in self.player_list:
            if self.got_egged(i):
                egged.append(i)
        return egged
    
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
        
        msg_terrorists = self.mvp_terrorists()
        if msg_terrorists:
            return msg_terrorists
        
        msg_dmg_split = self.mvp_dmg_split()
        if msg_dmg_split:
            return self.mvp_dmg_split()
        return
    
    def get_lvp(self):
        return self.lvp_dmg_split()
    
    ################################ MVP ################################
    
    def mvp_dmg_split(self):
        i_players, min_dmg, total_dmg = Stats.get_min_value(self, self.get_dmg_split, exclude=[self.is_support,self.is_cannon])
        dps_total_dmg = Stats.get_tot_value(self, self.get_dmg_split, exclude=[self.is_support])
        if min_dmg/dps_total_dmg < 1/6*0.75:
            self.add_mvps(i_players) 
            dmg_ratio = min_dmg / total_dmg * 100
            mvp_names = self.players_to_string(i_players)
            return langues["selected_language"]["SABETHA MVP SPLIT"].format(mvp_names=mvp_names, dmg_ratio=dmg_ratio)
        return
    
    def mvp_terrorists(self):
        i_players = self.get_terrorists()
        self.add_mvps(i_players)
        if i_players:
            mvp_names = self.players_to_string(i_players)
            return langues["selected_language"]["SABETHA MVP BOMB"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    def lvp_dmg_split(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_split)
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        dmg_ratio = max_dmg / total_dmg * 100
        return langues["selected_language"]["SABETHA LVP SPLIT"].format(lvp_names=lvp_names, dmg_ratio=dmg_ratio)

    ################################ CONDITIONS ###############################
    
    def is_cannon(self, i_player: int, n: int=0):
        pos_player = self.get_player_pos(i_player)
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
    
    def is_terrorist(self, i_player: int):
        bomb_history = self.get_player_mech_history(i_player, ["Timed Bomb"])
        if bomb_history:
            poses = self.get_player_pos(i_player)
            players = self.player_list
            for bomb in bomb_history:
                bomb_time = bomb['time'] + 3000
                time_index = time_to_index(bomb_time)
                try:
                    bomb_pos = poses[time_index]
                except:
                    continue
                bombed_players = 0
                for i in players:
                    if i == i_player or self.is_dead(i):
                        continue
                    i_pos = self.get_player_pos(i)[time_index]
                    if get_dist(bomb_pos, i_pos)*sabetha_scaler <= 270:
                        bombed_players += 1
                if bombed_players > 1:
                    return True
        return False
    
    ################################ DATA MECHAS ################################
        
    def get_dmg_split(self,i_player: int):
        dmg_kernan = self.log.jcontent['phases'][2]['dpsStatsTargets'][i_player][0][0]
        dmg_mornifle = self.log.jcontent['phases'][5]['dpsStatsTargets'][i_player][0][0]
        dmg_karde = self.log.jcontent['phases'][7]['dpsStatsTargets'][i_player][0][0]
        return dmg_kernan + dmg_mornifle + dmg_karde 
    
    def get_terrorists(self):
        terrotists = []
        for i in self.player_list:
            if self.is_terrorist(i):
                terrotists.append(i)
        return terrotists 

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
        msg_tantrum = self.mvp_tantrum()
        if msg_tantrum:
            return msg_tantrum
        
        msg_cc = self.mvp_cc_sloth()
        if msg_cc:
            return self.mvp_cc_sloth()
        return    
        
    def get_lvp(self):
        return self.get_lvp_cc_boss()
        
    ################################ MVP ################################
    
    def mvp_cc_sloth(self):
        i_players, min_cc, total_cc = Stats.get_min_value(self, self.get_cc_boss, exclude=[self.is_shroom])  
        if min_cc < 800:
            self.add_mvps(i_players)
            cc_ratio = min_cc / total_cc * 100
            mvp_names = self.players_to_string(i_players)
            if min_cc == 0:
                if len(i_players) > 1:
                    return langues["selected_language"]["SLOTH MVP 0 CC P"].format(mvp_names=mvp_names)
                return langues["selected_language"]["SLOTH MVP 0 CC S"].format(mvp_names=mvp_names)
            if len(i_players) > 1:
                return langues["selected_language"]["SLOTH MVP CC P"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
            return langues["selected_language"]["SLOTH MVP CC S"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
    
    def mvp_tantrum(self):
        i_players, max_tantrum, _ = Stats.get_max_value(self, self.get_tantrum)
        if max_tantrum > 1:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) > 1:
                return langues["selected_language"]["SLOTH MVP TANTRUM P"].format(mvp_names=mvp_names, max_tantrum=max_tantrum)
            return langues["selected_language"]["SLOTH MVP TANTRUM S"].format(mvp_names=mvp_names, max_tantrum=max_tantrum)
    
    ################################ LVP ################################
    
    

    ################################ CONDITIONS ###############################
    
    def is_shroom(self, i_player: int):
        rota = self.get_player_rotation(i_player)
        for skill in rota:
            if skill['id'] == 34408:
                return True
        return False
    
    ################################ DATA MECHAS ################################
    
    def get_tantrum(self, i_player: int):
        return self.get_mech_value(i_player, "Tantrum")

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
        self.add_mvps(i_players)
        cc_ratio = min_cc / total_cc * 100
        mvp_names = self.players_to_string(i_players)
        if min_cc == 0:
            return langues["selected_language"]["MATTHIAS MVP 0 CC"].format(mvp_names=mvp_names)
        else:
            return langues["selected_language"]["MATTHIAS MVP CC"].format(mvp_names=mvp_names, min_cc=min_cc, cc_ratio=cc_ratio)
        
    ################################ LVP ################################
            
    def lvp_cc_matthias(self):
        i_players, max_cc, total_cc = Stats.get_max_value(self, self.get_cc_total)       
        self.add_lvps(i_players)
        cc_ratio = max_cc / total_cc * 100
        lvp_names = self.players_to_string(i_players)
        return langues["selected_language"]["MATTHIAS LVP CC"].format(lvp_names=lvp_names, max_cc=max_cc, cc_ratio=cc_ratio)
    
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
        msg_tower = self.lvp_tower()
        if msg_tower:
            return msg_tower
        return self.lvp_glenna()
    
    ################################ MVP ################################
    
    def mvp_mine(self):
        i_players = self.get_mined_players()
        if i_players:
            self.add_mvps(i_players)
            mvp_names = self.players_to_string(i_players)
            if len(i_players) == 1:
                return langues["selected_language"]["ESCORT MVP MINE S"].format(mvp_names=mvp_names)
            else:
                return langues["selected_language"]["ESCORT MVP MINE P"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    def lvp_glenna(self):
        i_players, max_call, _ = Stats.get_max_value(self, self.get_glenna_call)
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        return langues["selected_language"]["ESCORT LVP GLENNA"].format(lvp_names=lvp_names)
    
    def lvp_tower(self):
        towers = self.get_towers()
        lvp_names = self.players_to_string(towers)
        for i in self.player_list:
            for n in range(1,6):
                if self.is_tower_n(i,n) and not self.is_tower(i):
                    return
        self.add_lvps(towers)
        if len(towers) == 1:
            return langues["selected_language"]["ESCORT LVP TOWER S"].format(lvp_names=lvp_names)
        return langues["selected_language"]["ESCORT LVP TOWER P"].format(lvp_names=lvp_names)
    
    ################################ CONDITIONS ################################
    
    def got_mined(self, i_player: int):
        return self.get_mech_value(i_player, "Mine Detonation Hit") > 0
    
    def is_tower_n(self, i_player: int, n: int):
        poses = self.get_player_pos(i_player)
        tower = globals()[f"escort_tower{n}"]
        for pos in poses:
            if get_dist(pos, tower) < tower_radius:
                return True
        return False
    
    def is_tower(self, i_player: int):
        for n in range(1,6):
            if not self.is_tower_n(i_player, n):
                return False
        return True

    ################################ DATA MECHAS ################################
    
    def get_mined_players(self):
        p = []
        for i in self.player_list:
            if self.got_mined(i):
                p.append(i)
        return p
            
    def get_glenna_call(self, i_player: int):
        return self.get_mech_value(i_player, "Over Here! Cast")
    
    def get_towers(self):
        towers = []
        for i in self.player_list:
            if self.is_tower(i):
                towers.append(i)
        return towers

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
        return self.lvp_orb_kc()
        
    ################################ MVP ################################
            
    def mvp_orb_kc(self):
        i_players, min_orb, _ = Stats.get_min_value(self, self.get_good_orb)
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if min_orb == 0:
            return langues["selected_language"]["KC MVP ORB 0"].format(mvp_names=mvp_names)
        else:
            return langues["selected_language"]["KC MVP ORB"].format(mvp_names=mvp_names, min_orb=min_orb)
            
    ################################ LVP ################################
    
    def lvp_orb_kc(self):
        i_players, max_orb, _ = Stats.get_max_value(self, self.get_good_orb)
        lvp_names = self.players_to_string(i_players)
        self.add_lvps(i_players)
        return langues["selected_language"]["KC LVP ORB"].format(lvp_names=lvp_names, max_orb=max_orb)
    
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
        self.add_mvps(i_fdp)
        if len(i_fdp) == 1:
            return langues["selected_language"]["XERA MVP SKIP S"].format(fdp_names=fdp_names)
        if len(i_fdp) > 1:
            return langues["selected_language"]["XERA MVP SKIP P"].format(fdp_names=fdp_names)
        return
    
    def mvp_glide(self):
        i_glide = self.get_gliding_death()
        glide_names = self.players_to_string(i_glide)
        self.add_mvps(i_glide)
        if len(i_glide) == 1:
            return langues["selected_language"]["XERA MVP GLIDE S"].format(glide_names=glide_names)
        if len(i_glide) > 1:
            return langues["selected_language"]["XERA MVP GLIDE P"].format(glide_names=glide_names)
        return
    
    ################################ LVP ################################
    
    def lvp_minijeu(self):
        i_players, max_minijeu, _ = Stats.get_max_value(self, self.get_tp_back, exclude=[self.is_fdp])
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        if max_minijeu == 2:
            return langues["selected_language"]["XERA LVP MINI-JEU"].format(lvp_names=lvp_names)
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
            pos_player = self.get_player_pos(i_player, i_time, i_time + i_delta)
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
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        
        msg_tp = self.mvp_tp()
        if msg_tp:
            return msg_tp
        return          
    
    def get_lvp(self):
        return self.get_lvp_dps()
      
    ################################ MVP ################################
    
    def mvp_tp(self):
        i_players, max_tp, _ = Stats.get_max_value(self, self.get_tp)
        mvp_names = self.players_to_string(i_players)
        if max_tp > 1:
            self.add_mvps(i_players)
            if len(i_players) == 1:
                return langues["selected_language"]["CAIRN MVP TP S"].format(mvp_names=mvp_names, max_tp=max_tp)
            if len(i_players) > 1:
                return langues["selected_language"]["CAIRN MVP TP P"].format(mvp_names=mvp_names, max_tp=max_tp)
        return
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    def get_tp(self, i_player: int):
        return self.get_mech_value(i_player, 'Orange TP')

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
        msg_pic = self.mvp_pic()
        if msg_pic:
            return msg_pic
        return self.get_bad_dps()
    
    def get_lvp(self):
        return self.get_lvp_dps()   
        
    ################################ MVP ################################
    
    def mvp_pic(self):
        i_players = self.get_piced()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if len(i_players) == 1:
            return langues["selected_language"]["MO MVP PICS S"].format(mvp_names=mvp_names) 
        if len(i_players) > 1:
            return langues["selected_language"]["MO MVP PICS P"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    def get_piced(self):
        piced = []
        for i in self.player_list:
            if self.is_dead_instant(i):
                piced.append(i)
        return piced

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
        
        msg_bisou = self.mvp_traitors()
        if msg_bisou:
            return msg_bisou
        
        return self.get_mvp_cc_boss(extra_exclude=[self.is_fix])
    
    def get_lvp(self):
        return self.get_lvp_cc_boss()
    
    ################################ MVP ################################ 
    
    def mvp_impaled(self):
        i_players = self.get_impaled()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if len(i_players) == 1:
            return langues["selected_language"]["SAMAROG MVP IMPALED S"].format(mvp_names=mvp_names) 
        if len(i_players) > 1:
            return langues["selected_language"]["SAMAROG MVP IMPALED P"].format(mvp_names=mvp_names)
        return 
    
    def mvp_traitors(self):
        i_trait, i_vict = self.get_traitors()
        trait_names = self.players_to_string(i_trait)
        vict_names = self.players_to_string(i_vict)
        self.add_mvps(i_trait)
        if len(i_trait) == 1:
            return langues["selected_language"]["SAMAROG MVP BISOU S"].format(trait_names=trait_names, vict_names=vict_names)
        if len(i_trait) > 1:
            return langues["selected_language"]["SAMAROG MVP BISOU P"].format(trait_names=trait_names, vict_names=vict_names)
        return  
    
    ################################ LVP ################################ 
    
    
    
    ################################ CONDITIONS ################################
    
    def got_impaled(self, i_player: int):
        if self.is_dead_instant(i_player):
            mech_history = self.get_player_mech_history(i_player)
            for mech in mech_history:
                if mech['name'] == "DC":
                    mech_history.remove(mech)
            if len(mech_history) > 1:
                if (mech_history[-2]['name'] == "Swp" or mech_history[-2]['name'] == "Schk.Wv") and mech_history[-1]['name'] == "Dead":
                    return True
        return False
    
    def is_fix(self, i_player: int):
        return self.get_mech_value(i_player, "Fixate: Samarog") >= 3
    
    ################################ DATA MECHAS ################################
    
    def get_impaled(self):
        i_players = []
        for i in self.player_list:
            if self.got_impaled(i):
                  i_players.append(i)
        return i_players
    
    def get_traitors(self):
        traitors, victims = [], []
        big_greens = self.get_mechanic_history("Big Green")
        small_greens = self.get_mechanic_history("Small Green")
        for s, b in zip(small_greens, big_greens):
            i_s, i_b = self.get_player_id(s['actor']), self.get_player_id(b['actor'])
            kiss_time = b['time']+6000
            i_kiss = time_to_index(kiss_time)
            try:
                s_pos = self.get_player_pos(i_s)[i_kiss]
                b_pos = self.get_player_pos(i_b)[i_kiss]
            except:
                continue
            if get_dist(s_pos, b_pos)*samarog_scaler > 80:
                if i_b not in victims:
                    victims.append(i_b)
                if i_s not in traitors:
                    traitors.append(i_s)
        return traitors, victims

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
        msg_pizza = self.mvp_pizza()
        if msg_pizza:
            return msg_pizza
        return
    
    def get_lvp(self):
        msg_tears = self.lvp_tears()
        if msg_tears:
            return msg_tears
        return self.get_lvp_dps()

    ################################ MVP ################################
    
    def mvp_black(self):
        i_players, max_black, _ = Stats.get_max_value(self, self.get_black_trigger)
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        nb_players = len(i_players)
        if nb_players == 1:
            return langues["selected_language"]["DEIMOS MVP BLACK S"].format(mvp_names=mvp_names, max_black=max_black)
        if nb_players > 1:
            return langues["selected_language"]["DEIMOS MVP BLACK P"].format(mvp_names=mvp_names, max_black=max_black)
        return
    
    def mvp_pizza(self):
        i_players = self.get_pizzaed()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return langues["selected_language"]["DEIMOS MVP PIZZA"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################ 
    
    def lvp_tears(self):
        i_players, max_tears, _ = Stats.get_max_value(self, self.get_tears)
        lvp_names = self.players_to_string(i_players)
        if i_players and max_tears > 2:
            self.add_lvps(i_players)
            return langues["selected_language"]["DEIMOS LVP TEARS"].format(lvp_names=lvp_names, max_tears=max_tears)
        return
    
    ################################ CONDITIONS ################################
    
    def got_pizzaed(self, i_player: int):
        if self.is_dead_instant(i_player):
            mech_history = self.get_player_mech_history(i_player)
            for mech in mech_history:
                if mech['name'] == "DC":
                    mech_history.remove(mech)
            if mech_history[-2]['name'] == "Pizza" and mech_history[-1]['name'] == "Dead":
                return True
        return False
            
    
    ################################ DATA MECHAS ################################

    def get_black_trigger(self, i_player: int):
        return self.get_mech_value(i_player, "Black Oil Trigger")
    
    def get_tears(self, i_player: int):
        return self.get_mech_value(i_player, "Tear")
    
    def get_pizzaed(self):
        pizzaed = []
        for i in self.player_list:
            if self.got_pizzaed(i):
                pizzaed.append(i)
        return pizzaed

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
        msg_wall = self.mvp_wall()
        if msg_wall:
            return msg_wall
        msg_fall = self.mvp_fall()
        if msg_fall:
            return msg_fall
        return self.get_mvp_cc_boss()
    
    def get_lvp(self):
        return self.get_lvp_cc_boss()
        
    ################################ MVP ################################
    
    def mvp_wall(self):
        i_players = self.get_walled_players()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return langues["selected_language"]["SH MVP WALL"].format(mvp_names=mvp_names)
        return
    
    def mvp_fall(self):
        i_players = self.get_walled_players()
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if i_players:
            return langues["selected_language"]["SH MVP FALL"].format(mvp_names=mvp_names)
        return
    
    ################################ LVP ################################
    
    
    
    ################################ CONDITIONS ################################
    
    def took_wall(self, i_player: int):
        if self.is_dead_instant(i_player) and not self.has_fallen(i_player):
            return True
        return False
        
    def has_fallen(self, i_player: int):
        if self.is_dead_instant(i_player):
            last_pos = self.get_player_pos(i_player)[-1]
            death_time = self.get_player_death_timer(i_player)
            fell_at_begin = get_dist(sh_center_arena, last_pos) > sh_radius2
            fell_to_radius23 = death_time > self.bosshp_to_time(90)+2500 and death_time < self.bosshp_to_time(66)+2500 and get_dist(sh_center_arena, last_pos) > sh_radius3
            fell_to_radius34 = death_time > self.bosshp_to_time(66)+2500 and death_time < self.bosshp_to_time(33)+2500 and get_dist(sh_center_arena, last_pos) > sh_radius4
            fell_to_radius45 = death_time > self.bosshp_to_time(33)+2500 and get_dist(sh_center_arena, last_pos) > sh_radius5
            if fell_at_begin or fell_to_radius23 or fell_to_radius34 or (self.cm and fell_to_radius45):
                return True
        return False
    
    ################################ DATA MECHAS ################################

    def get_walled_players(self):
        walled = []
        for i in self.player_list:
            if self.took_wall(i):
                walled.append(i)
        return walled
    
    def get_fallen_players(self):
        fallen = []
        for i in self.player_list:
            if self.has_fallen(i):
                fallen.append(i)
        return fallen

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
        return self.get_lvp_dps()
   
    ################################ MVP ################################
    
    def mvp_cracks(self):
        i_players, max_cracks, _ = Stats.get_max_value(self, self.get_cracks)
        mvp_names = self.players_to_string(i_players)
        self.add_mvps(i_players)
        if len(i_players) == 1:
            return langues["selected_language"]["DHUUM MVP CRACKS S"].format(mvp_names=mvp_names, max_cracks=max_cracks)
        if len(i_players) > 1:
            return langues["selected_language"]["DHUUM MVP CRACKS P"].format(mvp_names=mvp_names, max_cracks=max_cracks)
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
        self.add_mvps(i_players)
        if len(i_players) == 1:
            return langues["selected_language"]["LARGOS MVP DASH S"].format(mvp_names=mvp_names, max_dash=max_dash)
        if len(i_players) > 1:
            return langues["selected_language"]["LARGOS MVP DASH P"].format(mvp_names=mvp_names, max_dash=max_dash)
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
        return self.get_lvp_dps()
        
    ################################ MVP ################################
    
    def mvp_fdp(self):
        i_players = self.get_fdp()
        self.add_mvps(i_players)
        fdp_names = self.players_to_string(i_players)
        if len(i_players) == 1:
            return langues["selected_language"]["QADIM MVP PYRE S"].format(fdp_names=fdp_names)
        if len(i_players) > 1:
            return langues["selected_language"]["QADIM MVP PYRE P"].format(fdp_names=fdp_names)
    
    def mvp_wave(self):
        i_players, max_waves, _ = Stats.get_max_value(self, self.get_wave)
        self.add_mvps(i_players)
        mvp_names = self.players_to_string(i_players)
        if len(i_players) == 1:
            return langues["selected_language"]["QADIM MVP WAVE S"].format(mvp_names=mvp_names, max_waves=max_waves)
        if len(i_players) > 1:
            return langues["selected_language"]["QADIM MVP WAVE P"].format(mvp_names=mvp_names, max_waves=max_waves)
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
                pos_p1 = self.get_player_pos(i, start=start_p1, end=end_p1)
                pos_p2 = self.get_player_pos(i, start=start_p2, end=end_p2)
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
        self.add_mvps(i_players)
        mvp_names = self.players_to_string(i_players)
        dmg_ratio = min_dmg / total_dmg * 100
        return langues["selected_language"]["ADINA MVP SPLIT"].format(mvp_names=mvp_names, dmg_ratio=dmg_ratio)
    
    ################################ LVP ################################    
    
    def lvp_dmg_split(self):
        i_players, max_dmg, total_dmg = Stats.get_max_value(self, self.get_dmg_split)
        self.add_lvps(i_players)
        lvp_names = self.players_to_string(i_players)
        dmg_ratio = max_dmg / total_dmg * 100
        return langues["selected_language"]["ADINA LVP SPLIT"].format(lvp_names=lvp_names, dmg_ratio=dmg_ratio)
    
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
        msg_cc = self.get_mvp_cc_total(extra_exclude=[self.is_pylon])
        if msg_cc:
            return msg_cc
        return
    
    def get_lvp(self):
        msg_cc = self.get_lvp_cc_total()
        if msg_cc:
            return msg_cc
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
