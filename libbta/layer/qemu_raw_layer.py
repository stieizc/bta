from . import BlkLayer
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

    def __init__(self, name):
        super().__init__(name)
        self.trace_handlers = {
            'paio_submit': (
                'queue', ('qemu_raw_rw', self.trace_attrs_queue)
                ),
            'handle_aiocb_rw': (
                'submit', ('queue', self.rule_submit)
                )
            }
        self.use_default_lower_linker()

        @self.when('upper', 'finish')
        def finish_with_upper(r):
            finish_time = r.timestamps['finish']
            for req in r.related['lower']:
                if not req.timestamps['finish']:
                    self.finish_request(req, finish_time)

    @staticmethod
    def rule_submit(req, trace):
        return req['id'] == trace['aiocb'] \
            and req['offset'] == int(trace['aiocb__aio_offset']) \
            and req['length'] == int(trace['aiocb__aio_nbytes'])

    def finish_request(self, req, timestamp):
        self.req_queue['submit'].remove(req)
        self.accept_req(req, 'finish', timestamp)

    # Override BlkLayer
    def init_queues(self):
        for t in self.EVENT_TYPES:
            self.queues[t] = ReqQueue()

    def get_queue(self, action, event):
        return self.queues[action]
