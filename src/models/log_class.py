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
        self.wingman = False
        if("wingman" in self.url):
            self.wingman = True
        if(self.wingman==True and ("logContent" not in self.url)):
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
        match boss_name:
            case "vg":
                vg = VG(log, "VG")
            case "gors":
                gors = GORS(log, "GORS")
            case "sab":
                sab = SABETHA(log, "SABETHA")
            case "sloth":
                sloth = SLOTH(log, "SLOTH")
            case "matt":
                matt = MATTHIAS(log, "MATTHIAS")
            case "esc":
                esc = ESCORT(log, "ESCORT")
            case "kc":
                kc = KC(log, "KC")
            case "xera":
                xera = XERA(log, "XERA")
            case "cairn":
                cairn = CAIRN(log, "CAIRN")
            case "mo":
                mo = MO(log, "MO")
            case "sam":
                sam = SAMAROG(log, "SAMAROG")
            case "dei":
                dei = DEIMOS(log, "DEIMOS")
            case "sh":
                sh = SH(log, "SH")
            case "dhumm":
                dhuum = DHUUM(log, "DHUUM")
            case "ca":
                ca = CA(log, "CA")
            case "twins":
                twins = LARGOS(log, "LARGOS")
            case "qadim":
                qadim = Q1(log, "QUOIDIMM")
            case "adina":
                adina = ADINA(log, "ADINA")
            case "sabir":
                sabir = SABIR(log, "SABIR")
            case "qpeer":
                qpeer = QTP(log, "QTP")
            case _:
                raise ValueError("Unknown Boss") 

class Boss:  
    def __init__(self, log: Log, name: str):
        self.log = log
        self.cm = self.is_cm()
        self.logName = self.get_logName()
        self.name = name
        
    ################################ Fonction pour attribus Boss ################################
    
    def is_cm(self):
        return self.log.pjcontent['isCM']
    
    def get_logName(self):
        return self.log.pjcontent['fightName']       
            
    ################################ Fonctions vérification ################################
        
    def is_quick(self, i_player: int):
        jlog = self.log.jcontent
        if(jlog['phases'][0]['boonGenGroupStats'][i_player]['data'][2][0]>=35
            or jlog['phases'][0]['boonGenGroupStats'][i_player]['data'][2][1]>=35):
            return True
        return False

    def is_alac(self, i_player: int):
        jlog = self.log.jcontent
        if(jlog['phases'][0]['boonGenGroupStats'][i_player]['data'][3][0]>=35
            or jlog['phases'][0]['boonGenGroupStats'][i_player]['data'][3][1]>=35):
            return True
        return False
    
    def is_support(self, i_player: int):
        if(self.is_quick(i_player) or self.is_alac(i_player)):
            return True
        return False
    
    ################################ DATA JOUEUR ################################
    
    def get_player_name(self, i_player: int):
        jlog = self.log.jcontent
        return jlog['players'][i_player]['name']
    
    def get_pos_player(self, i_player: int):
        return self.log.pjcontent['players'][i_player]['combatReplayData']['positions']
    
class Stats:
    @staticmethod
    def get_max_value(log : Log,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):
        
        jlog = log.jcontent
        i_max = None
        value_max = 0
        nb_players = len(jlog['players'])
        excluding = len(exclude)>0        
        for i in range(nb_players):
            filtre = False
            value = fnc(i)
            if(excluding):
                for c in exclude:
                    if(c(log,i)):
                        filtre = True
                        break           
            if(not filtre and value > value_max):
                value_max = value
                i_max = i
        return i_max, value_max
    
    @staticmethod
    def get_min_value(log : Log,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):
        
        jlog = log.jcontent
        i_min = None
        value_min = BIG
        nb_players = len(jlog['players'])
        excluding = len(exclude)>0   
        for i in range(nb_players):
            filtre = False
            value = fnc(i)
            if(excluding):
                for c in exclude:
                    if(c(i)):
                        filtre = True
                        break      
            if(not filtre and value < value_min):
                value_min = value
                i_min = i
        return i_min, value_min

    @staticmethod
    def get_tot_value(log : Log,
                      fnc: classmethod, 
                      exclude: list[classmethod] = []):
                
        jlog = log.jcontent
        value_tot = 0
        nb_players = len(jlog['players'])
        excluding = len(exclude)>0        
        for i in range(nb_players):
            filtre = False
            value = fnc(i) 
            if(excluding):
                for c in exclude:
                    if(c(i)):
                        filtre = True
                        break      
            if(not filtre):
                value_tot += value
        return value_tot
    
################################ VG ################################

