import json

DEFAULT_LANGUAGE = "FR"
DEFAULT_TITLE = "Run"
DEFAULT_INPUT_FILE = "src/input_logs.txt"

BIG = float('inf')

DPS_REPORT_JSON_URL = "https://dps.report/getJson?permalink="

ALL_BOSSES = []
ALL_PLAYERS = {}

BOSS_DICT = {
    #  RAID BOSSES
    15438: "vg",
    15429: "gors",
    15375: "sab",
    
    16123: "sloth",
    16115: "matt",
    
    16253: "esc",
    16235: "kc",
    16246: "xera",
    
    17194: "cairn",
    17172: "mo",
    17188: "sam",
    17154: "dei",
    
    19767: "sh",
    19450: "dhuum",
    
    43974: "ca",
    21105: "twins",
    20934: "qadim",
    
    22006: "adina",
    21964: "sabir",
    22000: "qpeer",
    
    26725: "greer",
    26774: "decima",
    26712: "ura",
    
    #  IBS BOSSES
    22154: "ice",
    22343: "falln",
    22492: "frae",
    22711: "whisp",
    22521: "bone",
    
    #  EOD BOSSES
    24033: "trin",
    23957: "ankka",
    24266: "li",
    43488: "void",
    25414: "olc",
    
    #  SOTO BOSSES
    25705: "dagda",
    25989: "cerus",
    
    # FRAC BOSSES
    17021: "mama",
    17028: "siax",
    16948: "enso",
    
    17632: "skor",
    17949: "arriv",
    17759: "arkk",
    
    23254: "ai",
    
    25577: "kana",
    
    26231: "eparc"
    }

EXTRA_BOSS_DICT = {
    16199: "golem",
    19645: "golem"
}

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Alt-Used': 'dps.report',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}

