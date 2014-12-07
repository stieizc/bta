#!/usr/bin/env python3
from libbta import Event
import re

meta_pattern = re.compile(r"""
        \[(?P<timestamp>\d+(\.\d*)?|\.\d+)\]
        \ +\(.*\)    # Ignore delta
        \ +(?P<host>\S+)
        \ +(?P<fullname>\S+)
""", re.VERBOSE)


def parse(infile):
    """
    Read lines from infile, where each line is an event
    """
    events = []
    with open(infile, encoding='utf-8') as tracefile:
        for line in tracefile:
            e = parseline(line)
            events.append(e)
    return events


def parseline(line):
    """
    Generate event from line
    """
    meta, _,  attrs = line.partition(': {')

    m = meta_pattern.match(meta)
    timestamp = float(m.group('timestamp'))
    fullname = m.group('fullname')
    name_fields = fullname.split(':')
    if len(name_fields) == 1:
        scope = 'kernel'
        name = fullname
    else:
        scope = name_fields[0]
        name = name_fields[1]

    event = Event(name, timestamp)

    event['host'] = m.group('host')
    event['domain'] = m.group('host') + '.' + scope

    parse_attrs(attrs, event)
    return event


def parse_attrs(attrs, event):
    paren_level = 0
    bracket_level = 0
    brace_level = 0

    last = 0
    current = 0
    #print(attrs)
    for c in attrs:
        if c == '{':
            last = current + 1
            brace_level += 1
        elif c == '}' or c == ',':
            if brace_level == 0 and paren_level == 0 and bracket_level == 0:
                val = attrs[last:current]
                #print(key)
                #print(val)
                event[key.strip()] = val.strip()
                last = current + 1
            if c == '}':
                brace_level -= 1
        elif c == '[':
            bracket_level += 1
        elif c == ']':
            bracket_level -= 1
        elif c == '(':
            paren_level += 1
        elif c == ')':
            paren_level -= 1
        elif c == '=':
            if brace_level == 0 and paren_level == 0 and bracket_level == 0:
                key = attrs[last:current]
                last = current + 1
        current += 1
        #print("Hi {} {} {}".format(paren_level, bracket_level, brace_level))
