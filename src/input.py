import sys
from const import DEFAULT_INPUT_FILE, BOSS_DICT

class InputParser:
    def __init__(self, input_file = DEFAULT_INPUT_FILE):
        self.urls = []
        with open(input_file, "r") as file:
            for line in file.readlines():
                line = line.strip()
                if not line or not line.startswith("https://"):
                    continue
                self.urls.append(line)
    
    def validate(self):
        problems = []
        for url in self.urls:
            parts = url.split("_")
            if "https://dps.report/" not in url or \
            parts[1] not in BOSS_DICT.values() or \
            not parts[0].split("-")[1].isdigit() or \
            not parts[0].split("-")[2].isdigit():
                problems.append(url)
        if problems:
            sys.exit(print(f"Invalid urls: {problems}"))
        return self