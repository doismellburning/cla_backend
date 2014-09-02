import mock

from django.conf import settings
from django.test import TestCase
from django.db import models

from eligibility_calculator.models import CaseData, ModelMixin
from eligibility_calculator.exceptions import PropertyExpectedException

from cla_common.constants import ELIGIBILITY_STATES
from cla_common.money_interval.models import MoneyInterval

from core.tests.mommy_utils import make_recipe, make_user

from legalaid.models import Case, ValidateModelMixin, Income


def walk(coll):
    """Return a generator for all atomic values in coll and its subcollections.
    An atomic value is one that's not iterable as determined by iter."""
    try:
        k = iter(coll)
        for x in k:
            for y in walk(x):
                yield y
    except TypeError:
        yield coll


class EligibilityCheckTestCase(TestCase):

    # def test_to_case_data_fail_without_your_finances(self):
    #     """
    #     Should fail as your_finances object is always needed
    #     """
    #     check = EligibilityCheck()
    #
    #     self.assertRaises(ValueError, check.to_case_data)

    def assertModelMixinEqual(self, obj1, obj2):
        for prop in obj1.__class__.PROPERTY_META.keys():
            if hasattr(obj1, prop) or hasattr(obj2, prop):
                val1 = getattr(obj1, prop)
                val2 = getattr(obj2, prop)

                assertFunc = self.assertEqual
                if isinstance(val1, list) or isinstance(val2, list):
                    assertFunc = self.assertItemsEqual
                if isinstance(val1, ModelMixin) or isinstance(val2, ModelMixin):
                    self.assertModelMixinEqual(val1, val2)
                    continue

                assertFunc(val1, val2, u"%s: %s != %s" % (prop, val1, val2))

    def test_to_case_data_without_partner(self):
        """
        EligibilityCheck partner data won't be used during CaseData creation
        """
        check = make_recipe('legalaid.eligibility_check',
            category=make_recipe('legalaid.category', code='code'),
            you=make_recipe('legalaid.person',
                income= make_recipe('legalaid.income',
                    earnings= {"interval_period": "per_month",
                               "per_interval_value": 500,
                                },
                    other_income={"interval_period": "per_month",
                                  "per_interval_value": 600
                                  },
                    self_employed=True
                ),
                savings=make_recipe('legalaid.savings',
                    bank_balance=100,
                    investment_balance=200,
                    asset_balance=300,
                    credit_balance=400,
                ),
                deductions=make_recipe('legalaid.deductions',
                    income_tax=MoneyInterval('per_month', pennies=600),
                    national_insurance=MoneyInterval('per_month', pennies=100),
                    maintenance=MoneyInterval('per_month', pennies=710),
                    childcare=MoneyInterval('per_month', pennies=715),
                    mortgage=MoneyInterval('per_month', pennies=700),
                    rent=MoneyInterval('per_month', pennies=20),
                    criminal_legalaid_contributions=730
                )
            ),
            dependants_young=3, dependants_old=2,
            is_you_or_your_partner_over_60=True,
            on_passported_benefits=True,
            on_nass_benefits=False,
            has_partner=False,
        )

        case_data = check.to_case_data()
        self.assertModelMixinEqual(
            case_data,
            CaseData(
                category='code',
                facts={
                    'dependants_young': 3,
                    'dependants_old': 2,
                    'is_you_or_your_partner_over_60':True,
                    'on_passported_benefits':True,
                    'on_nass_benefits': False,
                    'has_partner': False,
                    'is_partner_opponent': False,
                },
                you={
                    'savings':{
                        'bank_balance':100,
                        'investment_balance': 200,
                        'credit_balance':400,
                        'asset_balance': 300,
                    },
                    'income': {
                        'earnings': 500,
                        'other_income': 600,
                        'self_employed': True,
                    },
                    'deductions': {
                        'income_tax': 600,
                        'national_insurance': 100,
                        'maintenance': 710,
                        'childcare': 715,
                        'mortgage': 700,
                        'rent': 20,
                        'criminal_legalaid_contributions': 730,
                    }
                },
                property_data=[]
        ))

    def test_to_case_data_with_partner(self):
        """
        EligibilityCheck partner data is used during CaseData creation
        """
        check = make_recipe('legalaid.eligibility_check',
            category=make_recipe('legalaid.category', code='code'),
            you=make_recipe('legalaid.person',
                income=make_recipe('legalaid.income',
                    earnings=MoneyInterval('per_month', pennies=500),
                    other_income=MoneyInterval('per_month', pennies=600),
                    self_employed=True
                ),
                savings=make_recipe('legalaid.savings',
                    bank_balance=100,
                    investment_balance=200,
                    asset_balance=300,
                    credit_balance=400,
                ),
                deductions=make_recipe('legalaid.deductions',
                    income_tax=MoneyInterval('per_month', pennies=600),
                    national_insurance=MoneyInterval('per_month', pennies=100),
                    maintenance=MoneyInterval('per_month', pennies=710),
                    childcare=MoneyInterval('per_month', pennies=715),
                    mortgage=MoneyInterval('per_month', pennies=700),
                    rent=MoneyInterval('per_month', pennies=20),
                    criminal_legalaid_contributions=730
                )
            ),
            partner=make_recipe('legalaid.person',
                income= make_recipe('legalaid.income',
                    earnings=MoneyInterval('per_month', pennies=501),
                    other_income=MoneyInterval('per_month', pennies=601),
                    self_employed=False
                ),
                savings= make_recipe('legalaid.savings',
                    bank_balance=101,
                    investment_balance=201,
                    asset_balance=301,
                    credit_balance=401,
                ),
                deductions=make_recipe('legalaid.deductions',
                    income_tax=MoneyInterval('per_month', pennies=700),
                    national_insurance=MoneyInterval('per_month', pennies=1),
                    maintenance=MoneyInterval('per_month', pennies=711),
                    childcare=MoneyInterval('per_month', pennies=716),
                    mortgage=MoneyInterval('per_month', pennies=720),
                    rent=MoneyInterval('per_month', pennies=1),
                    criminal_legalaid_contributions=731
                )
            ),
            dependants_young=3, dependants_old=2,
            is_you_or_your_partner_over_60=True,
            on_passported_benefits=True,
            on_nass_benefits=False,
            has_partner=True,
        )

        case_data = check.to_case_data()
        self.assertModelMixinEqual(case_data, CaseData(
            category='code',
            facts={
                'dependants_young': 3,
                'dependants_old': 2,
                'is_you_or_your_partner_over_60':True,
                'on_passported_benefits': True,
                'on_nass_benefits': False,
                'has_partner': True,
                'is_partner_opponent': False,
            },
            you={
                'savings':{
                    'bank_balance':100,
                    'investment_balance': 200,
                    'credit_balance':400,
                    'asset_balance': 300,
                },
                'income': {
                    'earnings': 500,
                    'other_income':600,
                    'self_employed': True,
                },
                'deductions': {
                    'income_tax': 600,
                    'national_insurance': 100,
                    'maintenance': 710,
                    'childcare': 715,
                    'mortgage': 700,
                    'rent': 20,
                    'criminal_legalaid_contributions': 730,
                }
            },
            partner={
                'savings':{
                    'bank_balance':101,
                    'investment_balance': 201,
                    'credit_balance':401,
                    'asset_balance': 301,
                },
                'income': {
                    'earnings': 501,
                    'other_income':601,
                    'self_employed': False,
                },
                'deductions': {
                    'income_tax': 700,
                    'national_insurance': 1,
                    'maintenance': 711,
                    'childcare': 716,
                    'mortgage': 720,
                    'rent': 1,
                    'criminal_legalaid_contributions': 731,
                }
            },
            property_data=[],
        ))

    def test_validate(self):
        check = make_recipe(
            'legalaid.eligibility_check',
            category=make_recipe('legalaid.category', code='code'),
            you=make_recipe('legalaid.person',
                            income= make_recipe('legalaid.income',
                                                earnings= {"interval_period": "per_month",
                                                           "per_interval_value": 500,
                                                           },
                                                other_income={"interval_period": "per_month",
                                                              "per_interval_value": 600
                                                },
                                                self_employed=True
                            ),
                            savings=make_recipe('legalaid.savings',
                                                bank_balance=100,
                                                investment_balance=200,
                                                asset_balance=300,
                                                credit_balance=400,
                                                ),
                            deductions=make_recipe('legalaid.deductions',
                                                   income_tax=MoneyInterval('per_month', pennies=600),
                                                   national_insurance=MoneyInterval('per_month', pennies=100),
                                                   maintenance=MoneyInterval('per_month', pennies=710),
                                                   childcare=MoneyInterval('per_month', pennies=715),
                                                   mortgage=MoneyInterval('per_month', pennies=700),
                                                   rent=MoneyInterval('per_month', pennies=20),
                                                   criminal_legalaid_contributions=730
                            )
            ),
            dependants_young=3, dependants_old=2,
            is_you_or_your_partner_over_60=True,
            on_passported_benefits=True,
            has_partner=True,
            )
        expected = {'warnings':
                        {'partner':
                             {'deductions': ['Field "deductions" is required'],
                              'income': ['Field "income" is required'],
                              'savings': ['Field "savings" is required']}}}

        self.assertEqual(expected, check.validate())
        check.you = None
        expected2 = {'warnings':
                         {
                             'partner': {'deductions': ['Field "deductions" is required'],
                                         'income': ['Field "income" is required'],
                                         'savings': ['Field "savings" is required']},
                             'you': {'deductions': ['Field "deductions" is required'],
                                     'income': ['Field "income" is required'],
                                     'savings': ['Field "savings" is required']}}}
        self.assertDictEqual(expected2, check.validate())

    @mock.patch('legalaid.models.EligibilityChecker')
    def test_update_state(self, MockedEligibilityChecker):
        """
            calling .is_eligible() sequencially will:

            1. through PropertyExpectedException
            2. return True
            3. return False
            4. through PropertyExpectedException again
        """
        mocked_checker = MockedEligibilityChecker()
        mocked_checker.is_eligible.side_effect = [
            PropertyExpectedException(), True, False, PropertyExpectedException()
        ]

        # 1. PropertyExpectedException => UNKNOWN
        check = make_recipe('legalaid.eligibility_check', state=ELIGIBILITY_STATES.UNKNOWN)
        check.update_state()
        self.assertEqual(check.state, ELIGIBILITY_STATES.UNKNOWN)

        # 2. True => YES
        check.update_state()
        self.assertEqual(check.state, ELIGIBILITY_STATES.YES)

        # 3. False => NO
        check.update_state()
        self.assertEqual(check.state, ELIGIBILITY_STATES.NO)

        # 4. PropertyExpectedException => UNKNOWN
        check.update_state()
        self.assertEqual(check.state, ELIGIBILITY_STATES.UNKNOWN)


