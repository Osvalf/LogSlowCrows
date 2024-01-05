from models.log_class import*
import concurrent.futures


if __name__ == "__main__":    
        
    def createLog(url):
        return Log(url)
    
    input_urls = txt_file_to_list("src/input logs.txt")
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(createLog, input_value) for input_value in input_urls]
        concurrent.futures.wait(futures)
    
    all_mvp_dic = {x:all_mvp.count(x) for x in all_mvp}
    all_lvp_dic = {x:all_lvp.count(x) for x in all_lvp}
    
    print("\n")
    
    all_bosses.sort(key=lambda x: x.start_date, reverse=False)

    print(all_mvp_dic)
    print(all_lvp_dic)
    
    #print(f"\nListe de tous les boss instanciés : {all_bosses}\n") # Afficher toutes les instances
    
