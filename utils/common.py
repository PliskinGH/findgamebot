# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 18:21:04 2022

@author: Pliskin
"""

import re

CONFIG_DEFAULT = "DEFAULT"
CONFIG_ID = "ID"

def split_config_list(value):
    return [x.strip() for x in value.split(',')]

def get_guild_from_config(config, guild_id):
    found = False
    
    for guild in config.sections():
        found = (guild_id == config.getint(guild, CONFIG_ID, fallback=None))
        if (found):
            break
    
    if (not(found)):
        guild = CONFIG_DEFAULT
    
    return guild

def parse_intervals(string, cardinal):
    value_list = []
    if not(re.match('^[0-9\-\,]*$', string)):
        return value_list
    
    intervals = []
    intervals_str = string.split(',')
    for interval_str in intervals_str:
        bounds = [int(x) for x in interval_str.split('-')]
        if (len(bounds) == 1):
            intervals.append(bounds)
        elif (len(bounds) > 1):
            max_bound = max(bounds)
            min_bound = min(bounds)
            intervals.append([min_bound, max_bound])
    
    if (len(intervals) == 1 and len(intervals[0]) == 1):
        for i in range(1, min(cardinal, intervals[0][0]) + 1):
            value_list.append(i)
    elif (len(intervals)):
        for interval in intervals:
            if (len(interval) == 1):
                value_list.append(interval[0])
            elif (len(interval)):
                for i in range(interval[0], min(cardinal, interval[1]) + 1):
                    value_list.append(i)
    
    return value_list