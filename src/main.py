from models.log_class import*
import concurrent.futures
from time import perf_counter

TITRE = "Run"

def main() -> None:
    input_urls = txt_file_to_list("src/input logs.txt")
    #Pour tester séparément
    #input_urls = ["https://dps.report/XQb8-20240110-214324_qpeer"]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(Log, input_value) for input_value in input_urls]
        concurrent.futures.wait(futures)
    
    all_mvp_dic = {x:all_mvp.count(x) for x in all_mvp}
    all_lvp_dic = {x:all_lvp.count(x) for x in all_lvp}
    
    print("\n")
    
    all_bosses.sort(key=lambda x: x.start_date, reverse=False)

    # Fonction reward si pas de test
    reward = get_message_reward(all_bosses, all_mvp_dic, all_lvp_dic, titre=TITRE)
    for s in reward:
        print(s)
            
    print("\n")
    
    #print(f"\nListe de tous les objets boss instanciés : {all_bosses}\n") # Afficher toutes les instances

if __name__ == "__main__":
    print("Starting")
    start_time = perf_counter()  
    main()
    end_time = perf_counter()
    print(f"--- {end_time - start_time:.3f} seconds ---\n")
    
    
