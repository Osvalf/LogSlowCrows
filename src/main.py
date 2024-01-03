from models.log_class import*
from const import*

if __name__ == "__main__":
    
    log = Log('https://dps.report/IgfZ-20240101-233109_gors')
    
    boss = eval(all_bosses[-1].__class__.__name__) # Get le nom d'instance en fonction du log pour les tests

    print("\n",boss.current.mvp,"\n") # Get le mvp
    
    for i in range(10):
        player_name = boss.current.get_player_name(i)
        if(boss.current.is_alac(i)):
            print(f"{player_name} est ALAC")
        elif(boss.current.is_quick(i)):
            print(f"{player_name} est QUICK")
        else:
            print(f"{player_name} est DPS")

    print(f"\nListe de tous les boss instanciés : {all_bosses}\n") # Afficher toutes les instances
    
