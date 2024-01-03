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
                vg = VG(log)
            case "gors":
                gors = GORS(log)
            case "sab":
                sab = SABETHA(log)
            case "sloth":
                sloth = SLOTH(log)
            case "matt":
                matt = MATTHIAS(log)
            case "esc":
                esc = ESCORT(log)
            case "kc":
                kc = KC(log)
            case "xera":
                xera = XERA(log)
            case "cairn":
                cairn = CAIRN(log)
            case "mo":
                mo = MO(log)
            case "sam":
                sam = SAMAROG(log)
            case "dei":
                dei = DEIMOS(log)
            case "sh":
                sh = SH(log)
            case "dhumm":
                dhuum = DHUUM(log)
            case "ca":
                ca = CA(log)
            case "twins":
                twins = LARGOS(log)
            case "qadim":
                qadim = Q1(log)
            case "adina":
                adina = ADINA(log)
            case "sabir":
                sabir = SABIR(log)
            case "qpeer":
                qpeer = QTP(log)
            case _:
                raise ValueError("Unknown Boss") 

class Boss:  
    def __init__(self, log: Log):
        self.log = log
        
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
    
    def __init__(self, log: Log):
        super().__init__(log)
        VG.mvp = self.get_mvp()
        VG.wing = 1
        VG.current = self
        all_bosses.append(self)

################################ GORS ################################

class GORS(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        GORS.mvp = self.get_mvp()
        GORS.wing = 1
        GORS.current = self
        all_bosses.append(self)

################################ SABETHA ################################

class SABETHA(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        SABETHA.mvp = self.get_mvp()
        SABETHA.wing = 1
        SABETHA.current = self
        all_bosses.append(self)
        
    def get_dmg_split_sab(self,i_player: int):
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
        total_dmg_split = Stats.get_tot_value(self.log, self.get_dmg_split_sab)
        i, v = Stats.get_min_value(self.log, self.get_dmg_split_sab, exclude=[self.is_support,self.is_cannon])
        v = v / total_dmg_split * 100
        msg = f" * *[**MVP** : {self.get_player_name(i)} avec {v:.1f}% des degats sur split en pur dps]*"
        return msg

################################ SLOTH ################################

class SLOTH(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        SLOTH.mvp = self.get_mvp()
        SLOTH.wing = 1
        SLOTH.current = self
        all_bosses.append(self)

################################ MATTHIAS ################################

class MATTHIAS(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        MATTHIAS.mvp = self.get_mvp()
        MATTHIAS.wing = 1
        MATTHIAS.current = self
        all_bosses.append(self)

################################ ESCORT ################################

class ESCORT(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        ESCORT.mvp = self.get_mvp()
        ESCORT.wing = 1
        ESCORT.current = self
        all_bosses.append(self)

################################ KC ################################

class KC(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        KC.mvp = self.get_mvp()
        KC.wing = 1
        KC.current = self
        all_bosses.append(self)

################################ XERA ################################

class XERA(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        XERA.mvp = self.get_mvp()
        XERA.wing = 1
        XERA.current = self
        all_bosses.append(self)

################################ CAIRN ################################

class CAIRN(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        CAIRN.mvp = self.get_mvp()
        CAIRN.wing = 1
        CAIRN.current = self
        all_bosses.append(self)

################################ MO ################################

class MO(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        MO.mvp = self.get_mvp()
        MO.wing = 1
        MO.current = self
        all_bosses.append(self)

################################ SAMAROG ################################

class SAMAROG(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        SAMAROG.mvp = self.get_mvp()
        SAMAROG.wing = 1
        SAMAROG.current = self
        all_bosses.append(self)

################################ DEIMOS ################################

class DEIMOS(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        DEIMOS.mvp = self.get_mvp()
        DEIMOS.wing = 1
        DEIMOS.current = self
        all_bosses.append(self)

################################ SH ################################

class SH(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        SH.mvp = self.get_mvp()
        SH.wing = 1
        SH.current = self
        all_bosses.append(self)

################################ DHUUM ################################

class DHUUM(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        DHUUM.mvp = self.get_mvp()
        DHUUM.wing = 1
        DHUUM.current = self
        all_bosses.append(self)

################################ CA ################################

class CA(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        CA.mvp = self.get_mvp()
        CA.wing = 1
        CA.current = self
        all_bosses.append(self)

################################ LARGOS ################################

class LARGOS(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        LARGOS.mvp = self.get_mvp()
        LARGOS.wing = 1
        LARGOS.current = self
        all_bosses.append(self)

################################ QADIM ################################

class Q1(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        Q1.mvp = self.get_mvp()
        Q1.wing = 1
        Q1.current = self
        all_bosses.append(self)

################################ ADINA ################################

class ADINA(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        ADINA.mvp = self.get_mvp()
        ADINA.wing = 1
        ADINA.current = self
        all_bosses.append(self)

################################ SABIR ################################

class SABIR(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        SABIR.mvp = self.get_mvp()
        SABIR.wing = 1
        SABIR.current = self
        all_bosses.append(self)

################################ QTP ################################

class QTP(Boss):
    
    current = None
    
    def __init__(self, log: Log):
        super().__init__(log)
        QTP.mvp = self.get_mvp()
        QTP.wing = 1
        QTP.current = self
        all_bosses.append(self)