class CaseTestCase(TestCase):
    def test_create_has_laa_reference(self):
        case = make_recipe('legalaid.case')

        # there is an LAA Reference
        self.assertIsNotNone(case.laa_reference)

        # it is valid as per algorithm
        self.assertEqual(case.id + settings.LAA_REFERENCE_SEED, case.laa_reference)

        # it is 7 digits long
        self.assertEqual(len(unicode(case.laa_reference)), 7)

    def test_assign_to_provider_overriding_provider(self):
        providers = make_recipe('cla_provider.provider', _quantity=2)

        case = make_recipe('legalaid.case', provider=providers[0])

        self.assertTrue(case.provider)

        case.assign_to_provider(providers[1])

        self.assertEqual(case.provider, providers[1])

    def test_assign_to_provider_None(self):
        provider = make_recipe('cla_provider.provider')

        case = make_recipe('legalaid.case', provider=None)

        self.assertFalse(case.provider)

        case.assign_to_provider(provider)

        self.assertEqual(case.provider, provider)


    def test_assign_alternative_help(self):
        articles = make_recipe('knowledgebase.article', _quantity=10)
        user = make_user()
        case = make_recipe('legalaid.case', provider=None)

        # assign some articles
        self.assertListEqual(list(case.alternative_help_articles.all()), [])
        case.assign_alternative_help(user, articles[:5])
        self.assertListEqual(list(case.alternative_help_articles.all()), articles[:5])

        # assign some more articles; originals should be gone
        case.assign_alternative_help(user, articles[5:])

        self.assertListEqual(list(case.alternative_help_articles.all()), articles[5:])


    def test_lock_doesnt_override_existing_lock(self):
        import logging

        # disabling logging temporarily
        logging.disable(logging.CRITICAL)

        users = make_user(_quantity=2)
        case = make_recipe('legalaid.case',
            locked_by=users[0]
        )
        self.assertFalse(case.lock(users[1]))
        self.assertEqual(case.locked_by, users[0])

        # enabling logging back
        logging.disable(logging.NOTSET)

    def test_lock_without_saving(self):
        user = make_user()
        case = make_recipe('legalaid.case')
        self.assertTrue(case.lock(user, save=False))
        self.assertEqual(case.locked_by, user)

        db_case = Case.objects.get(pk=case.pk)
        self.assertEqual(db_case.locked_by, None)

    def test_lock_and_save(self):
        user = make_user()
        case = make_recipe('legalaid.case')
        self.assertTrue(case.lock(user))
        self.assertEqual(case.locked_by, user)

        db_case = Case.objects.get(pk=case.pk)
        self.assertEqual(db_case.locked_by, user)

    # CASE COUNT

    def test_case_count_doesnt_updated_if_null_pd(self):
        """
        if case.personal_details == None:
            case.personal_details.case_count shouldn't get updated
        """
        case = make_recipe('legalaid.case')
        self.assertTrue(case.personal_details, None)

    def test_case_count_gets_updated_if_pd_not_null(self):
        pd = make_recipe('legalaid.personal_details')

        self.assertEqual(pd.case_count, 0)
        # saving first case
        make_recipe('legalaid.case', personal_details=pd)
        self.assertEqual(pd.case_count, 1)

        # saving second case
        make_recipe('legalaid.case', personal_details=pd)
        self.assertEqual(pd.case_count, 2)

        # saving different case
        pd2 = make_recipe('legalaid.personal_details')
        make_recipe('legalaid.case', personal_details=pd2)
        self.assertEqual(pd.case_count, 2)
        self.assertEqual(pd2.case_count, 1)


