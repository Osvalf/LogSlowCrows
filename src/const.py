import json

BIG = float('inf')

all_bosses = []
all_players = {}

boss_dict = {
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
    }

extra_boss_dict = {
    16199 : "golem",
    19645 : "golem"
}

with open('wingman_updater/WINGMAN_DATA.json') as f:
    wingman_data = json.load(f)
    
nm_dict = {}
for boss, data in wingman_data["NM_BOSSES"].items():
    nm_dict[boss] = data["Duration"]
    
cm_dict = {}
for boss, data in wingman_data["CM_BOSSES"].items():
    cm_dict[boss] = data["Duration"]
    
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


