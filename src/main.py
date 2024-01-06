from models.log_class import*
import concurrent.futures


if __name__ == "__main__":    
        
    def createLog(url):
        return Log(url)
    
    input_urls = txt_file_to_list("src/input logs.txt")
    
    #Pour tester séparément
    #input_urls = ["https://dps.report/oV8b-20231223-211804_vg"]
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(createLog, input_value) for input_value in input_urls]
        concurrent.futures.wait(futures)
    
    all_mvp_dic = {x:all_mvp.count(x) for x in all_mvp}
    all_lvp_dic = {x:all_lvp.count(x) for x in all_lvp}
    
    print("\n")
    
    all_bosses.sort(key=lambda x: x.start_date, reverse=False)
    
    # Fonction reward si pas de test
    if len(input_urls) >= 19:
        reward = get_message_reward(all_bosses, all_mvp_dic, all_lvp_dic)
        for s in reward:
            print(s)
        
    print("\n")
    
    #print(f"\nListe de tous les objets boss instanciés : {all_bosses}\n") # Afficher toutes les instances
    
