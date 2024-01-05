from urllib.request import Request, urlopen
import json
import requests
from const import*
from func import*

class Log:
    def __init__(self, url: str):
        self.url = url
        self.content = self.get_html()
        self.jcontent = self.get_parsed_json()
        self.pjcontent = self.get_json()
        BossFactory.create_boss(self)

    def get_html(self):        # url convertie en string contenant les infos en javascript
        self.wingman = "wingman" in self.url
        if(self.wingman and ("logContent" not in self.url)):
            self.url = self.url.replace("log","logContent")
        req = Request(url=self.url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urlopen(req).read()
        # Decode using UTF-8 instead of "unicode_escape"
        content = html.decode("utf-8")
        return content

    def get_parsed_json(self):     # javascript converti en json
        cont = self.content.split('var _logData = ')[1].split('var logData = _logData;')[0].rsplit(';', 1)[0].strip()
        jcont = json.loads(cont)
        return jcont
    
    def get_json(self):
        return requests.get(f"https://dps.report/getJson?permalink={self.url}").json()
    
class BossFactory:
    @staticmethod
    def create_boss(log : Log):
        boss_id = log.jcontent['triggerID']
        boss_name = boss_dict[boss_id]
        boss = None
        match boss_name:
            case "vg":
                boss = VG(log)
            case "gors":
                boss = GORS(log)
            case "sab":
                boss = SABETHA(log)
            case "sloth":
                boss = SLOTH(log)
            case "matt":
                boss = MATTHIAS(log)
            case "esc":
                boss = ESCORT(log)
            case "kc":
                boss = KC(log)
            case "xera":
                boss = XERA(log)
            case "cairn":
                boss = CAIRN(log)
            case "mo":
                boss = MO(log)
            case "sam":
                boss = SAMAROG(log)
            case "dei":
                boss = DEIMOS(log)
            case "sh":
                boss = SH(log)
            case "dhumm":
                boss = DHUUM(log)
            case "ca":
                boss = CA(log)
            case "twins":
                boss = LARGOS(log)
            case "qadim":
                boss = Q1(log)
            case "adina":
                boss = ADINA(log)
            case "sabir":
                boss = SABIR(log)
            case "qpeer":
                boss = QTP(log)
            case _:
                raise ValueError("Unknown Boss") 
        all_bosses.append(boss)

class Boss:  

    name = None
    wing = 0

    def __init__(self, log: Log):
        self.log = log
        self.cm = self.is_cm()
        self.logName = self.get_logName()
        self.mechanics = self.get_mechanics()
        
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
            
    ################################ CONDITIONS ################################
        
    def is_quick(self, i_player: int):
        player_quick_contrib = self.log.jcontent['phases'][0]['boonGenGroupStats'][i_player]['data'][2]
        return player_quick_contrib[0]>=35 or player_quick_contrib[1]>=35

    def is_alac(self, i_player: int):
        player_alac_contrib = self.log.jcontent['phases'][0]['boonGenGroupStats'][i_player]['data'][3]
        return player_alac_contrib[0]>=35 or player_alac_contrib[1]>=35
    
    def is_support(self, i_player: int):
        return self.is_quick(i_player) or self.is_alac(i_player)
    
    def is_tank(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['toughness']>0
    
    def is_heal(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['healing']>0
    
    def is_dead(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['defenses'][0]['deadCount']>0
    
    ################################ DATA JOUEUR ################################
    
    def get_player_name(self, i_player: int):
        return self.log.jcontent['players'][i_player]['name']
    
    def get_pos_player(self, i_player: int , start: int = 0, end: int = None): 
        return self.log.pjcontent['players'][i_player]['combatReplayData']['positions'][start:end]
    
    def get_cc_boss(self, i_player: int):
        return self.log.jcontent['phases'][0]['dpsStatsTargets'][i_player][0][3]
    
    def get_cc_total(self, i_player: int):
        return self.log.jcontent['phases'][0]['dpsStats'][i_player][3]
    
    def get_player_id(self, name: str):
        players = self.log.pjcontent['players']
        for e in players:
            if e['name'] == name:
                return players.index(e)
        return None
    
    ################################ DATA BOSS ################################
    
    def get_pos_boss(self, start: int = 0, end: int = None):
        targets = self.log.pjcontent['targets']
        for e in targets:
            if e['id'] in boss_dict.keys():
                return e['combatReplayData']['positions'][start:end]
        raise ValueError('No Boss in targets')
    
class Stats:
    @staticmethod
    def get_max_value(log : Log,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):

        i_max = None
        value_max = 0
        value_tot = 0
        nb_players = len(log.jcontent['players'])
        for i in range(nb_players):
            value = fnc(i)
            value_tot += value
            for filtre in exclude:
                if filtre(i):
                    break
            else:
                if value > value_max:
                    value_max = value
                    i_max = i
        i_maxs = []
        for i in range(nb_players):
            for filtre in exclude:
                if filtre(i):
                    break
            else:
                value = fnc(i)
                if value == value_max:
                    i_maxs.append(i)
        return i_maxs, value_max, value_tot
    
    @staticmethod
    def get_min_value(log : Log,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):

        i_min = None
        value_min = BIG
        value_tot = 0
        nb_players = len(log.jcontent['players'])
        for i in range(nb_players):
            value = fnc(i)
            value_tot += value
            for filtre in exclude:
                if filtre(i):
                    break
            else:
                if value < value_min:
                    value_min = value
                    i_min = i
        i_mins = []
        for i in range(nb_players):
            for filtre in exclude:
                if filtre(i):
                    break
            else:
                value = fnc(i)
                if value == value_min:
                    i_mins.append(i)
        return i_mins, value_min, value_tot

    @staticmethod
    def get_tot_value(log : Log,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):
                
        value_tot = 0
        nb_players = len(log.jcontent['players'])
        for i in range(nb_players):
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
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        VG.last = self
        
    ################################ MVP / LVP ################################   
        
    def get_mvp(self):
        p, v, t = Stats.get_max_value(self.log, self.get_bleu)
        s = ', '.join(list(map(self.get_player_name, p)))
        if len(p)>1:
            return f" * *[**MVP** : {s} se sont tous les {len(p)} pris **{v}** **bleues**]*"
        else:
            return f" * *[**MVP** : {s} s'est pris **{v}** **bleues**]*"
    
    def get_lvp(self):
        return f"LVP de {self.name}"

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
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        GORS.last = self
        
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        p, v, t = Stats.get_min_value(self.log, self.get_dmg_split, exclude=[self.is_support])
        s = ', '.join(list(map(self.get_player_name, p)))
        r = v / t * 100
        return f" * *[**MVP** : {s} avec seulement **{r:.1f}%** des degats sur **split** en DPS]*"
    
    def get_lvp(self):
        return f"LVP de {self.name}"

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
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SABETHA.last = self
    
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        total_dmg_split = Stats.get_tot_value(self.log, self.get_dmg_split)
        p, v, t = Stats.get_min_value(self.log, self.get_dmg_split, exclude=[self.is_support,self.is_cannon])
        v = v / t * 100
        s = ', '.join(list(map(self.get_player_name, p)))
        return f" * *[**MVP** : {s} avec seulement **{v:.1f}%** des degats sur **split** sans faire de **canon**]*"
    
    def get_lvp(self):
        return f"LVP de {self.name}"

    ################################ CONDITIONS ###############################
    
    def is_cannon(self, i_player: int, n: int=0):
        
        detect_radius = 45
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
                if get_dist(e, canon) <= detect_radius:
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
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SLOTH.last = self
        
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        total_cc_boss = Stats.get_tot_value(self.log, self.get_cc_boss)
        p, v, t = Stats.get_min_value(self.log, self.get_cc_boss, exclude=[self.is_shroom])
        r = v / total_cc_boss * 100
        s = ', '.join(list(map(self.get_player_name, p)))
        if len(p)>1:
            return f" * *[**MVP** : {s} qui ont fait seulement **{v:.0f}** de **CC** (**{r:.1f}%** du total) sans manger de **shroom**]*"
        return f" * *[**MVP** : {s} qui a fait seulement **{v:.0f}** de **CC** (**{r:.1f}%** du total) sans manger de **shroom**]*"
    
    def get_lvp(self):
        return f"LVP de {self.name}"

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
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        MATTHIAS.last = self
          
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        total_cc_boss = Stats.get_tot_value(self.log, self.get_cc_total)
        p, v, t = Stats.get_min_value(self.log, self.get_cc_total, exclude=[self.is_sac])
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
        return f"LVP de {self.name}"

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
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        ESCORT.last = self 
       
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        p = self.get_mined_players()
        s = ', '.join(list(map(self.get_player_name, p)))
        if len(p)>0:
            if len(p)==1:
                return f" * *[**MVP** : {s} qui a bien **profité** de l'escort en prenant une **mine**]*"
            else:
                return f" * *[**MVP** : {s} qui ont bien **profité** de l'escort en prenant une **mine**]*"
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        p, v, t = Stats.get_max_value(self.log, self.get_glenna_call)
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
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        KC.last = self  
        
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        p, v, t = Stats.get_min_value(self.log, self.get_good_orb)
        s = ', '.join(list(map(self.get_player_name, p)))
        if len(p)==1:
            return f" * *[**MVP** : {s} qui n'a collecté que **{v}** orbes sur tout le fight]*"
        else:
            return f" * *[**MVP** : {s} qui n'ont collecté que **{v}** orbes sur tout le fight]*"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
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

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        XERA.last = self  
        
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        fdp = self.get_fdp()
        s = ', '.join(list(map(self.get_player_name, fdp)))
        if len(fdp) == 1:
            return f" * *[**MVP** : {s} oui ce **fdp** a vraiment skip un **mini-jeu**]*"
        elif len(fdp) > 0:
            return f" * *[**MVP** : {s} oui ces **fdp** ont vraiment skip un **mini-jeu**]*"
        glide = self.get_gliding_death()
        s = ', '.join(list(map(self.get_player_name, glide)))
        if len(glide) == 1:
            return f" * *[**MVP** : {s} ce champion **mort** pendant le **glide**]*"
        elif len(glide) > 0:
            return f" * *[**MVP** : {s} ces champions **morts** pendant le **glide**]*"
        p, v, t = Stats.get_min_value(self.log, self.get_cc_boss)
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
    
    def get_lvp(self):
        p, v, t = Stats.get_max_value(self.log, self.get_tp_back)
        s = ', '.join(list(map(self.get_player_name, p)))
        if v == 2:
            return f" * *[**LVP** : {s} merci d'avoir tanké **2** mini-jeu sans les skip]*"
        p, v, t = Stats.get_max_value(self.log, self.get_cc_boss)
        s = ', '.join(list(map(self.get_player_name, p)))
        r = v / t * 100
        return f" * *[**LVP** : {s} merci d'avoir fait **{v:.0f}** de CC soit **{r:.1f}%** de la squad]*"
    
    ################################ CONDITIONS ################################
    
    
    
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
            if self.is_dead(i):
                if self.log.pjcontent['players'][i]['defenses'][5]['deadCount'] > 0:
                    dead.append(i)
        return dead
    
    
        

################################ CAIRN ################################

class CAIRN(Boss):
    
    last = None
    name = "CAIRN"
    wing = 4
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        CAIRN.last = self
      
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

################################ MO ################################

class MO(Boss):
    
    last = None
    name = "MO"
    wing = 4
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        MO.last = self   
        
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

################################ SAMAROG ################################

class SAMAROG(Boss):
    
    last = None
    name = "SAMAROG"
    wing = 4
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SAMAROG.last = self
    
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

################################ DEIMOS ################################

class DEIMOS(Boss):
    
    last = None
    name = "DEIMOS"
    wing = 4
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        DEIMOS.last = self

    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

################################ SH ################################

class SH(Boss):
    
    last = None
    name = "SH"
    wing = 5
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SH.last = self
        
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

################################ DHUUM ################################

class DHUUM(Boss):
    
    last = None
    name = "DHUUM"
    wing = 5
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        DHUUM.last = self
   
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

################################ CA ################################

class CA(Boss):
    
    last = None
    name = "CA"
    wing = 6

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        CA.last = self
  
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

################################ LARGOS ################################

class LARGOS(Boss):
    
    last = None
    name = "LARGOS"
    wing = 6
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        LARGOS.last = self

    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

################################ QADIM ################################

class Q1(Boss):
    
    last = None
    name = "QUOIDIMM"
    wing = 6

    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        Q1.last = self
        
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

################################ ADINA ################################

class ADINA(Boss):
    
    last = None
    name = "ADINA"
    wing = 7
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        ADINA.last = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ SABIR ################################

class SABIR(Boss):
    
    last = None
    name = "SABIR"
    wing = 7
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SABIR.last = self

    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

################################ QTP ################################

class QTP(Boss):
    
    last = None
    name = "QTP"
    wing = 7
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        QTP.last = self
 
    ################################ MVP / LVP ################################
    
    def get_mvp(self):
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################