class MoneyIntervalFieldTestCase(TestCase):
    def test_create_save_moneyinterval(self):
        ei = MoneyInterval('per_week', pennies=5000)
        per_month = int((5000.0 * 52.0) / 12.0)

        i = Income(earnings=ei, other_income=ei, self_employed=True)
        self.assertEqual(i.earnings.interval_period, 'per_week')
        i.save()

        ix = Income.objects.get(id=i.id)
        eix = ix.earnings
        self.assertEqual(eix.interval_period, 'per_week')
        self.assertEqual(eix.per_interval_value, 5000)
        self.assertEqual(eix.as_monthly(), per_month)

    def test_annual_moneyinterval(self):
        ei = MoneyInterval(interval_period='per_year', pennies=1200000)
        self.assertEqual(ei.as_monthly(), 100000)


class ValidationModelMixinTestCase(TestCase):

    class Model1(models.Model):
        pass

    class Model2(ValidateModelMixin, models.Model):
        pass

    class Model3(ValidateModelMixin, models.Model):

        a = models.CharField(null=True, blank=True)
        b = models.CharField(null=True, blank=True)
        c = models.CharField(null=True, blank=True)

        def get_dependencies(self):
            return {'a', 'b', 'c'}

    class Model4(ValidateModelMixin, models.Model):
        related = models.ForeignKey('Model3')

        def get_dependencies(self):
            return {'related__a', 'related__b', 'related__c'}


    def setUp(self):
        super(ValidationModelMixinTestCase, self).setUp()
        self.model1 = self.Model1()
        self.model2 = self.Model2()
        self.model3 = self.Model3()
        self.model4 = self.Model4()
        self.model4.related = self.model3

    def test_mixin_worked(self):
        self.assertFalse(hasattr(self.model1, 'validate'))
        self.assertTrue(hasattr(self.model2, 'validate'))
        self.assertTrue(hasattr(self.model3, 'validate'))

    def test_not_impl_error(self):
        with self.assertRaises(NotImplementedError):
            self.model2.get_dependencies()

    def test_validate_all_invalid(self):
        expected = {'warnings': {'a': ['Field "a" is required'],
                                 'b': ['Field "b" is required'],
                                 'c': ['Field "c" is required']}}
        self.assertEqual(expected, self.model3.validate())

    def test_validate_partial_invalid(self):
        self.model3.a = 'a'
        self.model3.b = 'b'

        expected = {'warnings': { 'c': ['Field "c" is required']}}
        self.assertEqual(expected, self.model3.validate())

    def test_validate_none_invalid(self):
        self.model3.a = 'a'
        self.model3.b = 'b'
        self.model3.c = 'c'

        expected = {'warnings': {}}
        self.assertEqual(expected, self.model3.validate())

    def test_validate_nested_invalid(self):
        expected = {'warnings': {'related': {'a': ['Field "a" is required'], 'c': ['Field "c" is required'], 'b': ['Field "b" is required']}}}

        self.assertEqual(expected, self.model4.validate())
