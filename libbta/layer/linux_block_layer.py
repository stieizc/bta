import sys

from libbta import ReqQueue
from . import BlkLayer


class LinuxBlockLayer(BlkLayer):
    """
    Layer for Linux's block layer

    Life cycle of a req:
    (remap ->) queue -> getrq -> insert -> issue -> complete
                     -> merge

    'queued' is the real 'add' event.
    """

    req_attrs_map = {'offset': ('sector', int), 'length': ('nr_sector', int),
                     'dev': ('dev', str), 'rwbs': ('rwbs', int)}

    def __init__(self, name):
        super().__init__(name)
        self.event_info_map = {
            'block_bio_queue': {'type': 'add', 'name': 'block_bio'},
            'block_bio_backmerge': {'type': 'backmerge'},
            'block_bio_frontmerge': {'type': 'frontmerge'},
            'block_rq_issue': {'type': 'submit', 'src': 'add',
                               'rule': self.rule},
            'block_rq_complete': {'type': 'finish', 'src': 'submit',
                                  'rule': self.rule}}
        self.req_queue = {'add': ReqQueue(), 'submit': ReqQueue(),
                          'finish': ReqQueue()}
        self.event_handlers['backmerge'] = self.backmerge_request
        self.event_handlers['frontmerge'] = self.frontmerge_request
        self.event_handlers['finish'] = self.finish_request

    def __repr__(self):
        return '\n'.join([
            super().__repr__(),
            'Added: ' + str(len(self.req_queue['add'])),
            'Submitted: ' + str(len(self.req_queue['submit'])),
            'Finished: ' + str(len(self.req_queue['finish']))])

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

    def finish_request(self, event, info):
        master_req = self.fifo_mv_request(event, info)
        if master_req:
            for req in master_req.merged_reqs:
                self._finish_req(event.timestamp, self.req_queue['finish'],
                                 req)

    @classmethod
    def rule(cls, req, event):
        offset = int(event['sector']) * cls.SECTOR_SIZE
        length = int(event['nr_sector']) * cls.SECTOR_SIZE
        dev = event['dev']
        rwbs = int(event['rwbs'])
        return req['offset'] == offset and req['length'] == length \
            and req['dev'] == dev and req.op_type_equal(rwbs)
