import datetime
from unittest import skip
import dateutil.parser as parser

from django.test import TestCase
from django.utils import timezone

from cla_common.constants import CASELOGTYPE_ACTION_KEYS

from core.tests.mommy_utils import make_recipe

from ..forms import ProviderCaseClosure, \
    OperatorCaseClosure

@skip('skip until this is reimplemented using Log')
class ProviderCaseClosureReportFormTestCase(TestCase):
    def test_rows(self):
        """
            Search:
                Provider pk: 1
                date from: 02/04/2014
                date to: 15/04/2014

            Cases / Outcomes:
                ref '1': provider 1, closure date (16/04/2014 00:01) => excluded
                ref '2': provider 1, closure date (15/04/2014 23:59) => included
                ref '3': provider 1, rejected date (15/04/2014 23:59) => included
                ref '4': provider 1, accepted date (15/04/2014 23:59) => excluded
                ref '5': provider 2, closure date (02/04/2014 00:01) => excluded
                ref '6': provider 1, closure date (02/04/2014 00:01) => included
                ref '7': provider 1, closure date (02/04/2014 00:00) => included
                ref '8': provider 1, closure date (01/04/2014 23:59) => excluded
                ref '9': provider 1, rejected date (01/04/2014 23:59) => excluded
                ref '10': provider 1, no closure => excluded

            Result:
                [7, 6, 3, 2] - [Total: 4]

        """
        providers = make_recipe('cla_provider.provider', active=True, _quantity=2)

        def create_db_record(case_ref, closure_date, provider,
            action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_CLOSE_CASE
        ):
            raise NotImplementedError()
            case_outcome = make_recipe('legalaid.case_log',
                logtype__action_key=action_key,
                case__provider=provider,
                case__reference=case_ref,
                logtype__code='outcome_%s' % case_ref,
                logtype__subtype=CASELOGTYPE_SUBTYPES.OUTCOME,
                case__eligibility_check__category__name='Category_%s' % case_ref
            )
            closure_date = parser.parse(closure_date)
            case_outcome.__class__.objects.filter(pk=case_outcome.pk).update(
                created=closure_date.replace(tzinfo=timezone.utc)
            )

        create_db_record('1', '2014-04-15T23:01', providers[0], action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_CLOSE_CASE)
        create_db_record('2', '2014-04-15T22:59:01', providers[0], action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_CLOSE_CASE)
        create_db_record('3', '2014-04-15T22:59', providers[0], action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_REJECT_CASE)
        create_db_record('4', '2014-04-15T22:59', providers[0], action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_ACCEPT_CASE)
        create_db_record('5', '2014-04-01T23:01', providers[1], action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_CLOSE_CASE)
        create_db_record('6', '2014-04-01T23:01', providers[0], action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_CLOSE_CASE)
        create_db_record('7', '2014-04-01T23:00', providers[0], action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_CLOSE_CASE)
        create_db_record('8', '2014-04-01T22:59', providers[0], action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_CLOSE_CASE)
        create_db_record('9', '2014-04-01T22:59', providers[0], action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_REJECT_CASE)
        create_db_record('10', '2014-04-01T22:59', providers[0], action_key='other')


        # form, non-empty result
        form = ProviderCaseClosure({
            'provider': providers[0].pk,
            'date_from': datetime.date(2014, 4, 2),
            'date_to': datetime.date(2014, 4, 15)
        })

        self.assertTrue(form.is_valid())

        rows = list(form.get_rows())
        self.assertEqual(rows,
            [
                [u'7', '02/04/2014 00:00', u'outcome_7', u'Category_7'],
                [u'6', '02/04/2014 00:01', u'outcome_6', u'Category_6'],
                [u'3', '15/04/2014 23:59', u'outcome_3', u'Category_3'],
                [u'2', '15/04/2014 23:59', u'outcome_2', u'Category_2'],
                [],
                ['Total: 4']
            ]
        )

        # form, empty results
        form = ProviderCaseClosure({
            'provider': providers[0].pk,
            'date_from': datetime.date(2014, 4, 19),
            'date_to': datetime.date(2014, 4, 20)
        })

        self.assertTrue(form.is_valid())

        rows = list(form.get_rows())
        self.assertEqual(rows,
            [
                [],
                ['Total: 0']
            ]
        )

    def test_get_headers(self):
        form = ProviderCaseClosure()

        self.assertEqual(
            form.get_headers(),
            ['Case #', 'Closure Date', 'Outcome Code', 'Law Categories']
        )


