from models.log_class import*
from const import*

if __name__ == "__main__":
    
    log = Log('https://dps.report/rdqi-20240101-232122_vg')

    boss = all_bosses[-1] # Get le nom d'instance en fonction du log pour les tests
    
    
    mechs_list = [mech['name'] for mech in boss.mechanics]
    print(mechs_list)
    
    print(boss.mvp) 
    
    print(f"\nListe de tous les boss instanciés : {all_bosses}\n") # Afficher toutes les instances
    
