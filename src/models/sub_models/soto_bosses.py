from models.boss_class import Boss, Stats
from models.log_class import Log
from func import *
import numpy as np

################################ DAGDA ################################

class DAGDA(Boss):
    
    last    = None
    name    = "DAGDA"
    boss_id = 25705
    wing    = "SOTO"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp   = self.get_mvp()
        self.lvp   = self.get_lvp()
        DAGDA.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ CERUS ################################

class CERUS(Boss):
    
    last    = None
    name    = "CERUS"
    boss_id = 25989
    wing    = "SOTO"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp   = self.get_mvp()
        self.lvp   = self.get_lvp()
        DAGDA.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()