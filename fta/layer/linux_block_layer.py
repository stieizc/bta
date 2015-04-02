from . import BlkLayer
from . import rules
from fta import Event
from fta.utils import rwbs
from fta.exceptions import EventDiscarded
from fta.exceptions import MergeFailed


trace_attrs = {
    'offset': ('sector', BlkLayer.sec2byte),
    'length': ('nr_sector', BlkLayer.sec2byte),
    'dev': 'dev', 'ops': ('rwbs', rwbs.parse_bio),
    }

trace_attrs_submit_finish = {
    'cmd_length': ('_cmd_length', int),
    }
trace_attrs_submit_finish.update(trace_attrs)


class LinuxBlockLayer(BlkLayer):
    """
    Layer for Linux's block layer

    Life cycle of a req:
    (remap ->) queue -> getrq -> insert -> issue -> complete
                     -> merge
    """

    def __init__(self, name):
        super().__init__(name)
        self.trace_handlers = {
            'block_bio_queue': self.handler_gen_req(
                'queue',
                'block_bio',
                dest=self.get_queue_req_op('queue'),
                attrs=trace_attrs,
                ),
            'block_rq_issue': self.handler_mv_req(
                'submit',
                dest=self.get_queue_req_op('submit'),
                src=self.get_queue_req_op('queue'),
                rule=self.rule,
                attrs=trace_attrs_submit_finish,
                discard=self.is_scsi,
                ),
            'block_rq_complete': self.handler_mv_req(
                'finish',
                dest=self.get_queue_req_op('finish'),
                src=self.get_queue_req_op('submit'),
                rule=self.rule,
                attrs=trace_attrs_submit_finish,
                discard=self.is_scsi,
                ),
            'block_bio_backmerge': self.merge_request(
                self.rule_backmerge,
                self._backmerge,
                ),
            'block_bio_frontmerge': self.merge_request(
                self.rule_frontmerge,
                self._frontmerge,
                )
            }
        self.when(
            'lower', 'queue',
            self.link_with_lower_from(
                self.get_queue_req_op('submit'), 'overlaps')
            )

        @self.on('finish')
        def finish_merged_request(master_req):
            merged_reqs = master_req.related['merged']
            if not merged_reqs:
                return
            event = master_req.events['finish']
            dest = self.queues['finish'][master_req['ops'][0]]
            for req in merged_reqs:
                self.accept_req(req, event, 'finish', dest)

    @staticmethod
    def _backmerge(to_merge, master):
        master['length'] += to_merge['length']

    @staticmethod
    def rule_backmerge(to_merge, master):
        return to_merge['dev'] == master['dev'] and \
            to_merge['offset'] == master['offset'] + master['length']

    @staticmethod
    def _frontmerge(to_merge, master):
        master['offset'] = to_merge['offset']
        master['length'] += to_merge['length']

    @staticmethod
    def rule_frontmerge(to_merge, master):
        return master['dev'] == to_merge['dev'] and \
            master['offset'] == to_merge['offset'] + to_merge['length']

    def merge_request(self, merge_rule, _merge):
        _queue = self.queues['queue']
        _rule = self.rule

        def merge(trace):
            event = Event(trace, trace_attrs)
            queue = _queue[event['ops'][0]]
            # Pop the req to be merged
            to_merge = queue.req_out(_rule, event)
            if not to_merge:
                raise EventDiscarded(event)
            # Don't pop the master req!
            for req in queue:
                if merge_rule(to_merge, req):
                    _merge(to_merge, req)
                    req.link('merged', to_merge)
                    return to_merge
            raise MergeFailed(to_merge, event)
        return merge

    @staticmethod
    def rule(req, event):
        return rules.same_pos(req, event) and req['dev'] == event['dev'] and \
            rules.same_op_type(req, event)

    @staticmethod
    def is_scsi(event):
        if event['length'] == 0:
            if event['cmd_length'] != 0:
                return True
