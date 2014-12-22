from collections import deque
from functools import partial

from . import BlkLayer


class LinuxBlockLayer(BlkLayer):
    """
    Layer for Linux's block layer

    Life cycle of a req:
    (remap ->) queue -> getrq -> insert -> issue -> complete
                     -> merge

    'queued' is the real 'add' event.
    """
    RWBS_FLAG_WRITE = (1 << 0)
    RWBS_FLAG_DISCARD = (1 << 1)
    RWBS_FLAG_READ = (1 << 2)
    RWBS_FLAG_RAHEAD = (1 << 3)
    RWBS_FLAG_BARRIER = (1 << 4)
    RWBS_FLAG_SYNC = (1 << 5)
    RWBS_FLAG_META = (1 << 6)
    RWBS_FLAG_SECURE = (1 << 7)
    RWBS_FLAG_FLUSH = (1 << 8)
    RWBS_FLAG_FUA = (1 << 9)

    def __init__(self, name):
        super().__init__(name,
                         [('offset', 'sector'), ('length', 'nr_sector'),
                          ('dev', 'dev'), ('type', 'rwbs')])
        self.added_reqs = deque()
        self.submitted_reqs = deque()
        self.finished_reqs = deque()

    def __repr__(self):
        string = '\n'.join([super().__repr__(),
                            'Added: ' + str(self.added_reqs),
                            'Submitted: ' + str(self.submitted_reqs),
                            'Finished: ' + str(self.finished_reqs)])
        return string

    def read_event(self, event):
        """
        Read a event, associate it with a request, deduce it's relation with
        upper layer. Well, the deducing actually happens in upper layer
        """
        if event.name == 'block_bio_queue':
            self.added_request(event)
        elif event.name == 'block_bio_backmerge':
            self.backmerge_request(event)
        elif event.name == 'block_bio_frontmerge':
            self.frontmerge_request(event)
        elif event.name == 'block_rq_issue':
            self.submit_request(event)
        elif event.name == 'block_rq_complete':
            self.finish_request(event)

    def added_request(self, event):
        req = self.gen_req('blk_bio', event)
        self._add_req(event.timestamp, self.added_reqs, req)

    def submit_request(self, event):
        """
        Read a event, submit a request
        """
        self.fifo_req_mv_warn(
                self.added_reqs,
                self.gen_critique(event),
                partial(self._submit_req, event.timestamp,
                        self.submitted_reqs),
                event)

    def backmerge_request(self, event):
        to_merge = self.fifo_req_out_warn(
                self.added_reqs,
                self.gen_critique(event),
                event)

        if to_merge:
            offset = to_merge.offset
            dev = to_merge['dev']
            _type = to_merge.type
            for req in self.added_reqs:
                if (req['dev'] == dev and req.offset + req.length == offset
                    and self._op_type_same(req.type, _type)):
                    req.length += to_merge.length
                    req.merged_reqs.append(to_merge)
                    return

    def frontmerge_request(self, event):
        to_merge = self.fifo_req_out_warn(
                self.added_reqs,
                self.gen_critique(event),
                event)

        if to_merge:
            offset = to_merge.offset + to_merge.length
            dev = to_merge['dev']
            _type = to_merge.type
            for req in self.added_reqs:
                if (req['dev'] == dev and req.offset == offset
                    and self._op_type_same(req.type, _type)):
                    req.offset = to_merge.offset
                    req.length += to_merge.length
                    req.merged_reqs.append(to_merge)
                    return

        print('Cannot merge req {0}, event {1}'.format(to_merge, event))

    def finish_request(self, event):
        """
        Read a event, finish a request
        """
        master_req = self.fifo_req_mv_warn(
                self.submitted_reqs,
                self.gen_critique(event),
                partial(self._finish_req, event.timestamp,
                        self.finished_reqs),
                event)

        if master_req:
            for req in master_req.merged_reqs:
                self._finish_req(event.timestamp, self.finished_reqs, req)

    def gen_req(self, name, event):
        req = super().gen_req(name, event)
        req.offset = self.sec2byte(req.offset)
        req.length = self.sec2byte(req.length)
        req.type = int(req.type)
        return req

    @staticmethod
    def op_type(rwbs):
        return (7 & rwbs)

    @staticmethod
    def _op_type_same(rwbs1, rwbs2):
        return  LinuxBlockLayer.op_type(rwbs1) == LinuxBlockLayer.op_type(rwbs2)

    @staticmethod
    def critique(offset, length, dev, _type, req):
        return (req['offset'] == offset and req['length'] == length
                and req['dev'] == dev and
                LinuxBlockLayer._op_type_same(req['type'], _type))

    def gen_critique(self, event):
        offset = self.sec2byte(event['sector'])
        length = self.sec2byte(event['nr_sector'])
        dev = event['dev']
        _type = int(event['rwbs'])
        return partial(self.critique, offset, length, dev, _type)
