from . import BlkLayer
from . import rules
from fta.request_queue import ReqQueue
from fta.utils import rwbs


class QemuRawLayer(BlkLayer):
    """
    Layer for Qemu's Raw File Backend

    Doesn't have a finish trace for itself, since it calls a callback function
    on finish, which instead finish upper requests.

    Rely on upper for finishing request. It is possible that a request is
    actually finished but never marked so.
    """

    trace_attrs_queue = {
        'id': 'acb', 'offset': ('sector_num', BlkLayer.sec2byte),
        'length': ('nb_sectors', BlkLayer.sec2byte),
        'ops': ('type', rwbs.parse_qemu_aio)
        }
    trace_attrs_submit = {
        'id': 'aiocb', 'offset': ('aiocb__aio_offset', BlkLayer.sec2byte),
        'length': ('aiocb__aio_nbytes', BlkLayer.sec2byte)
        }

    def __init__(self, name):
        super().__init__(name)
        self.trace_handlers = {
            'paio_submit': self.handler_gen_req(
                'queue',
                'qemu_raw_rw',
                dest=self.queues['queue'],
                attrs=self.trace_attrs_queue,
                ),
            'handle_aiocb_rw': self.handler_mv_req(
                'submit',
                dest=self.get_queue_req_op('submit'),
                src=self.queues['queue'],
                rule=self.rule_submit,
                attrs=self.trace_attrs_submit,
                ),
            }
        self.when(
            'lower', 'queue',
            self.link_with_lower_from(
                self.get_queue_req_op('submit'), 'overlaps')
            )

        @self.when('upper', 'finish')
        def finish_with_upper(upper_req):
            src = self.queues['submit'][upper_req.op_type]
            dest = self.queues['finish'][upper_req.op_type]
            event = upper_req.events['finish']
            for req in upper_req.related['lower']:
                if not req.events['finish']:
                    src.remove(req)
                    self.accept_req(req, event, 'finish', dest)

    @staticmethod
    def rule_submit(req, event):
        return rules.same_pos(req, event) and rules.same_id(req, event)

    # Override BlkLayer
    def init_queues(self):
        for t in ['submit', 'finish']:
            self.queues[t] = {'read': ReqQueue(), 'write': ReqQueue()}
        self.queues['queue'] = ReqQueue()
