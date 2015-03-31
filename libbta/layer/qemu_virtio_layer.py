from . import BlkLayer
from . import rules

trace_attrs_queue = {
    'id': ('req',), 'offset': ('sector', BlkLayer.sec2byte),
    'length': ('nsectors', BlkLayer.sec2byte)
    }


class QemuVirtioLayer(BlkLayer):
    """
    Layer for Qemu's Virtio
    """

    trace_attrs_queue_write = {
        'additonal': {'ops': ['write']}
        }.update(trace_attrs_queue)

    trace_attrs_queue_read = {
        'additonal': {'ops': ['read']}
        }.update(trace_attrs_queue)

    trace_attrs_submit_read = {
        'offset': ('sector_num', BlkLayer.sec2byte),
        'length': ('nb_sectors', BlkLayer.sec2byte)
        }

    trace_attrs_finish = {
        'id': ('req', )
        }

    def __init__(self, name):
        super().__init__(name)
        self.trace_handlers = {
            # queue
            'virtio_blk_handle_write': (
                'queue', ('qemu_virtio_write', self.trace_attrs_queue_write)
                ),
            'virtio_blk_handle_read': (
                'queue', ('qemu_virtio_read', self.trace_attrs_queue_read)
                ),
            # submit
            'bdrv_aio_multiwrite': self.submit_write_request,
            'bdrv_aio_readv': (
                'submit', ('add', rules.same_pos, self.trace_attrs_submit_read)
                ),
            # finish
            'virtio_blk_rw_complete': (
                'finish', ('submit', rules.same_id, self.trace_attrs_finish)
                )
            }
        self.when('lower', 'add', self.link_reqs_with_lower(self.))

    def submit_write_request(self, trace):
        """
        Read a trace, submit some write requests
        """
        for i in range(int(trace['num_callbacks'])):
            req = self.queues['queue']['write'].popleft()
            self.accept_req(req, trace.timestamp, 'submit')
