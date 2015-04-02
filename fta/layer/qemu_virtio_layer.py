from . import BlkLayer
from . import rules
from fta import Event
from fta.request_queue import ReqQueue

trace_attrs_queue = {
    'id': 'req', 'offset': ('sector', BlkLayer.sec2byte),
    'length': ('nsectors', BlkLayer.sec2byte)
    }

trace_attrs_queue_write = {
    'additional': [('ops', ['write'])]
    }
trace_attrs_queue_write.update(trace_attrs_queue)

trace_attrs_queue_read = {
    'additional': [('ops', ['read'])]
    }
trace_attrs_queue_read.update(trace_attrs_queue)

trace_attrs_submit_read = {
    'offset': ('sector_num', BlkLayer.sec2byte),
    'length': ('nb_sectors', BlkLayer.sec2byte),
    }

trace_attrs_finish = {
    'id': 'req'
    }


class QemuVirtioLayer(BlkLayer):
    """
    Layer for Qemu's Virtio
    """
    def __init__(self, name):
        super().__init__(name)
        self.trace_handlers = {
            # queue
            'virtio_blk_handle_write': self.handler_gen_req(
                'queue',
                'qemu_virtio_write',
                dest=self.queues['queue']['write'],
                attrs=trace_attrs_queue_write,
                ),
            'virtio_blk_handle_read': self.handler_gen_req(
                'queue',
                'qemu_virtio_read',
                dest=self.queues['queue']['read'],
                attrs=trace_attrs_queue_read,
                ),
            # submit
            'bdrv_aio_multiwrite': self.submit_write_request,
            'bdrv_aio_readv': self.handler_mv_req(
                'submit',
                dest=self.queues['submit'],
                src=self.queues['queue']['read'],
                rule=rules.same_pos,
                attrs=trace_attrs_submit_read,
                ),
            # finish
            'virtio_blk_rw_complete': self.handler_mv_req(
                'finish',
                dest=self.get_queue_req_op('finish'),
                src=self.queues['submit'],
                rule=rules.same_id,
                attrs=trace_attrs_finish,
                ),
            }
        self.when(
            'lower', 'queue',
            self.link_with_lower_from(
                self.queues['submit'], 'overlaps')
            )

    def submit_write_request(self, trace):
        """
        Read a trace, submit some write requests
        """
        event = Event(trace)
        for i in range(int(trace['num_callbacks'])):
            req = self.queues['queue']['write'].popleft()
            self.accept_req(req, event, 'submit', self.queues['submit'])

    def init_queues(self):
        for t in ['queue', 'finish']:
            self.queues[t] = {'read': ReqQueue(), 'write': ReqQueue()}
        self.queues['submit'] = ReqQueue()
