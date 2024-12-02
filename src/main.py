from argparse import ArgumentParser
from time import perf_counter
import grequests

from const import REQUEST_HEADERS, DPS_REPORT_JSON_URL, DEFAULT_LANGUAGE, DEFAULT_TITLE, DEFAULT_INPUT_FILE, ALL_BOSSES, ALL_PLAYERS
from models.log_class import Log
from models.boss_facto import BossFactory
import func
from languages import LANGUES
from input import InputParser

def _make_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', required=False)
    parser.add_argument('-l', '--language', required=False, default=DEFAULT_LANGUAGE)
    parser.add_argument('-r', '--reward', action='store_true', required=False)
    parser.add_argument('-i', '--input', required=False, default=DEFAULT_INPUT_FILE)
    return parser

def main(input_file, **kwargs) -> None:
    urls = InputParser(input_file).validate().urls
    requests = []
    for url in urls:
        requests.append(grequests.get(url))
        requests.append(grequests.get(DPS_REPORT_JSON_URL, params={"permalink": url}, headers=REQUEST_HEADERS))
    responses = grequests.map(requests, size=2*len(urls))
    logs = [Log(url) for url in urls]
    for i in range(len(urls)):
        logs[i].set_jcontent(responses[2*i])
        logs[i].set_pjcontent(responses[2*i+1])
    for log in logs:
        BossFactory.create_boss(log)
    print("\n")
    split_run_message = func.get_message_reward(ALL_BOSSES, ALL_PLAYERS, titre=DEFAULT_TITLE)
    for message in split_run_message:
        print(message)

    print("\n")

if __name__ == "__main__":
    print("Starting\n")
    start_time = perf_counter()
    LANGUES["selected_language"] = LANGUES["FR"]
    args = _make_parser().parse_args()
    main(args.input, reward_mode=args.reward, debug=args.debug, language=args.language)
    end_time = perf_counter()
    print(f"--- {end_time - start_time:.3f} seconds ---\n")