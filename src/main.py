from models.log_class import*

if __name__ == "__main__":
    
    log = Log('https://dps.report/gmdg-20231118-223008_xera')

    boss = all_bosses[-1] # Get le nom d'instance en fonction du log pour les tests
    
    mechs_list = [mech['name'] for mech in boss.mechanics]
    print(mechs_list)
    
    print(boss.mvp)
    print(boss.lvp)
    print("\n")
    
    print(f"\nListe de tous les boss instanciés : {all_bosses}\n") # Afficher toutes les instances
    
