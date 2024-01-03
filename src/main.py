from models.log_class import*
from const import*

if __name__ == "__main__":
    
    log = Log('https://dps.report/IgfZ-20240101-233109_gors')
    
    boss = eval(all_bosses[-1].__class__.__name__) # Get le nom d'instance en fonction du log pour les tests

    print("\n",boss.current.mvp,"\n") # Get le mvp

    print(f"\nListe de tous les boss instanciés : {all_bosses}\n") # Afficher toutes les instances
    
