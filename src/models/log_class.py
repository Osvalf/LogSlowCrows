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
        
    ################################ Fonction pour attribus Boss ################################
    
    def is_cm(self):
        return self.log.pjcontent['isCM']
    
    def get_logName(self):
        return self.log.pjcontent['fightName']       
            
    ################################ Fonctions vérification ################################
        
    def is_quick(self, i_player: int):
        player_quick_contrib = self.log.jcontent['phases'][0]['boonGenGroupStats'][i_player]['data'][2]
        return player_quick_contrib[0]>=35 or player_quick_contrib[1]>=35

    def is_alac(self, i_player: int):
        player_alac_contrib = self.log.jcontent['phases'][0]['boonGenGroupStats'][i_player]['data'][3]
        return player_alac_contrib[0]>=35 or player_alac_contrib[1]>=35
    
    def is_support(self, i_player: int):
        return self.is_quick(i_player) or self.is_alac(i_player)
    
    ################################ DATA JOUEUR ################################
    
    def get_player_name(self, i_player: int):
        return self.log.jcontent['players'][i_player]['name']
    
    def get_pos_player(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['combatReplayData']['positions']
    
class Stats:
    @staticmethod
    def get_max_value(log : Log,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):

        i_max = None
        value_max = 0
        nb_players = len(log.jcontent['players'])
        for i in range(nb_players):
            for filtre in exclude:
                if filtre(i):
                    break
            else:
                value = fnc(i)
                if value > value_max:
                    value_max = value
                    i_max = i
        return i_max, value_max
    
    @staticmethod
    def get_min_value(log : Log,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):

        i_min = None
        value_min = BIG
        nb_players = len(log.jcontent['players'])
        for i in range(nb_players):
            for filtre in exclude:
                if filtre(i):
                    break
            else:
                value = fnc(i)
                if value < value_min:
                    value_min = value
                    i_min = i
        return i_min, value_min

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
    
    current = None
    name = "VG"
    wing = 1
    
    def __init__(self, log: Log):
        super().__init__(log)
        VG.mvp = self.get_mvp()
        VG.current = self
        
    def get_mvp(self):
        return f"MVP de {self.name}"

################################ GORS ################################

class GORS(Boss):
    
    current = None
    name = "GORS"
    wing = 1
    
    def __init__(self, log: Log):
        super().__init__(log)
        GORS.mvp = self.get_mvp()
        GORS.current = self
        
    def get_dmg_split(self, i_player: int):
        jlog = self.log.jcontent
        dmg = 0
        dmg_split_1 = jlog['phases'][3]['dpsStatsTargets'][i_player]
        dmg_split_2 = jlog['phases'][6]['dpsStatsTargets'][i_player]
        for i in range(len(dmg_split_1)):
            dmg += dmg_split_1[i][0] + dmg_split_2[i][0]
        return dmg
    
    def get_mvp(self):
        total_dmg_split = Stats.get_tot_value(self.log, self.get_dmg_split)
        i, v = Stats.get_min_value(self.log, self.get_dmg_split, exclude=[self.is_support])
        v = v / total_dmg_split * 100
        return f" * *[**MVP** : {self.get_player_name(i)} avec seulement {v:.1f}% des degats sur split en pur dps]*"

################################ SABETHA ################################

class SABETHA(Boss):
    
    current = None
    name = "SABETHA"
    wing = 1
    
    def __init__(self, log: Log):
        super().__init__(log)
        SABETHA.mvp = self.get_mvp()
        SABETHA.current = self
        
    def get_dmg_split(self,i_player: int):
        jlog = self.log.jcontent
        dmg = 0
        dmg_kernan = jlog['phases'][2]['dpsStatsTargets'][i_player][0][0]
        dmg_mornifle = jlog['phases'][5]['dpsStatsTargets'][i_player][0][0]
        dmg_karde = jlog['phases'][7]['dpsStatsTargets'][i_player][0][0]
        dmg += dmg_kernan + dmg_mornifle + dmg_karde
        return dmg
    
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
    
    def get_mvp(self):
        total_dmg_split = Stats.get_tot_value(self.log, self.get_dmg_split)
        i, v = Stats.get_min_value(self.log, self.get_dmg_split, exclude=[self.is_support,self.is_cannon])
        v = v / total_dmg_split * 100
        return f" * *[**MVP** : {self.get_player_name(i)} avec seulement {v:.1f}% des degats sur split en pur dps]*"

################################ SLOTH ################################

class SLOTH(Boss):
    
    current = None
    name = "SLOTH"
    wing = 2
    
    def __init__(self, log: Log):
        super().__init__(log)
        SLOTH.mvp = self.get_mvp()
        SLOTH.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ MATTHIAS ################################

class MATTHIAS(Boss):
    
    current = None
    name = "MATTHIAS"
    wing = 2
    
    def __init__(self, log: Log):
        super().__init__(log)
        MATTHIAS.mvp = self.get_mvp()
        MATTHIAS.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ ESCORT ################################

class ESCORT(Boss):
    
    current = None
    name = "ESCORT"
    wing = 3
    
    def __init__(self, log: Log):
        super().__init__(log)
        ESCORT.mvp = self.get_mvp()
        ESCORT.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ KC ################################

class KC(Boss):
    
    current = None
    name = "KC"
    wing = 3
    
    def __init__(self, log: Log):
        super().__init__(log)
        KC.mvp = self.get_mvp()
        KC.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ XERA ################################

class XERA(Boss):
    
    current = None
    name = "XERA"
    wing = 3

    def __init__(self, log: Log):
        super().__init__(log)
        XERA.mvp = self.get_mvp()
        XERA.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ CAIRN ################################

class CAIRN(Boss):
    
    current = None
    name = "CAIRN"
    wing = 4
    
    def __init__(self, log: Log):
        super().__init__(log)
        CAIRN.mvp = self.get_mvp()
        CAIRN.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ MO ################################

class MO(Boss):
    
    current = None
    name = "MO"
    wing = 4
    
    def __init__(self, log: Log):
        super().__init__(log)
        MO.mvp = self.get_mvp()
        MO.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ SAMAROG ################################

class SAMAROG(Boss):
    
    current = None
    name = "SAMAROG"
    wing = 4
    
    def __init__(self, log: Log):
        super().__init__(log)
        SAMAROG.mvp = self.get_mvp()
        SAMAROG.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ DEIMOS ################################

class DEIMOS(Boss):
    
    current = None
    name = "DEIMOS"
    wing = 4
    
    def __init__(self, log: Log):
        super().__init__(log)
        DEIMOS.mvp = self.get_mvp()
        DEIMOS.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ SH ################################

class SH(Boss):
    
    current = None
    name = "SH"
    wing = 5
    
    def __init__(self, log: Log):
        super().__init__(log)
        SH.mvp = self.get_mvp()
        SH.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ DHUUM ################################

class DHUUM(Boss):
    
    current = None
    name = "DHUUM"
    wing = 5
    
    def __init__(self, log: Log):
        super().__init__(log)
        DHUUM.mvp = self.get_mvp()
        DHUUM.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ CA ################################

class CA(Boss):
    
    current = None
    name = "CA"
    wing = 6

    def __init__(self, log: Log):
        super().__init__(log)
        CA.mvp = self.get_mvp()
        CA.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ LARGOS ################################

class LARGOS(Boss):
    
    current = None
    name = "LARGOS"
    wing = 6
    
    def __init__(self, log: Log):
        super().__init__(log)
        LARGOS.mvp = self.get_mvp()
        LARGOS.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ QADIM ################################

class Q1(Boss):
    
    current = None
    name = "QUOIDIMM"
    wing = 6

    def __init__(self, log: Log):
        super().__init__(log)
        Q1.mvp = self.get_mvp()
        Q1.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ ADINA ################################

class ADINA(Boss):
    
    current = None
    name = "ADINA"
    wing = 7
    
    def __init__(self, log: Log):
        super().__init__(log)
        ADINA.mvp = self.get_mvp()
        ADINA.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ SABIR ################################

class SABIR(Boss):
    
    current = None
    name = "SABIR"
    wing = 7
    
    def __init__(self, log: Log):
        super().__init__(log)
        SABIR.mvp = self.get_mvp()
        SABIR.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ QTP ################################

class QTP(Boss):
    
    current = None
    name = "QTP"
    wing = 7
    
    def __init__(self, log: Log):
        super().__init__(log)
        QTP.mvp = self.get_mvp()
        QTP.current = self

    def get_mvp(self):
        return f"MVP de {self.name}"
