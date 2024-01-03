from models.log_class import*
from const import*

if __name__ == "__main__":
    
    log = Log('https://dps.report/IgfZ-20240101-233109_gors')

    boss = eval(all_bosses[-1].__class__.__name__) # Get le nom d'instance en fonction du log pour les tests

    print("\n",boss.current.mvp,"\n") # Get le mvp
    
    # Exemple affichage des rôle
    alacs,quicks,dpss=[],[],[]   
    for i in range(10):
        player_name = boss.current.get_player_name(i)
        if boss.current.is_alac(i):
            alacs.append(boss.current.get_player_name(i))
        if boss.current.is_quick(i):
            quicks.append(boss.current.get_player_name(i))
        else:
            dpss.append(boss.current.get_player_name(i))
    for e in alacs:
        print(f"{e} est ALAC")
    for e in quicks:
        print(f"{e} est QUICK")
    for e in dpss:
        print(f"{e} est DPS")

    print(f"\nListe de tous les boss instanciés : {all_bosses}\n") # Afficher toutes les instances
    
