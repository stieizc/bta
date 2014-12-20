#!/usr/bin/env python3
from libbta import Event
import re

meta_pattern = re.compile(r"""
        \[(?P<timestamp>\d+(\.\d*)?|\.\d+)\]
        \ +\(.*\)    # Ignore delta
        \ +(?P<host>\S+)
        \ +(?P<fullname>\S+)
""", re.VERBOSE)
attrs_group = re.compile(r"(?<={).*?(?=})")
key_val_pattern = re.compile(r"(?:[^,[]|\[.*\])+")
key_val_split = re.compile(r" *(\S+) *= *(.*)")


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
    meta, attrs = re.split(r': (?={)', line, 1)

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

    #print(attrs)
    parse_attrs(attrs, event)
    #parse_attrs_with_one_parened(attrs, event)
    return event


def parse_attrs_with_one_parened(attrs, event):
    for key_vals in attrs_group.findall(attrs.strip()):
        for key_val in key_val_pattern.findall(key_vals):
            m = key_val_split.match(key_val)
            event[m.group(1)] = m.group(2).strip()
    return event

def parse_attrs(attrs, event):
    #print(attrs.strip())
    paren_level = 0
    bracket_level = 0
    brace_level = 0

    last = 0
    current = 0
    tokens = [token for token in re.split('([{}[\],])| ', attrs.strip()) if
              token]
    for token in tokens:
        #print('$ '+token)
        if token == '{':
            last = current + 1
            brace_level += 1
        elif token == '}' or token == ',':
            if brace_level == 1 and paren_level == 0 and bracket_level == 0:
                val = ''.join(tokens[last:current])
                #print(val)
                event[key.strip()] = val.strip()
                last = current + 1
            if token == '}':
                brace_level -= 1
        elif token == '[':
            bracket_level += 1
        elif token == ']':
            bracket_level -= 1
        elif token == '(':
            paren_level += 1
        elif token == ')':
            paren_level -= 1
        elif token == '=':
            if brace_level == 1 and paren_level == 0 and bracket_level == 0:
                key = ''.join(tokens[last:current])
                #print('k '+key)
                last = current + 1
        current += 1
        #print("Hi {} {} {}".format(paren_level, bracket_level, brace_level))
