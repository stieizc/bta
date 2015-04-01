from . import BlkLayer
from . import rules
from libbta import ReqQueue
from libbta.utils import rwbs


class QemuRawLayer(BlkLayer):
    """
    Layer for Qemu's Raw File Backend

    Doesn't have a finish trace for itself, since it calls a callback function
    on finish, which instead finish upper requests.

    Rely on upper for finishing request. It is possible that a request is
    actually finished but never marked so.
    """

    trace_attrs_queue = {
        'id': 'acb', 'offset': ('sector_num', int),
        'length': ('nb_sectors', int), 'ops': ('type', rwbs.parse_qemu_aio)
        }
    trace_attrs_submit = {
        'id': 'aiocb', 'offset': 'aiocb__aio_offset',
        'length': 'aiocb__aio_nbytes'
        }

    def __init__(self, name):
        super().__init__(name)
        self.trace_handlers = {
            'paio_submit': (
                'queue', 'qemu_raw_rw', self.trace_attrs_queue
                ),
            'handle_aiocb_rw': (
                'submit', ('queue', self.rule_submit),
                self.trace_attrs_submit
                )
            }
        self.use_default_lower_linker()

        @self.when('upper', 'finish')
        def finish_with_upper(upper_req):
            for req in upper_req.related['lower']:
                if not req.events['finish']:
                    self.finish_request(req, upper_req)

    @staticmethod
    def rule_submit(req, event):
        return rules.same_pos(req, event) and rules.same_id(req, event)

    def finish_request(self, req, upper_req):
        self.req_queue['submit'].remove(req)
        self.accept_req(req, upper_req, 'finish', self.queues['finish'])

    # Override BlkLayer
    def init_queues(self):
        for t in self.EVENT_TYPES:
            self.queues[t] = ReqQueue()

    def get_queue(self, action, event):
        return self.queues[action]
