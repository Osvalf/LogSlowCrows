import argparse
import concurrent.futures
import IPython
from time import perf_counter
import sys
import traceback

from models.log_class import *
from func import *

TITRE = "Run"

class ThreadPoolExecutorStackTraced(concurrent.futures.ThreadPoolExecutor):

    def submit(self, fn, *args, **kwargs):
        return super(ThreadPoolExecutorStackTraced, self).submit(
            self._function_wrapper, fn, *args, **kwargs)

    def _function_wrapper(self, fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            print(f"Problematic log is : {args[0]}")
            raise sys.exc_info()[0](traceback.format_exc())

def main(args) -> None:
    input_lines = txt_file_to_lines("src/input logs.txt")
    reward_mode = False
    error = False
    input_urls, error = lines_to_urls(input_lines, reward_mode=reward_mode)
    if error:
        print(input_urls)
    # Pour tester séparément
    # input_urls = ["https://dps.report/XXNc-20240117-232331_vg"]
    
    with ThreadPoolExecutorStackTraced() as executor:
        futures = [executor.submit(Log, url) for url in input_urls]
        for future in futures:
            try:
                test = future.result()
            except TypeError as e:
                pass

    print("\n")
    if args.debug:
        IPython.embed()
    # Fonction reward si pas de test
    if not error:
        split_run_message = get_message_reward(all_bosses, all_players, titre=TITRE)
        for message in split_run_message:
            print(message)

    print("\n")

if __name__ == "__main__":
    print("Starting\n")
    start_time = perf_counter()
    langues["selected_language"] = langues["EN"]
    arg = argparse.ArgumentParser()
    arg.add_argument('--debug', action='store_true')
    args = arg.parse_args()
    main(args)
    """log = Log("https://dps.report/GlBX-20240904-213704_sam")
    boss = all_bosses[0]
    print(boss.wingman_percentile)
    print(boss.mvp)
    print(boss.lvp)"""
    end_time = perf_counter()
    print(f"--- {end_time - start_time:.3f} seconds ---\n")