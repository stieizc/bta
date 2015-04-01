import sys

from . import BlkLayer
from libbta.utils import rwbs


class LinuxBlockLayer(BlkLayer):
    """
    Layer for Linux's block layer

    Life cycle of a req:
    (remap ->) queue -> getrq -> insert -> issue -> complete
                     -> merge
    """

    trace_attrs = {
            'offset': ('sector', int), 'length': ('nr_sector', int),
            'dev': 'dev', 'ops': ('rwbs', rwbs.parse_bio),
            'optional': {'cmd_length': ('_cmd_length', int)},
            }

    def __init__(self, name):
        super().__init__(name)
        self.trace_handlers = {
            'block_bio_queue': (
                'queue', ('block_bio', self.trace_attrs)
                ),
            'block_rq_issue': (
                'submit',
                ('queue', self.rule, self.trace_attrs)
                ),
            'block_rq_complete': (
                'finish',
                ('submit', self.rule, self.trace_attrs)
                ),
            'block_bio_backmerge': self.backmerge_request,
            'block_bio_frontmerge': self.frontmerge_request,
            }

    def submit_request(self, trace):
        event = trace.gen_set_event(self.trace_attrs)
        if self.is_scsi(event):
            return
        return self.fifo_mv_request(event, info, warn=True)

    def finish_request(self, event, info):
        if event['nr_sector'] == '0':
            cmd_len = event.get('_cmd_length')
            if cmd_len and cmd_len != '0':
                return None
        master_req = self.fifo_mv_request(event, info)
        if master_req:
            for req in master_req.merged_reqs:
                self._finish_req(event.timestamp, self.req_queue['finish'],
                                 req)
        return master_req

    def backmerge_request(self, event, info):
        to_merge = self.req_queue['add'].req_out(self.rule, event)

        if to_merge:
            for req in self.req_queue['add']:
                if self.rule_backmerge(to_merge, req):
                    req.length += to_merge.length
                    req.merged_reqs.append(to_merge)
                    return to_merge
        print('Cannot backmerge req {0}, event {1}'.format(to_merge, event),
              file=sys.stderr)

    @classmethod
    def rule_backmerge(cls, to_merge, dest):
        return to_merge['dev'] == dest['dev'] \
            and to_merge.offset == dest.offset + dest.length \
            and to_merge.op_type_same(dest)

    def frontmerge_request(self, event, info):
        to_merge = self.req_queue['add'].req_out(self.rule, event)

        if to_merge:
            for req in self.req_queue['add']:
                if self.rule_frontmerge(to_merge, req):
                    req.offset = to_merge.offset
                    req.length += to_merge.length
                    req.merged_reqs.append(to_merge)
                    return to_merge
        print('Cannot frontmerge req {0}, event {1}'.format(to_merge, event),
              file=sys.stderr)

    @classmethod
    def rule_frontmerge(cls, to_merge, dest):
        return dest['dev'] == to_merge['dev'] \
            and dest.offset == to_merge.offset + to_merge.length \
            and to_merge.op_type_same(dest)

    @classmethod
    def rule(cls, req, event):
        offset = int(event['sector']) * cls.SECTOR_SIZE
        length = int(event['nr_sector']) * cls.SECTOR_SIZE
        dev = event['dev']
        rwbs = int(event['rwbs'])
        return req['offset'] == offset and req['length'] == length \
            and req['dev'] == dev and req.op_type_equal(rwbs)

    @staticmethod
    def is_scsi(self, event):
        if event['length'] == 0:
            cmd_len = event.get('_cmd_length')
            if cmd_len and cmd_len != 0:
                return True
        return False
