from urllib.request import Request, urlopen
import json
import requests
from const import*

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
        return self.log.pjcontent['plyaers'][i_player]['defenses'][0]['deadCount']>0
    
    ################################ DATA JOUEUR ################################
    
    def get_player_name(self, i_player: int):
        return self.log.jcontent['players'][i_player]['name']
    
    def get_pos_player(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['combatReplayData']['positions']
    
    def get_cc_boss(self, i_player: int):
        return self.log.jcontent['phases'][0]['dpsStatsTargets'][i_player][0][3]
    
    def get_cc_total(self, i_player: int):
        return self.log.jcontent['phases'][0]['dpsStats'][i_player][3]
    
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
            return f" * *[**MVP** : {s} se sont tous les {len(p)} pris **{v}** bleues sur VG]*"
        else:
            return f" * *[**MVP** : {s} s'est pris **{v}** bleues sur VG]*"
    
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
        v = v / t * 100
        return f" * *[**MVP** : {s} avec seulement **{v:.1f}%** des degats sur split en DPS]*"
    
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
        return f" * *[**MVP** : {s} avec seulement **{v:.1f}%** des degats sur split sans faire de canon]*"
    
    def get_lvp(self):
        return f"LVP de {self.name}"

    ################################ CONDITIONS ###############################
    
    def is_cannon(self, i_player: int, n: int=0):
        
        detect_radius = 45
        pos_player = self.get_pos_player(i_player)
        match n:
            case 0: 
                canon_pos = [pos_cannon1, pos_cannon2, pos_cannon3, pos_cannon4]
            case 1:
                canon_pos = [pos_cannon1]
            case 2:
                canon_pos = [pos_cannon2]
            case 3:
                canon_pos = [pos_cannon3]
            case 4:
                canon_pos = [pos_cannon4]
            case _:
                canon_pos = []
        for e in pos_player:
            for cannon in canon_pos:
                if (e[0] - cannon[0])**2 + (e[1] - cannon[1])**2 <= detect_radius**2:
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
        relativ_v = v / total_cc_boss * 100
        s = ', '.join(list(map(self.get_player_name, p)))
        if len(p)>1:
            return f" * *[**MVP** : {s} qui ont fait seulement **{v:.0f}** de CC (**{relativ_v:.1f}%** du total) sans manger de shroom]*"
        return f" * *[**MVP** : {s} qui a fait seulement **{v:.0f}** de CC (**{relativ_v:.1f}%** du total) sans manger de shroom]*"
    
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
        relativ_v = v / total_cc_boss * 100
        s = ', '.join(list(map(self.get_player_name, p)))
        if v == 0:
            if len(p)>1:
                return f" * *[**MVP** : {s} qui n'ont même pas CC sans s'être sacrifié]*"
            else:
                return f" * *[**MVP** : {s} qui n'a même pas CC sans s'être sacrifié]*"
        elif len(p)>1:
            return f" * *[**MVP** : {s} qui ont fait seulement **{v:.0f}** de CC (**{relativ_v:.1f}%** du total) sans s'être sacrifié]*"
        return f" * *[**MVP** : {s} qui a fait seulement **{v:.0f}** de CC (**{relativ_v:.1f}%** du total) sans s'être sacrifié]*"
    
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
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################



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
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################



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
        return f"MVP de {self.name}"
    
    def get_lvp(self):
        return f"LVP de {self.name}"
    
    ################################ CONDITIONS ################################
    
    
    
    ################################ DATA MECHAS ################################

    

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


