from libbta import ReqQueue
from . import BlkLayer


class QemuRawLayer(BlkLayer):
    """
    Layer for Qemu's Raw File Backend

    Doesn't have a finish event for itself, since it calls a callback function
    on finish. So it relies on the deducer to find a relationship, and mark it
    as finished. So finish_request is actually called by deducer.

    Rely on deducer for finishing request. It is possible that a request is
    actually finished but never marked so, if the deducer can't decide.
    """
    QEMU_AIO_FLAG = {1 << 0: 'read', 1 << 1: 'write', 1 << 2: 'ioctl',
                     1 << 3: 'flush', 1 << 4: 'discard', 1 << 5: 'writez'}

    req_attrs_map = {'id': ('acb', str), 'offset': ('sector_num', int),
                     'length': ('nb_sectors', int), 'type': ('type', int)}

    def __init__(self, name):
        super().__init__(name)
        self.event_info_map = {
            'paio_submit': {'type': 'add', 'name': 'qemu_raw_rw'},
            'handle_aiocb_rw': {'type': 'submit', 'src': 'add',
                                'rule': self.rule_submit}}
        self.req_queue = {'add': ReqQueue(), 'submit': ReqQueue(),
                          'finish': ReqQueue()}

    def __repr__(self):
        return '\n'.join([
            super().__repr__(),
            'Added: ' + str(len(self.req_queue['add'])),
            'Submitted: ' + str(len(self.req_queue['submit'])),
            'Finished: ' + str(len(self.req_queue['finish']))])

    @classmethod
    def gen_req(cls, event, info):
        req = super().gen_req(event, info)
        rwbs = 0
        _type = req['type']
        for bit, action in cls.QEMU_AIO_FLAG.items():
            if _type & bit:
                rwbs = BlkLayer.add_rwbs_flag(rwbs, action)
        req.rwbs = rwbs
        return req

    @staticmethod
    def rule_submit(req, event):
        return req['id'] == event['aiocb'] \
            and req['offset'] == int(event['aiocb__aio_offset']) \
            and req['length'] == int(event['aiocb__aio_nbytes'])

    def finish_request(self, req, timestamp):
        # print("Remove {0}".format(req))
        self.req_queue['submit'].remove(req)
        self._finish_req(timestamp, self.req_queue['finish'], req)
