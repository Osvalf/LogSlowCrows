from urllib.request import Request, urlopen
import json
import requests
from func import*

class Log:
    def __init__(self, url: str):
        self.url = url
        self.content = self.get_html()
        self.jcontent = self.get_parsed_json()
        self.pjcontent = self.get_json()
        BossFactory.create_boss(self)

    def get_html(self):        # url convertie en string contenant les infos en javascript
        with requests.Session() as session:
            html = session.get(self.url).content.decode("utf-8")
        return html

    def get_parsed_json(self):     # javascript converti en json
        cont = self.content.split('var _logData = ')[1].split('var logData = _logData;')[0].rsplit(';', 1)[0].strip()
        jcont = json.loads(cont)
        return jcont
    
    def get_json(self):
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
                   "qpeer": QTP}
        
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
        
    ################################ Fonction pour attribus Boss ################################
    
    def is_cm(self):
        return self.log.pjcontent['isCM']
    
    def get_logName(self):
        return self.log.pjcontent['fightName']
    
    def get_mechanics(self):
        mechs = []
        for i in self.log.jcontent['mechanicMap']:
            if i['playerMech']:
                mechs.append(i)
        return mechs
    
    def get_duration_ms(self):
        return self.log.pjcontent['durationMS']
    
    def get_start_date(self):
        s = self.log.pjcontent['timeStartStd']
        date_format = "%Y-%m-%d %H:%M:%S %z"
        start_date = datetime.strptime(s, date_format)
        paris_timezone = timezone(timedelta(hours=1))
        return start_date.astimezone(paris_timezone)
    
    def get_end_date(self):
        s = self.log.pjcontent['timeEndStd']
        date_format = "%Y-%m-%d %H:%M:%S %z"
        start_date = datetime.strptime(s, date_format)
        paris_timezone = timezone(timedelta(hours=1))
        return start_date.astimezone(paris_timezone)

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
        for i, e in enumerate(players):
            if e['group'] < 50 and not self.is_buyer(i):
                real_players.append(i)
        return real_players
            
    ################################ CONDITIONS ################################
        
    def is_quick(self, i_player: int):
        player_quick_contrib = self.log.jcontent['phases'][0]['boonGenGroupStats'][i_player]['data'][2]
        return player_quick_contrib[0]>=20 or player_quick_contrib[1]>=20

    def is_alac(self, i_player: int):
        player_alac_contrib = self.log.jcontent['phases'][0]['boonGenGroupStats'][i_player]['data'][3]
        return player_alac_contrib[0]>=20 or player_alac_contrib[1]>=20
    
    def is_support(self, i_player: int):
        return self.is_quick(i_player) or self.is_alac(i_player)
    
    def is_dps(self, i_player: int):
        return not self.is_support(i_player)
    
    def is_tank(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['toughness']>0
    
    def is_heal(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['healing']>0
    
    def is_dead(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['defenses'][0]['deadCount']>0
    
    def is_buyer(self, i_player: int):
        i_death = None
        mechanics = self.log.pjcontent['mechanics']
        for i, e in enumerate(mechanics):
            if e['name'] == "Dead":
                i_death = i
                break
        if i_death != None:
            for e in mechanics[i_death]['mechanicsData']:
                if e['time'] < 20000 and e['actor'] == self.get_player_name(i_player):
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
        for e in players:
            if e['name'] == name:
                return players.index(e)
        return None
    
    def get_mvp_cc(self):
        p, v, t = Stats.get_min_value(self, self.get_cc_boss)
        for e in p:
            all_mvp.append(self.get_player_account(e))
        s = ', '.join(list(map(self.get_player_name, p)))
        r = v / t * 100
        if v == 0:
            if len(p) == 1:
                return f" * *[**MVP** : {s} n'a pas mis de **CC**]*"
            else:
                return f" * *[**MVP** : {s} n'ont pas mis de **CC**]*"
        else:
            if len(p) == 1:
                return f" * *[**MVP** : {s} n'a mis que **{v:.0f}** de **CC** (**{r:.1f}%** de la squad)]*"
            else:
                return f" * *[**MVP** : {s} n'ont mis que **{v:.0f}** de **CC** (**{r:.1f}%** de la squad)]*"
            
    def get_lvp_cc(self):
        p, v, t = Stats.get_max_value(self, self.get_cc_boss)
        for e in p:
            all_lvp.append(self.get_player_account(e))
        s = ', '.join(list(map(self.get_player_name, p)))
        r = v / t * 100
        return f" * *[**LVP** : {s} merci d'avoir fait **{v:.0f}** de **CC** (**{r:.1f}%** de la squad)]*"
    
    def get_bad_dps(self):
        i_sup, sup_max_dmg, _ = Stats.get_max_value(self, self.get_dmg_boss, exclude=[self.is_dps])
        i_dps, dps_min_dmg, tot_dmg = Stats.get_min_value(self, self.get_dmg_boss, exclude=[self.is_support, self.is_dead])
        if dps_min_dmg < sup_max_dmg:
            all_mvp.append(self.get_player_account(i_dps[0]))
            sup = self.get_player_name(i_sup[0])
            s = ', '.join(list(map(self.get_player_name, i_dps)))
            r = (1 - dps_min_dmg / sup_max_dmg) * 100 
            return f" * *[**MVP** : {s} qui en **DPS** n'a fait que **{dps_min_dmg / self.duration_ms :.1f}kdps** soit **{r:.1f}%** de moins que {sup} qui joue **support** on le rappelle]*"
        return None
    
    def get_lvp_dps(self):
        p, v, t = Stats.get_max_value(self, self.get_dmg_boss)
        for e in p:
            all_lvp.append(self.get_player_account(e))
        r = v / t * 100
        s = ', '.join(list(map(self.get_player_name, p)))
        return f" * *[**LVP** : {s} qui a fait **{v / self.duration_ms:.1f}kdps** (**{r:.0f}%** de la squad)]*"
    
    ################################ DATA BOSS ################################
    
    def get_pos_boss(self, start: int = 0, end: int = None):
        targets = self.log.pjcontent['targets']
        for e in targets:
            if e['id'] in boss_dict.keys():
                return e['combatReplayData']['positions'][start:end]
        raise ValueError('No Boss in targets')
    
    def get_phase_id(self, phase: str):
        phases = self.log.pjcontent['phases']
        for e in phases:
            if e['name'] == phase:
                start = time_to_index(e['start'])
                end = time_to_index(e['end'])
                return start, end
        raise ValueError('{phase} not found')
    
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
        
    ################################ MVP / LVP ################################   
        
    def get_mvp(self):
        p, v, t = Stats.get_max_value(self, self.get_bleu)
        s = ', '.join(list(map(self.get_player_name, p)))
        if v != 0:
            for e in p:
                all_mvp.append(self.get_player_account(e))
            if len(p)>1:
                return f" * *[**MVP** : {s} se sont tous les {len(p)} pris **{v}** **bleues**]*"
            else:
                return f" * *[**MVP** : {s} s'est pris **{v}** **bleues**]*"
        return 
    
    def get_lvp(self):
        return 

    ################################ CONDITIONS ###############################
    
    
    
    ################################ DATA MECHAS ################################
    
    def get_bleu(self, i_player: int):
        bleu = 0
        mechs_list = [mech['name'] for mech in self.mechanics]
        if "Green Guard TP" in mechs_list:
            i_tp = mechs_list.index("Green Guard TP")
            bleu += self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_tp][0]
        if "Boss TP" in mechs_list:
            i_tp = mechs_list.index("Boss TP")
            bleu += self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_tp][0]
        return bleu

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
        
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        p, v, t = Stats.get_min_value(self, self.get_dmg_split, exclude=[self.is_support])
        for e in p:
            all_mvp.append(self.get_player_account(e))
        s = ', '.join(list(map(self.get_player_name, p)))
        r = v / t * 100
        return f" * *[**MVP** : {s} avec seulement **{r:.1f}%** des degats sur **split** en **DPS**]*"
    
    def get_lvp(self):
        p, v, t = Stats.get_max_value(self, self.get_dmg_split)
        for e in p:
            all_lvp.append(self.get_player_account(e))
        s = ', '.join(list(map(self.get_player_name, p)))
        r = v / t * 100
        return f" * *[**LVP** : {s} avec **{r:.1f}%** des degats sur **split** en **DPS**]*"

    ################################ CONDITIONS ###############################
    
    
    
    ################################ DATA MECHAS ################################
        
    def get_dmg_split(self, i_player: int):
        jlog = self.log.jcontent
        dmg = 0
        dmg_split_1 = jlog['phases'][3]['dpsStatsTargets'][i_player]
        dmg_split_2 = jlog['phases'][6]['dpsStatsTargets'][i_player]
        for i in range(len(dmg_split_1)):
            dmg += dmg_split_1[i][0] + dmg_split_2[i][0]
        return dmg
    
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
    
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        total_dmg_split = Stats.get_tot_value(self, self.get_dmg_split)
        p, v, t = Stats.get_min_value(self, self.get_dmg_split, exclude=[self.is_support,self.is_cannon])
        for e in p:
            all_mvp.append(self.get_player_account(e))
        v = v / t * 100
        s = ', '.join(list(map(self.get_player_name, p)))
        return f" * *[**MVP** : {s} avec seulement **{v:.1f}%** des degats sur **split** sans faire de **canon**]*"
    
    def get_lvp(self):
        p, v, t = Stats.get_max_value(self, self.get_dmg_split)
        for e in p:
            all_lvp.append(self.get_player_account(e))
        s = ', '.join(list(map(self.get_player_name, p)))
        r = v / t * 100
        return f" * *[**LVP** : {s} avec **{r:.1f}%** des degats sur **split** en **DPS**]*"

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
        for e in pos_player:
            for canon in canon_pos:
                if get_dist(e, canon) <= canon_detect_radius:
                    return True
        return False
    
    ################################ DATA MECHAS ################################
        
    def get_dmg_split(self,i_player: int):
        jlog = self.log.jcontent
        dmg = 0
        dmg_kernan = jlog['phases'][2]['dpsStatsTargets'][i_player][0][0]
        dmg_mornifle = jlog['phases'][5]['dpsStatsTargets'][i_player][0][0]
        dmg_karde = jlog['phases'][7]['dpsStatsTargets'][i_player][0][0]
        dmg += dmg_kernan + dmg_mornifle + dmg_karde
        return dmg  

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
        
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        p, v, t = Stats.get_min_value(self, self.get_cc_boss, exclude=[self.is_shroom])
        for e in p:
            all_mvp.append(self.get_player_account(e))
        r = v / t * 100
        s = ', '.join(list(map(self.get_player_name, p)))
        if v == 0:
            if len(p)>1:
                return f" * *[**MVP** : {s} qui n'ont même pas **CC** sans manger de **shroom**]*"
            return f" * *[**MVP** : {s} qui n'a même pas **CC** sans manger de **shroom**]*"
        if len(p)>1:
            return f" * *[**MVP** : {s} qui ont fait seulement **{v:.0f}** de **CC** (**{r:.1f}%** du total) sans manger de **shroom**]*"
        return f" * *[**MVP** : {s} qui a fait seulement **{v:.0f}** de **CC** (**{r:.1f}%** du total) sans manger de **shroom**]*"
    
    def get_lvp(self):
        return self.get_lvp_cc()

    ################################ CONDITIONS ###############################
    
    def is_shroom(self, i_player: int):
        mechs_list = [mech['name'] for mech in self.mechanics]
        mech = "Slub"
        if mech in mechs_list:
            i_mech = mechs_list.index(mech)
            return self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_mech]>0
        return False
    
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
          
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        total_cc_boss = Stats.get_tot_value(self, self.get_cc_total)
        p, v, t = Stats.get_min_value(self, self.get_cc_total, exclude=[self.is_sac])
        for e in p:
            all_mvp.append(self.get_player_account(e))
        r = v / total_cc_boss * 100
        s = ', '.join(list(map(self.get_player_name, p)))
        if v == 0:
            if len(p)>1:
                return f" * *[**MVP** : {s} qui n'ont même pas **CC** sans s'être **sacrifié**]*"
            else:
                return f" * *[**MVP** : {s} qui n'a même pas **CC** sans s'être **sacrifié**]*"
        elif len(p)>1:
            return f" * *[**MVP** : {s} qui ont fait seulement **{v:.0f}** de **CC** (**{r:.1f}%** du total) sans s'être sacrifié]*"
        return f" * *[**MVP** : {s} qui a fait seulement **{v:.0f}** de **CC** (**{r:.1f}%** du total) sans s'être sacrifié]*"
    
    def get_lvp(self):
        p, v, t = Stats.get_max_value(self, self.get_cc_total)       
        for e in p:
            all_lvp.append(self.get_player_account(e))
        r = v / t * 100
        s = ', '.join(list(map(self.get_player_name, p)))
        return f" * *[**LVP** : {s} merci d'avoir mis **{v:.0f}** de **CC** (**{r:.1f}%** de la squad)]*"
            
        

    ################################ CONDITIONS ###############################
    
    def is_sac(self, i_player: int):
        return self.get_nb_sac(i_player)>0
    
    ################################ DATA MECHAS ################################    
    
    def get_nb_sac(self, i_player: int):
        mechs_list = [mech['name'] for mech in self.mechanics]
        mech = "Sacrifice"
        if mech in mechs_list:
            i_mech = mechs_list.index(mech)
            return self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_mech][0]
        return 0 

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
       
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        p = self.get_mined_players()
        s = ', '.join(list(map(self.get_player_name, p)))
        if p:
            for e in p:
                all_mvp.append(self.get_player_account(e))
            if len(p)==1:
                return f" * *[**MVP** : {s} qui a bien **profité** de l'escort en prenant une **mine**]*"
            else:
                return f" * *[**MVP** : {s} qui ont bien **profité** de l'escort en prenant une **mine**]*"
        return 
    
    def get_lvp(self):
        p, v, t = Stats.get_max_value(self, self.get_glenna_call)
        for e in p:
            all_lvp.append(self.get_player_account(e))
        s = ', '.join(list(map(self.get_player_name, p)))
        return f" * *[**LVP** : {s}, merci d'avoir **call** glenna **{v}** fois]*"
    
    ################################ CONDITIONS ################################
    
    def is_mined(self, i_player: int):
        mechs_list = [mech['name'] for mech in self.mechanics]
        mech = "Mine Detonation Hit"
        if mech in mechs_list:
            i_mech = mechs_list.index(mech)
            return self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_mech][0]>0
        return False
    
    ################################ DATA MECHAS ################################
    
    def get_mined_players(self):
        p = []
        nb_players = len(self.log.jcontent['players'])
        for i in range(nb_players):
            if self.is_mined(i):
                p.append(i)
        return p
    
    def get_glenna_call(self, i_player: int):
        mechs_list = [mech['name'] for mech in self.mechanics]
        mech = "Over Here! Cast"
        if mech in mechs_list:
            i_mech = mechs_list.index(mech)
            return self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_mech][0]
        return 0
            


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
        
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        p, v, t = Stats.get_min_value(self, self.get_good_orb)
        s = ', '.join(list(map(self.get_player_name, p)))
        for e in p:
            all_mvp.append(self.get_player_account(e))
        if v == 0:
            if len(p)==1:
                return f" * *[**MVP** : {s} qui n'a pas collecté d'**orbe** sur tout le fight]*"
            else:
                return f" * *[**MVP** : {s} qui n'ont pas collecté d'**orbe** sur tout le fight]*"
        else:
            if len(p)==1:
                return f" * *[**MVP** : {s} qui n'a collecté que **{v}** orbes sur tout le fight]*"
            else:
                return f" * *[**MVP** : {s} qui n'ont collecté que **{v}** orbes sur tout le fight]*"
    
    def get_lvp(self):
        return 
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    def get_good_orb(self, i_player: int):
        mechs_list = [mech['name'] for mech in self.mechanics]
        i_r = mechs_list.index('Good Red Orb')
        i_w = mechs_list.index('Good White Orb')
        return self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_r][0] + self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_w][0]

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
        
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        fdp = self.get_fdp()
        s = ', '.join(list(map(self.get_player_name, fdp)))
        for e in fdp:
            all_mvp.append(self.get_player_account(e))
        if len(fdp) == 1:
            return f" * *[**MVP** : oui {s} a vraiment **skip** un **mini-jeu**]*"
        elif fdp:
            return f" * *[**MVP** : oui {s} ont vraiment **skip** un **mini-jeu**]*"
        glide = self.get_gliding_death()
        s = ', '.join(list(map(self.get_player_name, glide)))
        for e in glide:
            all_mvp.append(self.get_player_account(e))
        if len(glide) == 1:
            return f" * *[**MVP** : {s} champion **mort** pendant le **glide**]*"
        elif glide:
            return f" * *[**MVP** : {s} champions **morts** pendant le **glide**]*"
        return self.get_mvp_cc() 
    
    def get_lvp(self):
        p, v, t = Stats.get_max_value(self, self.get_tp_back, exclude=[self.is_fdp])
        for e in p:
            all_lvp.append(self.get_player_account(e))
        s = ', '.join(list(map(self.get_player_name, p)))
        if v == 2:
            return f" * *[**LVP** : {s} merci d'avoir tanké **2** mini-jeu sans les skip]*"
        return self.get_lvp_cc()
    
    ################################ CONDITIONS ################################
    
    def is_fdp(self, i_player: int):
        return i_player in self.get_fdp()
    
    ################################ DATA MECHAS ################################

    def get_tp_out(self, i_player: int):
        mechs_list = [mech['name'] for mech in self.mechanics]
        i_tp = mechs_list.index('TP')
        return self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_tp][0]
    
    def get_tp_back(self, i_player: int):
        mechs_list = [mech['name'] for mech in self.mechanics]
        i_tp = mechs_list.index('TP back')
        return self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_tp][0]
    
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
            i_player = self.get_player_id(e['actor'])
            time = e['time']+1000 # 1s de delais pour etre sur
            i_time = time_to_index(time)
            pos_player = self.get_pos_player(i_player, i_time, i_time + i_delta)
            for p in pos_player:
                if get_dist(p, xera_centre) <= xera_centre_radius:
                    fdp.append(i_player)
                    break
        return fdp
    
    def get_gliding_death(self):
        dead = []
        for i in range(10):
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
      
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        s = self.get_bad_dps()
        if s:
            return s   
        return 
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
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
        
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        s = self.get_bad_dps()
        if s:
            return s   
        return 
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
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
    
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        p = self.get_impaled()
        for e in p:
            all_mvp.append(self.get_player_account(e))
        if len(p) == 1:
            s = ', '.join(list(map(self.get_player_name, p)))
            return f" * *[**MVP** : {s} s'est fait **empaler**, gros respect]*" 
        if len(p) > 1:
            s = ', '.join(list(map(self.get_player_name, p)))
            return f" * *[**MVP** : {s} se sont fait **empaler**, gros respect]*"
        return self.get_mvp_cc() 
    
    def get_lvp(self):
        return self.get_lvp_cc()
    
    ################################ CONDITIONS ################################
    
    def is_impaled(self, i_player: int):
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
    
    ################################ DATA MECHAS ################################

    @staticmethod
    def get_sama_cartesian(corner1: list[float,float], corner2: list[float,float]):
        a = corner2[1] - corner1[1]
        b = corner1[0] - corner2[0]
        c = - a * corner1[0] - b * corner1[1]
        return a, b, c  
    
    def get_impaled(self):
        p = []
        for i in range(10):
            if self.is_impaled(i):
                  p.append(i)
        return p

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

    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        p, v, _ = Stats.get_max_value(self, self.get_black_trigger)
        if v != 0:
            for e in p:
                all_mvp.append(self.get_player_account(e))
            if len(p) == 1:
                s = ', '.join(list(map(self.get_player_name, p)))
                return f" * *[**MVP** : {s} merci à ce **champion** d'avoir trigger **{v} black**]*"
            if len(p) > 1:
                s = ', '.join(list(map(self.get_player_name, p)))
                return f" * *[**MVP** : {s} merci à ces **champions** d'avoir tous les {len(p)} trigger **{v} black**]*"
        return 
    
    def get_lvp(self):
        p, v, _ = Stats.get_max_value(self, self.get_tears)
        for e in p:
            all_lvp.append(self.get_player_account(e))
        s = ', '.join(list(map(self.get_player_name, p)))
        if p:
            return f" * *[**LVP** : {s} merci d'avoir ramassé **{v} tears**]*"
        return 
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    def get_black_trigger(self, i_player: int):
        mechs_list = [mech['name'] for mech in self.mechanics]
        mech = "Black Oil Trigger"
        if mech in mechs_list:
            i_black = mechs_list.index(mech)
            return self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_black][0]
        return 0
    
    def get_tears(self, i_player: int):
        mechs_list = [mech['name'] for mech in self.mechanics]
        mech = "Tear"
        if mech in mechs_list:
            i_tear = mechs_list.index(mech)
            return self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_tear][0]
        return 0

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
        
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        return self.get_mvp_cc()
    
    def get_lvp(self):
        return self.get_lvp_cc()
    
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
   
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        p, v, _ = Stats.get_max_value(self, self.get_cracks)
        s = ', '.join(list(map(self.get_player_name, p)))
        if v != 0:
            for e in p:
                all_mvp.append(self.get_player_account(e))
            if len(p) == 1:
                return f" * *[**MVP** : {s} s'est pris **{v} cracks**]*"
            if len(p) > 1:
                return f" * *[**MVP** : {s} se sont pris **{v} cracks**]*"
        return 
    
    def get_lvp(self):
        return 
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    def get_cracks(self, i_player: int):
        mechs_list = [mech['name'] for mech in self.mechanics]
        mech = "Cracks"
        if mech in mechs_list:
            i_tear = mechs_list.index(mech)
            return self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_tear][0]
        return 0    

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
  
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        s = self.get_bad_dps()
        if s:
            return s
        return 
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
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

    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        p, v, _ = Stats.get_max_value(self, self.get_dash, exclude=[self.is_heal, self.is_tank])
        s = ', '.join(list(map(self.get_player_name, p)))
        if v != 0:
            for e in p:
                all_mvp.append(self.get_player_account(e))
            if len(p) == 1:
                return f" * *[**MVP** : {s} s'est pris **{v} dash**]*"
            if len(p) > 1:
                return f" * *[**MVP** : {s} se sont pris **{v} dash**]*"
        return 
    
    def get_lvp(self):
        p, v, t = Stats.get_max_value(self, self.get_cc_total)
        for e in p:
            all_lvp.append(self.get_player_account(e))
        r = v / t * 100
        s = ', '.join(list(map(self.get_player_name, p)))
        return f" * *[**LVP** : {s} merci d'avoir fait **{v:.0f}** de **CC** (**{r:.1f}%** de la squad)]*"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    def get_dash(self, i_player: int):
        mechs_list = [mech['name'] for mech in self.mechanics]
        mech = "Vapor Rush Charge"
        if mech in mechs_list:
            i_dash = mechs_list.index(mech)
            return self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_dash][0]
        return 0 

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
        
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        p = self.get_fdp()
        s = ', '.join(list(map(self.get_player_name, p)))
        if len(p) == 1:
            return f" * *[**MVP** : {s} n'est pas allé taper le **pyre**]*"
        if len(p) > 1:
            return f" * *[**MVP** : {s} ne sont pas allé taper le **pyre**]*"
        s = self.get_bad_dps()
        if s:
            return s
        p, v, _ = Stats.get_max_value(self, self.get_wave, exclude=[self.is_quick])
        s = ', '.join(list(map(self.get_player_name, p)))
        if v != 0:
            if len(p) == 1:
                return f" * *[**MVP** : {s} s'est pris **{v} shockwave**]*"
            if len(p) > 1:
                return f" * *[**MVP** : {s} se sont pris **{v} shockwave**]*"
        return 
    
    def get_lvp(self):
        return 
    
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
                for e in pos_p1:
                    dist = get_dist(e,qadim_center)
                    if dist > qadim_fdp_radius:
                        add_fdp = False
                        break        
                for e in pos_p2:
                    dist = get_dist(e,qadim_center)
                    if dist > qadim_fdp_radius:
                        add_fdp = False
                        break 
                if add_fdp:
                    fdp.append(i)
        return fdp
    
    def get_wave(self, i_player: int):
        mechs_list = [mech['name'] for mech in self.mechanics]
        mech = "Mace Shockwave"
        if mech in mechs_list:
            i_wave = mechs_list.index(mech)
            return self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_wave][0]
        return 0

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
        
    ################################ MVP / LVP ################################

    def get_mvp(self):
        p, v, t = Stats.get_min_value(self, self.get_dmg_split, exclude=[self.is_support])
        r = v / t * 100
        s = ', '.join(list(map(self.get_player_name, p)))
        return f" * *[**MVP** : {s} n'a fait que **{r:.1f}%** des dégats sur split]*"
        
        
    def get_lvp(self):
        p, v, t = Stats.get_max_value(self, self.get_dmg_split)
        for e in p:
            all_lvp.append(self.get_player_account(e))
        r = v / t * 100
        s = ', '.join(list(map(self.get_player_name, p)))
        return f" * *[**LVP** : {s} merci d'avoir fait **{r:.1f}%** des dégats sur split]*"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################
    
    def get_dmg_split(self, i_player: int):
        path = self.log.jcontent['phases']
        dmg = 0
        dmg_split1 = path[2]['dpsStats'][i_player][0]
        dmg_split2 = path[4]['dpsStats'][i_player][0]
        dmg_split3 = path[6]['dpsStats'][i_player][0]
        dmg += dmg_split1 + dmg_split2 + dmg_split3
        return dmg

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

    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        return self.get_mvp_cc()
    
    def get_lvp(self):
        return self.get_lvp_cc()
    
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
 
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        i_sup, sup_max_dmg, _ = Stats.get_max_value(self, self.get_dmg_boss, exclude=[self.is_dps])
        i_dps, dps_min_dmg, tot_dmg = Stats.get_min_value(self, self.get_dmg_boss, exclude=[self.is_support, self.is_dead, self.is_pylon])
        if dps_min_dmg < sup_max_dmg:
            all_mvp.append(self.get_player_account(i_dps[0]))
            sup = self.get_player_name(i_sup[0])
            s = ', '.join(list(map(self.get_player_name, i_dps)))
            r = (1 - dps_min_dmg / sup_max_dmg) * 100 
            return f" * *[**MVP** : {s} qui en **DPS** n'a fait que **{dps_min_dmg / self.duration_ms :.1f}kdps** soit **{r:.1f}%** de moins que {sup} qui joue **support** on le rappelle]*"
        return 
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
    ################################ CONDITIONS ################################
    
    def is_pylon(self, i_player: int):
        return self.get_orb_caught(i_player) > 1
    
    ################################ DATA MECHAS ################################

    def get_orb_caught(self, i_player: int):
        mechs_list = [mech['name'] for mech in self.mechanics]
        mech = "Critical Mass"
        i_orb = mechs_list.index(mech)
        return self.log.jcontent['phases'][0]['mechanicStats'][i_player][i_orb][0]
