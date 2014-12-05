from collections import deque

from . import BlkLayer


class QemuVirtioLayer(BlkLayer):
    """
    Layer for Qemu's Virtio

    Read and Write event have different add and submit operations, but same
    finish operation. They have separate added queues, but same submit and
    finish queue.
    """
    SECTOR_SIZE = 512

    def __init__(self, name):
        super().__init__(name,
                         [('id', 'req'), ('offset', 'sector'),
                          ('length', 'nsectors')])
        self.added_write_reqs = deque()
        self.added_read_reqs = deque()
        self.submitted_reqs = deque()
        self.finished_reqs = deque()

    def __repr__(self):
        string = '\n'.join([super().__repr__(),
                            'Added write: ' + str(self.added_write_reqs),
                            'Added read: ' + str(self.added_read_reqs,),
                            'Submitted: ' + str(self.submitted_reqs),
                            'Finished: ' + str(self.finished_reqs)])
        return string

    def read_event(self, event):
        """
        Read a event, associate it with a request, deduce it's relation with
        upper layer. Well, the deducing actually happens in upper layer
        """
        if event.name == 'virtio_blk_handle_write':
            self.add_write_request(event)
        elif event.name == 'virtio_blk_handle_read':
            self.add_read_request(event)
        elif event.name == 'bdrv_aio_multiwrite':
            self.submit_write_request(event)
        elif event.name == 'bdrv_aio_readv':
            self.submit_read_request(event)
        elif event.name == 'virtio_blk_rw_complete':
            self.finish_request(event)

    def add_write_request(self, event):
        """
        Read a event, generate a write request
        """
        req = self.gen_req('qemu_virtio_write', event, 'write')
        self._add_req(req, event, self.added_write_reqs)

    def add_read_request(self, event):
        """
        Read a event, generate a read request
        """
        req = self.gen_req('qemu_virtio_read', event, 'read')
        self._add_req(req, event, self.added_read_reqs)

    def submit_write_request(self, event):
        """
        Read a event, submit some write requests
        """
        for i in range(int(event['num_callbacks'])):
            req = self.added_write_reqs.popleft()
            self._submit_req(req, event, self.submitted_reqs)

    def submit_read_request(self, event):
        """
        Read a event, submit some read requests
        """
        offset = int(event['sector_num']) * self.SECTOR_SIZE
        length = int(event['nb_sectors']) * self.SECTOR_SIZE
        for req, idx in zip(self.added_read_reqs,
                            range(len(self.added_read_reqs))):
            if req.offset == offset and req.length == length:
                del self.added_read_reqs[idx]
                self._submit_req(req, event, self.submitted_reqs)
                return
        print("Throw event {0}".format(event))

    def finish_request(self, event):
        _id = event['req']
        for req, idx in zip(self.submitted_reqs,
                            range(len(self.submitted_reqs))):
            if req['id'] == _id:
                del self.submitted_reqs[idx]
                self._finish_req(req, event, self.finished_reqs)
                return
        print("Throw event {0}".format(event))

    def gen_req(self, name, event, _type):
        req = super().gen_req(name, event)
        req.offset *= self.SECTOR_SIZE
        req.length *= self.SECTOR_SIZE
        req.type = _type
        return req
