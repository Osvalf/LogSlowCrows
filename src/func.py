import math

def time_to_index(time: int): #time in millisecond
    return int(time/150)

def get_dist(pos1: list[float,float], pos2: list[float,float]):
    return math.sqrt((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)