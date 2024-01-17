class Player:
    def __init__(self, boss, account: str):
        self.boss = [boss]
        self.account = account
        self.name = account[:-5]
        self.mvps = 0
        self.lvps = 0
        
    def add_boss(self, boss):
        self.boss.append(boss)
        self.boss.sort(key=lambda boss: boss.start_date, reverse=False)
        
    def get_boss_names(self):
        return [bos.name for bos in self.boss]
        
    def get_mvps(self):
        return f"Titres MVP de {self.name} : {self.mvps}"

    def get_lvps(self):
        return f"Titres LVP de {self.name} : {self.lvps}"