@skip('skip until this is reimplemented using Log')
class OperatorCaseClosureReportFormTestCase(TestCase):
    def test_rows(self):
        """
            Search:
                date from: 02/04/2014
                date to: 15/04/2014

            Cases / Outcomes:
                ref '1': provider 1, assign date (16/04/2014 00:00) => excluded
                ref '2': provider 1, assign date (15/04/2014 23:59) => included
                ref '3': provider 2, assign date (02/04/2014 00:01) => excluded
                ref '4': provider 1, assign date (02/04/2014 00:01) => included
                ref '5': provider 1, assign date (02/04/2014 00:00) => included
                ref '6': provider 1, assign date (01/04/2014 23:59) => excluded
                ref '7': provider 1, no assign => excluded

            Result:
                [5, 4, 2] - [Total: 3] - [Average: 100]

        """
        providers = make_recipe('cla_provider.provider', active=True, _quantity=2)

        # form, empty results
        form = OperatorCaseClosure({
            'date_from': datetime.date(2014, 4, 19),
            'date_to': datetime.date(2014, 4, 20)
        })

        self.assertTrue(form.is_valid())

        rows = list(form.get_rows())
        self.assertEqual(rows,
                         [
                             [],
                             ['Total: 0'],
                             ['Average Duration: 0']
                         ]
        )



        def create_db_record(case_ref, assign_date, provider,
            action_key=CASELOGTYPE_ACTION_KEYS.PROVIDER_CLOSE_CASE
        ):
            assign_date = parser.parse(assign_date).replace(tzinfo=timezone.utc)
            case_outcome = make_recipe('legalaid.case_log',
                                       logtype__action_key=action_key,
                                       case__provider=provider,
                                       case__reference=case_ref,
                                       case__created=assign_date - datetime.timedelta(seconds=200),
                                       created=assign_date - datetime.timedelta(seconds=20),
                                       logtype=caselogtype,
                                       case__eligibility_check__category__name='Category_%s' % case_ref
            )
            case_outcome.__class__.objects.filter(pk=case_outcome.pk).update(
                created=assign_date.replace(tzinfo=timezone.utc)
            )

        create_db_record('1', '2014-04-16T01:00', providers[0])
        create_db_record('2', '2014-04-15T00:59', providers[0])
        create_db_record('3', '2014-04-02T01:01', providers[1])
        create_db_record('4', '2014-04-02T01:01', providers[0])
        create_db_record('5', '2014-04-02T01:00', providers[0])
        create_db_record('6', '2014-04-01T00:59', providers[0])
        create_db_record('7', '2014-04-01T00:59', providers[0])


        # form, non-empty result
        form = OperatorCaseClosure({
            'date_from': datetime.date(2014, 4, 2),
            'date_to': datetime.date(2014, 4, 15)
        })

        self.assertTrue(form.is_valid())

        self.maxDiff = None

        rows = list(form.get_rows())
        self.assertEqual(rows,
                         [
                             [u'5', '02/04/2014 00:56', '02/04/2014 01:00', 200, u'REFSP', u'Name1'],
                             [u'3', '02/04/2014 00:57', '02/04/2014 01:01', 200, u'REFSP', u'Name2'],
                             [u'4', '02/04/2014 00:57', '02/04/2014 01:01', 200, u'REFSP', u'Name1'],
                             [u'2', '15/04/2014 00:55', '15/04/2014 00:59', 200, u'REFSP', u'Name1'],
                             [],
                             ['Total: 4'],
                             ['Average Duration: 200']
                         ]
        )


    def test_get_headers(self):
        form = OperatorCaseClosure()

        self.assertEqual(
            form.get_headers(),
           ['Case #', 'Call Started', 'Call Assigned', 'Duration (sec)','Outcome Code', 'To Provider']
        )
