from models.log_class import*

if __name__ == "__main__":
    
    log = Log('https://dps.report/uOiB-20240101-212748_dhuum')

    boss = all_bosses[-1] # Get le nom d'instance en fonction du log pour les tests
    print("\n")
    mechs_list = [mech['name'] for mech in boss.mechanics]
    print(mechs_list)
    print("\n")
    print(boss.mvp)
    print(boss.lvp)
    
    print(f"\nListe de tous les boss instanciés : {all_bosses}\n") # Afficher toutes les instances
    
