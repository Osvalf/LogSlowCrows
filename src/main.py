from models.log_class import*
import concurrent.futures
from time import perf_counter

TITRE = "Run"

def main() -> None:
    input_lines = txt_file_to_lines("src/input logs.txt")
    reward_mode = False
    error = False
    input_urls, error = lines_to_urls(input_lines, reward_mode=reward_mode)
    if error:
        print(input_urls)
    #Pour tester séparément
    #input_urls = ["https://dps.report/XXNc-20240117-232331_vg"]
    
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(Log, input_value) for input_value in input_urls]
        concurrent.futures.wait(futures)
    
    print("\n")
    
    all_bosses.sort(key=lambda boss: boss.start_date, reverse=False)
    
    # Fonction reward si pas de test
    if not error:
        split_run_message = get_message_reward(all_bosses, all_players, titre=TITRE)
        for message in split_run_message:
            print(message)
            
    print("\n")
    
    #print(f"\nListe de tous les objets boss instanciés : {all_bosses}\n") # Afficher toutes les instances

if __name__ == "__main__":
    print("Starting\n")
    start_time = perf_counter()    
    langues["selected_language"] = langues["EN"]
    main()
    """log = Log("https://dps.report/oF0B-20240203-233957_matt")
    boss = all_bosses[0]
    print(boss.mvp)"""
    end_time = perf_counter()
    print(f"--- {end_time - start_time:.3f} seconds ---\n")
    
