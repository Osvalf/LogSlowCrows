from models.boss_class import Boss, Stats
from models.log_class import Log
from func import *
import numpy as np

################################ MAMA ################################

class MAMA(Boss):
    
    last    = None
    name    = "MAMA"
    boss_id = 17021
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp  = self.get_mvp()
        self.lvp  = self.get_lvp()
        MAMA.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ SIAX ################################

class SIAX(Boss):
    
    last    = None
    name    = "SIAX"
    boss_id = 17028
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp = self.get_mvp()
        self.lvp = self.get_lvp()
        SIAX.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ ENSOLYSS ################################

class ENSOLYSS(Boss):
    
    last    = None
    name    = "ENSOLYSS"
    boss_id = 16948
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp      = self.get_mvp()
        self.lvp      = self.get_lvp()
        ENSOLYSS.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ SKORVALD ################################

class SKORVALD(Boss):
    
    last    = None
    name    = "SKORVALD"
    boss_id = 17632
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp      = self.get_mvp()
        self.lvp      = self.get_lvp()
        SKORVALD.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ ARTSARIIV ################################

class ARTSARIIV(Boss):
    
    last    = None
    name    = "ARTSARIIV"
    boss_id = 17949
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp       = self.get_mvp()
        self.lvp       = self.get_lvp()
        ARTSARIIV.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ ARKK ################################

class ARKK(Boss):
    
    last    = None
    name    = "ARKK"
    boss_id = 17759
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp  = self.get_mvp()
        self.lvp  = self.get_lvp()
        ARKK.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ DARK AI ################################

class DARKAI(Boss):
    
    last    = None
    name    = "DARK AI"
    boss_id = 23254
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp    = self.get_mvp()
        self.lvp    = self.get_lvp()
        DARKAI.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ KANAXAI ################################

class KANAXAI(Boss):
    
    last    = None
    name    = "KANAXAI"
    boss_id = 25577
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp     = self.get_mvp()
        self.lvp     = self.get_lvp()
        KANAXAI.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()
    
################################ EPARCH ################################

class EPARCH(Boss):
    
    last    = None
    name    = "EPARCH"
    boss_id = 26231
    wing    = "FRAC"
    
    def __init__(self, log: Log):
        super().__init__(log)
        self.mvp    = self.get_mvp()
        self.lvp    = self.get_lvp()
        EPARCH.last = self
        
    def get_mvp(self):
        msg_bad_dps = self.get_bad_dps()
        if msg_bad_dps:
            return msg_bad_dps
        return    
    
    def get_lvp(self):
        return self.get_lvp_dps()