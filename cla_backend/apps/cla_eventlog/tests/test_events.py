from django.test import TestCase

from cla_eventlog import event_registry
from cla_eventlog.constants import LOG_TYPES, LOG_ROLES, LOG_LEVELS
from cla_eventlog.models import Log

from cla_eventlog.tests.base import EventTestCaseMixin


class SelectableEventsTestCase(EventTestCaseMixin, TestCase):
    def test_select_selectable_code(self):
        # get dict {event_key: [list of selectable codes]}
        selectable_events = event_registry.get_selectable_events(role=LOG_ROLES.OPERATOR)

        for chosen_key, chosen_codes in selectable_events.items():
            for chosen_code in chosen_codes:
                # chosen key / code

                event = event_registry.get_event(chosen_key)()
                res = event.process(
                    self.dummy_case,
                    code=chosen_code,
                    notes='selectable notes',
                    created_by=self.dummy_user)

                self.assertLogEqual(res, Log(case=self.dummy_case,
                                             code=chosen_code,
                                             type=LOG_TYPES.OUTCOME,
                                             notes='selectable notes',
                                             level=LOG_LEVELS.HIGH,
                                             created_by=self.dummy_user))

    def test_select_selectable_code_invalid(self):
        # get dict {event_key: [list of selectable codes]}
        selectable_events = event_registry.get_selectable_events(role='admin')
        self.assertEqual(selectable_events, {})
