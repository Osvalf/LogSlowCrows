from models.log_class import*

if __name__ == "__main__":
    
    log = Log('https://dps.report/Zt09-20240101-225638_qpeer')
    
    boss = all_bosses[-1] # Get le nom d'instance en fonction du log pour les tests
    
    all_mvp = {x:all_mvp.count(x) for x in all_mvp}
    all_lvp = {x:all_lvp.count(x) for x in all_lvp}
    
    print("\n")

    print(boss.mvp)
    print(boss.lvp)
    
    print(all_mvp)
    print(all_lvp)
    
    print(f"\nListe de tous les boss instanciés : {all_bosses}\n") # Afficher toutes les instances
    
