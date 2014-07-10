from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_LEVELS, LOG_ROLES
from cla_eventlog.events import BaseEvent


class RejectCaseEvent(BaseEvent):
    key = 'reject_case'
    codes = {
        'MIS': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Misdiagnosed, assigned to wrong Specialist or another Specialist is dealing with client'
        },
        'MIS-MEANS': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Misdiagnosed, means test isn\'t correct'
        },
        'MIS-OOS': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Misdiagnosed, out of scope'
        },
        'COI': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [LOG_ROLES.SPECIALIST],
            'description': 'Conflict of Interest'
        },
    }

    def get_log_code(self, **kwargs):
        is_conflict = kwargs.get('is_conflict')

        if is_conflict:
            return 'COI'

        return super(RejectCaseEvent, self).get_log_code(**kwargs)
event_registry.register(RejectCaseEvent)


class AcceptCaseEvent(BaseEvent):
    key = 'accept_case'
    codes = {
        'SPOP': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Case taken'
        },
    }
event_registry.register(AcceptCaseEvent)


class CloseCaseEvent(BaseEvent):
    key = 'close_case'
    codes = {
        'CLSP': {
            'type': LOG_TYPES.OUTCOME,
            'level': LOG_LEVELS.HIGH,
            'selectable_by': [],
            'description': 'Closed SP Case'
        }
    }
event_registry.register(CloseCaseEvent)