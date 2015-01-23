from libbta import ReqQueue
from . import BlkLayer


class QemuVirtioLayer(BlkLayer):
    """
    Layer for Qemu's Virtio

    Read and Write event have different add and submit operations, but same
    finish operation. They have separate added queues, but same submit and
    finish queue.
    """
    req_attrs_map = {'id': ('req', str), 'offset': ('sector', int),
                     'length': ('nsectors', int)}


    def __init__(self, name):
        super().__init__(name)
        self.event_info_map = {
            'virtio_blk_handle_write': {'type': 'add',
                                        'name': 'qemu_virtio_write',
                                        'op': 'write', 'queue': 'add_write'},
            'virtio_blk_handle_read': {'type': 'add',
                                       'name': 'qemu_virtio_read',
                                       'op': 'read', 'queue': 'add_read'},
            'bdrv_aio_multiwrite': {'handler': 'submit_write'},
            'bdrv_aio_readv': {'type': 'submit', 'src': 'add_read',
                               'rule': self.rule_submit},
            'virtio_blk_rw_complete': {'type': 'finish', 'src': 'submit',
                                       'rule': self.rule_finish}}
        self.req_queue = {'add_read': ReqQueue(), 'add_write': ReqQueue(),
                          'submit': ReqQueue(), 'finish': ReqQueue()}
        self.event_handlers['submit_write'] = self.submit_write_request

    def __repr__(self):
        return '\n'.join([
            super().__repr__(),
            'Added write: '+ str(len(self.req_queue['add_write'])),
            'Added read: ' + str(len(self.req_queue['add_read'])),
            'Submitted: ' + str(len(self.req_queue['submit'])),
            'Finished: ' + str(len(self.req_queue['finish']))])

    @classmethod
    def gen_req(cls, event, info):
        req = super().gen_req(event, info)
        req.rwbs = BlkLayer.add_rwbs_flag(0, info['op'])
        return req

    def submit_write_request(self, event, info):
        """
        Read a event, submit some write requests
        """
        for i in range(int(event['num_callbacks'])):
            req = self.req_queue['add_write'].popleft()
            self._submit_req(event.timestamp, self.req_queue['submit'], req)

    @classmethod
    def rule_submit(cls, req, event):
        """
        Read a event, submit some read requests
        """
        offset = int(event['sector_num']) * cls.SECTOR_SIZE
        length = int(event['nb_sectors']) * cls.SECTOR_SIZE
        return req['offset'] == offset and req['length'] == length

    @staticmethod
    def rule_finish(req, event):
        return req['id'] == event['req']