class VG(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        VG.mvp = self.get_mvp()
        VG.wing = 1
        VG.current = self
        all_bosses.append(self)
        
    def get_mvp(self):
        return f"MVP de {self.name}"

################################ GORS ################################

class GORS(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        GORS.mvp = self.get_mvp()
        GORS.wing = 1
        GORS.current = self
        all_bosses.append(self)
        
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
        msg = f" * *[**MVP** : {self.get_player_name(i)} avec seulement {v:.1f}% des degats sur split en pur dps]*"
        return msg

################################ SABETHA ################################

class SABETHA(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        SABETHA.mvp = self.get_mvp()
        SABETHA.wing = 1
        SABETHA.current = self
        all_bosses.append(self)
        
    def get_dmg_split(self,i_player: int):
        jlog = self.log.jcontent
        dmg = 0
        dmg_kernan = jlog['phases'][2]['dpsStatsTargets'][i_player][0][0]
        dmg_mornifle = jlog['phases'][5]['dpsStatsTargets'][i_player][0][0]
        dmg_karde = jlog['phases'][7]['dpsStatsTargets'][i_player][0][0]
        dmg += dmg_kernan + dmg_mornifle + dmg_karde
        return dmg
    
    def is_cannon(self, 
                  i_player: int, 
                  n: int=0):
        
        detect_radius = 45
        pjlog = self.log.pjcontent
        pos_player = self.get_pos_player(i_player)
        if(n==0):
            for e in pos_player:
                c1 = (e[0] - pos_cannon1[0])**2 + (e[1] - pos_cannon1[1])**2 <= detect_radius**2
                c2 = (e[0] - pos_cannon2[0])**2 + (e[1] - pos_cannon2[1])**2 <= detect_radius**2
                c3 = (e[0] - pos_cannon3[0])**2 + (e[1] - pos_cannon3[1])**2 <= detect_radius**2
                c4 = (e[0] - pos_cannon4[0])**2 + (e[1] - pos_cannon4[1])**2 <= detect_radius**2
                if(c1 or c2 or c3 or c4):
                    return True
        else:
            cannon = eval(f"pos_cannon{n}")
            for e in pos_player:
                if((e[0] - cannon[0])**2 + (e[1] - cannon[1])**2 <= detect_radius**2):
                    return True
        return False
    
    def get_mvp(self):
        total_dmg_split = Stats.get_tot_value(self.log, self.get_dmg_split)
        i, v = Stats.get_min_value(self.log, self.get_dmg_split, exclude=[self.is_support,self.is_cannon])
        v = v / total_dmg_split * 100
        msg = f" * *[**MVP** : {self.get_player_name(i)} avec seulement {v:.1f}% des degats sur split en pur dps]*"
        return msg

################################ SLOTH ################################

class SLOTH(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        SLOTH.mvp = self.get_mvp()
        SLOTH.wing = 2
        SLOTH.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ MATTHIAS ################################

class MATTHIAS(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        MATTHIAS.mvp = self.get_mvp()
        MATTHIAS.wing = 2
        MATTHIAS.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ ESCORT ################################

class ESCORT(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        ESCORT.mvp = self.get_mvp()
        ESCORT.wing = 3
        ESCORT.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ KC ################################

class KC(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        KC.mvp = self.get_mvp()
        KC.wing = 3
        KC.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ XERA ################################

class XERA(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        XERA.mvp = self.get_mvp()
        XERA.wing = 3
        XERA.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ CAIRN ################################

class CAIRN(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        CAIRN.mvp = self.get_mvp()
        CAIRN.wing = 4
        CAIRN.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ MO ################################

class MO(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        MO.mvp = self.get_mvp()
        MO.wing = 4
        MO.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ SAMAROG ################################

class SAMAROG(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        SAMAROG.mvp = self.get_mvp()
        SAMAROG.wing = 4
        SAMAROG.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ DEIMOS ################################

class DEIMOS(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        DEIMOS.mvp = self.get_mvp()
        DEIMOS.wing = 4
        DEIMOS.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ SH ################################

class SH(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        SH.mvp = self.get_mvp()
        SH.wing = 5
        SH.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ DHUUM ################################

class DHUUM(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        DHUUM.mvp = self.get_mvp()
        DHUUM.wing = 5
        DHUUM.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ CA ################################

class CA(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        CA.mvp = self.get_mvp()
        CA.wing = 6
        CA.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ LARGOS ################################

class LARGOS(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        LARGOS.mvp = self.get_mvp()
        LARGOS.wing = 6
        LARGOS.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ QADIM ################################

class Q1(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        Q1.mvp = self.get_mvp()
        Q1.wing = 6
        Q1.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ ADINA ################################

class ADINA(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        ADINA.mvp = self.get_mvp()
        ADINA.wing = 7
        ADINA.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ SABIR ################################

class SABIR(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        SABIR.mvp = self.get_mvp()
        SABIR.wing = 7
        SABIR.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"

################################ QTP ################################

class QTP(Boss):
    
    current = None
    
    def __init__(self, log: Log, name: str):
        super().__init__(log, name)
        QTP.mvp = self.get_mvp()
        QTP.wing = 7
        QTP.current = self
        all_bosses.append(self)

    def get_mvp(self):
        return f"MVP de {self.name}"