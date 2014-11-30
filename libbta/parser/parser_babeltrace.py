#!/usr/bin/env python3
from libbta import Event
import re

meta_pattern = re.compile(r"""
        \[(?P<timestamp>\d+(\.\d*)?|\.\d+)\]
        #\ +\((?P<delta>.*)\)     # \ +\((?P<delta>\d+(\.\d*)?|\.\d+)\) Could Contain other things
        \ +\(.*\)    # Ignore delta
        \ +(?P<host>\w+)
        \ +(?P<scope>\w+)
        :(?P<name>\w+)
""", re.VERBOSE)

attr_split = re.compile(r"\{|}? *, *{?|\}")
key_val_pattern = re.compile(r" *(\w+) *= *(\w+)")

def parse(infile):
    """
    Read lines from infile, where each line is an event
    """
    events = [];
    with open(infile, encoding='utf-8') as tracefile:
        for line in tracefile:
            e = parseline(line)
            print(e)
            events.append(e)
    return events

def parseline(line):
    """
    Generate event from line
    """
    meta, _, attr = line.rpartition(':')
    attrs = {}

    m = meta_pattern.match(meta)
    timestamp = m.group('timestamp')
    name = m.group('name')
    for a in ['host', 'scope']:
        attrs[a] = m.group(a)

    key_vals = attr_split.split(attr.strip())
    for key_val in key_vals:
        if not key_val:
            continue
        m = key_val_pattern.match(key_val)
        attrs[m.group(1)] = m.group(2)

    return Event(name, timestamp, attrs)
