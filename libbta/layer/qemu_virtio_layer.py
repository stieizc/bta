from . import BlkLayer
from . import rules


trace_map_queue = {
    'id': ('req',), 'offset': ('sector', BlkLayer.sec2byte),
    'length': ('nsectors', BlkLayer.sec2byte)}

trace_map_queue_write = {
    'additonal': {'ops': ['write']}
    }.update(self.trace_map_queue))

trace_map_queue_read = {
    'additonal': {'ops': ['read']}
    }.update(self.trace_map_queue))

trace_map_submit_read = {
    'offset': ('sector_num', BlkLayer.sec2byte)
    'length': ('nb_sectors', BlkLayer.sec2byte)
    }

trace_map_finish = {
    'id': ('req', )
    }

class QemuVirtioLayer(BlkLayer):
    """
    Layer for Qemu's Virtio

    Read and Write event have different add and submit operations, but same
    finish operation. They have separate added queues, but same submit and
    finish queue.
    """

    def __init__(self, name):
        super().__init__(name)
        self.trace_handlers = {
            # queue
            'virtio_blk_handle_write': (
                'queue', ('qemu_virtio_write', trace_map_queue_write)
                ),
            'virtio_blk_handle_read': (
                'queue', ('qemu_virtio_read', trace_map_queue_read)
                ),
            # submit
            'bdrv_aio_multiwrite': self.submit_write_request,
            'bdrv_aio_readv': (
                'submit', (trace_map_submit_read, 'add', rules.same_pos)
                ),
            # finish
            'virtio_blk_rw_complete': (
                'finish', (trace_map_finish, 'submit', rules.same_id
                )
            }

    def submit_write_request(self, trace):
        """
        Read a event, submit some write requests
        """
        for i in range(int(trace['num_callbacks'])):
            req = self.queues['queue']['write'].popleft()
            self.accept_req(req, event.timestamp, 'submit')
