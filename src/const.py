import json

BIG = float('inf')

all_bosses = []
all_players = {}

boss_dict = {
    #  RAID BOSSES
    15438 : "vg",
    15429 : "gors",
    15375 : "sab",
    
    16123 : "sloth",
    16115 : "matt",
    
    16253 : "esc",
    16235 : "kc",
    16246 : "xera",
    
    17194 : "cairn",
    17172 : "mo",
    17188 : "sam",
    17154 : "dei",
    
    19767 : "sh",
    19450 : "dhuum",
    
    43974 : "ca",
    21105 : "twins",
    20934 : "qadim",
    
    22006 : "adina",
    21964 : "sabir",
    22000 : "qpeer",
    
    #  IBS BOSSES
    22154 : "ice",
    22343 : "falln",
    22492 : "frae",
    22711 : "whisp",
    22521 : "bone",
    
    #  EOD BOSSES
    24033 : "trin",
    23957 : "ankka",
    24266 : "li",
    43488 : "void",
    25414 : "olc",
    
    #  SOTO BOSSES
    25705 : "dagda",
    25989 : "cerus",
    
    # FRAC BOSSES
    17021 : "mama",
    17028 : "siax",
    16948 : "enso",
    
    17632 : "skor",
    17949 : "arriv",
    17759 : "arkk",
    
    23254 : "ai",
    
    25577 : "kana",
    
    26231 : "eparc"
    }

extra_boss_dict = {
    16199 : "golem",
    19645 : "golem"
}

custom_names = {
    "James Heal.5467"    : "Ravi",
    "hidrozig.5201"      : "Hidrozig",
    "histoRy.6401"       : "HistoRy",
    "Twiyaka.9738"       : "Brizeh",
    "Ava.7895"           : "Ava",
    "Rhonk.4283"         : "Rhonk",
    "Swiizz.5304"        : "Swiizz",
    "Le Scribe.1952"     : "Nico",
    "Lyco.3528"          : "Lyco",
    "endymion.3162"      : "Endymion",
    "Arkadia.9432"       : "Babar",
    "Fibonacci.8610"     : "Fibo",
    "Jiho.1035"          : "Jiho",
    "Blaxono Junior.4732": "Boti",
    "Moonaris.9587"      : "King",
    "Jason.4372"         : "Jason",
    "Arka.3754"          : "Arka",
    "Gabranth.2580"      : "Gab",
    "xxxime.9401"        : "Sweay",
    "JackyGnu.2486"      : "Jacky",
    "oscaro.3079"        : "Zheuja",
    "Yurih.9586"         : "Yurih",
    "Guitou.5682"        : "Guitou",
    "Yvaz.7593"          : "Ibu",
    "spirits x zeke.9054": "Zeke",
    "BobbyFrasier.8450"  : "BobbyFrasier",
    "ich.7086"           : "Ich",
    "Yoomi.8251"         : "Yoomi",
    "Jaydens.9812"       : "Jadam",
    "PonGX.7832"         : "Pongi",
    "Rayden.3145"        : "Rayden",
    "Teh Aajian.9714"    : "Teh Asian",
    "Koeur.1235"         : "Koeur",
    "Huny.6124"          : "Huny"
}

with open('wingman_updater/WINGMAN_DATA.json') as f:
    wingman_data = json.load(f)
    
emote_wingman = ":wing:"

################################ DATA VG ################################



################################ DATA GORS ################################



################################ DATA SABETHA ################################

pos_sab = [376.7,364.4]
pos_canon1 = [346.9,706.7]
pos_canon2 = [35.9,336.8]
pos_canon3 = [403.3,36.0]
pos_canon4 = [713.9,403.1] 

canon_detect_radius = 45

sabetha_scaler = 9.34179

################################ DATA SLOTH ################################



################################ DATA MATTHIAS ################################



################################ DATA ESCORT ################################

escort_tower1 = [387,129.1]
escort_tower2 = [304.1,115.7]
escort_tower3 = [187.1,118.8]
escort_tower4 = [226.1,252.3]
escort_tower5 = [80.3,255.5]

tower_radius = 19

################################ DATA KC ################################



################################ DATA XERA ################################

xera_debut = [497.1,86.4]
xera_l1 = [663.0,314.9]
xera_l2 = [532.5,557.4]
xera_fin = [268.3,586.4]
xera_r1 = [208.2,103.4]
xera_r2 = [87.0,346.8]
xera_centre = [366.4,323.4]

xera_debut_radius = 85
xera_centre_radius = 140

################################ DATA CAIRN ################################



################################ DATA MO ################################



################################ DATA SAMAROG ################################

sama_top_left_corn = [278.0,645.2]
sama_top_right_corn = [667.6,660.7]
sama_bot_left_corn = [299.4,58.6]
sama_bot_right_corn = [690.7,73.6]

samarog_scaler = 5.4621

################################ DATA DEIMOS ################################



################################ DATA SH ################################

sh_center_arena = [375,375]
sh_radius1 = 345.5
sh_radius2 = 304.2
sh_radius3 = 256.2
sh_radius4 = 208.5
sh_radius5 = 163

################################ DATA DHUUM ################################



################################ DATA CA ################################



################################ DATA LARGOS ################################



################################ DATA QADIM ################################

qadim_center = [411.5,431.1]
qadim_fdp_radius = 70

################################ DATA ADINA ################################



################################ DATA SABIR ################################



################################ DATA QTP ################################


