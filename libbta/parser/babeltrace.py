import regex
import re

from .parser import Parser
from libbta import Trace


meta_pattern = re.compile(r"""
        \[(?P<timestamp>\d+(\.\d*)?|\.\d+)\]
        \ +\(.*\)    # Ignore delta
        \ +(?P<host>\S+)
        \ +(?P<fullname>\S+)
""", re.VERBOSE)
attrs_group = re.compile(r"(?<={).*?(?=})")
# key_val_pattern = regex.compile(r"(?:[^,[]|\[.*\])+")
key_val_pattern = regex.compile(r"([^,([]+(?:[([](?:[^()[\]]*|(?1))*[)\]])*)")
key_val_split = re.compile(r" *(\S+) *= *(.*) *")


class Babeltrace(Parser): 
    @classmethod
    def parse(cls, infile):
        """
        Read lines from infile, where each line is an trace
        """
        traces = []
        with open(infile, encoding='utf-8') as tracefile:
            for line in tracefile:
                e = cls.parseline(line)
                traces.append(e)
        return traces
    

    @classmethod
    def parseline(cls, line):
        """
        Generate trace from line
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
    
        trace = Trace(name, timestamp)
    
        trace['host'] = m.group('host')
        trace['domain'] = m.group('host') + '.' + scope
    
        # print(attrs)
        cls.parse_attrs(attrs, trace)
        return trace
    

    @classmethod
    def parse_attrs(cls, attrs, trace):
        for key_vals in attrs_group.findall(attrs.strip()):
    
            for key_val in key_val_pattern.findall(key_vals.strip()):
                m = key_val_split.match(key_val)
                trace[m.group(1)] = m.group(2)
        return trace