CUSTOM_NAMES = {
    "Acebo.3649"            : "Acebo",
    "anko.5043"             : "Aiko",
    "Ambroid.7156"          : "Ambroid",
    "Arka.3754"             : "Arka",
    "Arthy.4521"            : "Arthy",
    "drework.6129"          : "Atalor",
    "Ava.7895"              : "Ava",
    "Anubis.9346"           : "Babar",
    "Arkadia.9432"          : "Babar",
    "RedGuard Arkadia.7539" : "Babar",
    "Balna.6021"            : "Balna",
    "nounours assassin.7459": "Baron",
    "Betameche.7610"        : "Beta",
    "BobbyFrasier.8450"     : "BobbyFrasier",
    "Mortarion.8517"        : "Bobette",
    "Blaxono Junior.4732"   : "Boti",
    "Bou.1052"              : "Bou",
    "Brizeh.5014"           : "Brizeh",
    "Twiyaka.9738"          : "Brizeh",
    "Ninjamobb.2083"        : "Brocoli",
    "Unity.2654"            : "Bubulle",
    "Captain.6892"          : "Captain",
    "Enmity.3465"           : "Captain",
    "Eleonora.5183"         : "Captainette",
    "Darkouu.2634"          : "Darkou",
    "duclik.8794"           : "Duclic",
    "Echo.3974"             : "Echo",
    "Elheanlie.2713"        : "Elheanlie",
    "endymion.3162"         : "Endymion",
    "Keelin.6318"           : "Eyza",
    "Eztair.5173"           : "Eztair",
    "Fibonacci.8610"        : "Fibo",
    "JFK.7925"              : "Fidji",
    "fightwalkyrie.4928"    : "Fight",
    "firestorck.2584"       : "Firestorck",
    "Firiel.2735"           : "Firiel",
    "TheFisto.5928"         : "Fisto",
    "Flore.5039"            : "Flore",
    "Flore.9312"            : "Flore",
    "Gabranth.2580"         : "Gab",
    "SoCrazyAboutSky.5706"  : "Gab",
    "gamepac.3875"          : "Gamepac",
    "Henroo.1379"           : "Henroo",
    "Henroo.9314"           : "Henroo",
    "hidrozig.5201"         : "Hidrozig",
    "histoRy.6401"          : "HistoRy",
    "Huny.6124"             : "Huny",
    "ich.7086"              : "Ich",
    "Innac Al Gaib.9861"    : "Innac",
    "Isgormr.8957"          : "Isgormr",
    "Ismael.1427"           : "Ismael",
    "JackyGnu.2486"         : "Jacky",
    "Rolmachine.3574"       : "Jacky",
    "Jayden.9812"           : "Jadam",
    "Jason.4372"            : "Jason",
    "Rubicorne.6702"        : "Jason",
    "tokageroh.7521"        : "Jason",
    "Jiho.1035"             : "Jiho",
    "Jolibo.1560"           : "Jolibo",
    "kaTe.8954"             : "kaTe",
    "ken for deamon.7560"   : "Kenny",
    "Moonaris.9587"         : "King",
    "Klexmer.1587"          : "Klexmer",
    "kocasy.9672"           : "Kocasy",
    "Kozenko.8764"          : "Kozenko",
    "Kraighh.1569"          : "Kraighh",
    "Kieli.7534"            : "Kuki",
    "kwar.1739"             : "Kwar",
    "langeover.4516"        : "Langeover",
    "larxted.2180"          : "Larxted",
    "Sodhom.2069"           : "Le Père",
    "legolasantoine.1927"   : "LegolasAntoine",
    "Lonzou.1740"           : "Lonzou",
    "JMoums.4931"           : "Lorin",
    "Thelumonis.5923"       : "Lumy",
    "Lyco.3528"             : "Lyco",
    "BackIsBachus.6073"     : "Malica",
    "Marple.5896"           : "Marple",
    "Mazz.3794"             : "Mazur",
    "alenet.3825"           : "Mec_de_chez_PUG",
    "MENTALLYINFECTED.8143" : "Mentally",
    "Miatsu.5310"           : "Miatsu",
    "Murran.3841"           : "Murran",
    "oloth.3021"            : "Mutinielle",
    "rank.5170"             : "Nathan",
    "Masatochan.3497"       : "Netsu",
    "Le Scribe.1952"        : "Nico",
    "Noobard.2741"          : "Noobard",
    "Thollen.5740"          : "Obhotan",
    "Heron.5146"            : "Osvalf",
    "Oxi.8326"              : "Oxi",
    "pinpin.6892"           : "Pinpin",
    "DrRenault.8371"        : "Pongi",
    "PonGX.7832"            : "Pongi",
    "Tequila.7385"          : "Princesse",
    "Theloverboiiii.6574"   : "Radiant",
    "bistourie.2705"        : "Ravi",
    "James Heal.5467"       : "Ravi",
    "MaLiPe.5921"           : "Ravi",
    "Ravi.5812"             : "Ravi",
    "Rayden.3145"           : "Rayden",
    "VodCom.6924"           : "Reegar",
    "rem.1307"              : "Rem",
    "Rhonk.4283"            : "Rhonk",
    "xEternal.1658"         : "Roger",
    "Kowalsky.3850"         : "Romen",
    "Rutzicooki.1829"       : "Rutz_voleur",
    "Sakiyu.1587"           : "Sakiyu",
    "sang vieux.5029"       : "Sang Vieux",
    "saulane.7193"          : "Saulane",
    "Sejter.9746"           : "Sejter",
    "serac.6780"            : "Seraq",
    "Seraq.4692"            : "Seraq",
    "Shadowgem.2681"        : "Shadow",
    "Shana AD.9081"         : "Shana",
    "Shirano.9835"          : "Shirano",
    "Sik.8352"              : "Sik",
    "sleipnir.5491"         : "Sleipnir",
    "Soul.7495"             : "Soul",
    "Spaiz.4907"            : "Spaiz",
    "SunDee.3572"           : "SunDee",
    "xxxime.9401"           : "Sweay",
    "iSwiizz.5360"          : "Swiizz",
    "Swiizz.5304"           : "Swiizz",
    "Tali.1634"             : "Tali",
    "Tarteman.4293"         : "Tarteman",
    "Dr Nem.8952"           : "Teh Asian",
    "Teh Aajian.9714"       : "Teh Asian",
    "ADTempys.6382"         : "Tempys",
    "Tenso.2650"            : "Tenso",
    "Teremko.6759"          : "Terem",
    "kuhungu.6541"          : "Tharbo",
    "darkstar.2674"         : "ThirdOrigin",
    "tiotere.2793"          : "Tiotere",
    "Werof.4382"            : "Tobi",
    "Tonnio.3256"           : "Tonnio",
    "totochki.2893"         : "Totoch",
    "UnknownD.9273"         : "Unknown",
    "Halza.1645"            : "Untamed",
    "Vekt.4631"             : "Vekt",
    "Mitasse.7951"          : "Volonn",
    "Volonn.1938"           : "Volonn",
    "vracotinau.1687"       : "Vracotinau",
    "WahaBoy.6893"          : "Waha",
    "WhiteWarat.7046"       : "White",
    "xChris.8904"           : "xChris",
    "Yurih.9586"            : "Yurih",
    "Zaka.4901"             : "Zaka",
    "KTR.1407"              : "Zenhorr",
    "oscaro.3079"           : "Zheuja"
}

with open('wingman_updater/WINGMAN_DATA.json') as f:
    wingman_data = json.load(f)
    
EMOTE_WINGMAN = ":wing:"