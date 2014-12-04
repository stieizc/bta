from collections import deque

from libbta import BlkRequest
from . import Layer


class QemuVirtioLayer(Layer):
    """
    Layer for Qemu's Virtio

    Read and Write event have different add and submit operations, but same
    finish operation, thus they have separate added queues, but same submit and
    finish queue
    """
    def __init__(self, name, upper=None):
        super().__init__(name, upper=None)

        self.added_write_reqs = deque()
        self.added_read_reqs = deque()
        self.submitted_reqs = deque()
        self.finished_reqs = deque()

        self.issued_reqs = self.submitted_reqs

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
        req = self._gen_request('qemu_virtio_write', event, is_write=1)
        self.added_write_reqs.append(req)

    def add_read_request(self, event):
        """
        Read a event, generate a read request
        """
        req = self._gen_request('qemu_virtio_read', event, is_write=0)
        self.added_read_reqs.append(req)

    def submit_write_request(self, event):
        """
        Read a event, submit some write requests
        """
        for i in range(event.get_int('num_callbacks')):
            req = self.added_write_reqs.popleft()
            req.submit_time = event.timestamp
            self.submitted_reqs.append(req)

    def submit_read_request(self, event):
        """
        Read a event, submit some read requests
        """
        offset = event.get_int('sector_num')
        length = event.get_int('nb_sectors')
        for req, idx in zip(self.added_read_reqs,
                            range(len(self.added_read_reqs))):
            if req.offset == offset and req.length == length:
                del self.added_read_reqs[idx]
                req.submit_time = event.timestamp
                self.submitted_reqs.append(req)
                return
        print("Throw event {0}".format(event))

    def finish_request(self, event):
        _id = event.get('req')
        for req, idx in zip(self.submitted_reqs,
                            range(len(self.submitted_reqs))):
            if req.get('id') == _id:
                del self.submitted_reqs[idx]
                req.finish_time = event.timestamp
                self.finished_reqs.append(req)
                return
        print("Throw event {0}".format(event))

    def _gen_request(self, name, event, is_write=1):
        attrs = {'is_write': is_write}
        for e_attr, r_attr in [('sector', 'offset'), ('nsectors',
                               'length')]:
            attrs[r_attr] = event.get_int(e_attr)
        for e_attr, r_attr in [('req', 'id')]:
            attrs[r_attr] = event.get(e_attr)

        req = BlkRequest(name, attrs)
        req.add_time = event.timestamp
        return req
