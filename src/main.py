from models.log_class import*
from const import*

if __name__ == "__main__":
    
    log = Log('https://dps.report/viV3-20231229-233308_sab')

    print("\n",SABETHA.current.get_mvp(),"\n") # Afficher le msg MVP sur sabetha
    
    for i in range(10): # Afficher les joueurs qui ont fait cannon
        if(SABETHA.current.is_cannon(i)):
            print(f"{SABETHA.current.get_player_name(i)} a fait cannon")
            
    print("\n")

    for i in range(10): # Afficher les joueurs qui jouent quick
        if(SABETHA.current.is_quick(i)):
            print(f"{SABETHA.current.get_player_name(i)} joue quick")

    print(f"\nListe de tous les boss instanciés : {all_bosses}\n") # Afficher toutes les instances
