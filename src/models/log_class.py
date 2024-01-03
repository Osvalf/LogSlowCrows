from urllib.request import Request, urlopen
import json
import requests
from const import*

class Log:
    def __init__(self, url):
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
        if(boss_dict[boss_id]=="sab"):
            sab = SABETHA(log)
        else:
            raise ValueError("Unknown Boss") 

class Boss:  
    def __init__(self, log):
        self.log = log
        
    ################################ Fonctions vérification ################################
        
    def is_quick(self,i_player):
        jlog = self.log.jcontent
        if(jlog['phases'][0]['boonGenGroupStats'][i_player]['data'][2][0]>=35
            or jlog['phases'][0]['boonGenGroupStats'][i_player]['data'][2][1]>=35):
            return True
        return False

    def is_alac(self,i_player):
        jlog = self.log.jcontent
        if(jlog['phases'][0]['boonGenGroupStats'][i_player]['data'][3][0]>=35
            or jlog['phases'][0]['boonGenGroupStats'][i_player]['data'][3][1]>=35):
            return True
        return False
    
    def is_support(self,i_player):
        if(self.is_quick(i_player) or self.is_alac(i_player)):
            return True
        return False
    
    ################################ DATA JOUEUR ################################
    
    def get_player_name(self,i_player):
        jlog = self.log.jcontent
        return jlog['players'][i_player]['name']
    
    def get_pos_player(self,i_player):
        return self.log.pjcontent['players'][i_player]['combatReplayData']['positions']
    
class Stats:
    @staticmethod
    def get_max_value(log, fnc, exclude=[]):
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
    def get_min_value(log, fnc, exclude=[]):
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
    def get_tot_value(log, fnc, exclude=[]):
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

class SABETHA(Boss):
    
    def __init__(self, log):
        super().__init__(log)
        SABETHA.mvp = self.get_mvp()
        SABETHA.wing = 1
        all_bosses.append(self)
        
    def get_dmg_split_sab(self,i_player):
        jlog = self.log.jcontent
        dmg = 0
        dmg_kernan = jlog['phases'][2]['dpsStatsTargets'][i_player][0][0]
        dmg_mornifle = jlog['phases'][5]['dpsStatsTargets'][i_player][0][0]
        dmg_karde = jlog['phases'][7]['dpsStatsTargets'][i_player][0][0]
        dmg += dmg_kernan + dmg_mornifle + dmg_karde
        return dmg
    
    def is_cannon(self,i_player,n=0):
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