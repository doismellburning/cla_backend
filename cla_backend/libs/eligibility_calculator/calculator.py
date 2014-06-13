from . import constants


class EligibilityChecker(object):
    def __init__(self, case_data):
        super(EligibilityChecker, self).__init__()
        self.case_data = case_data

    @property
    def gross_income(self):
        if not hasattr(self, '_gross_income'):
            self._gross_income = self.case_data.total_income
        return self._gross_income

    @property
    def disposable_income(self):
        if not hasattr(self, '_disposable_income'):
            gross_income = self.gross_income

            if self.case_data.facts.has_partner:
                gross_income -= constants.disposable_income.PARTNER_ALLOWANCE

            # children

            # TODO 2 values for children...
            gross_income -= self.case_data.facts.dependant_children * constants.disposable_income.CHILD_ALLOWANCE

            # Tax + NI
            income_tax_and_ni = self.case_data.you.deductions.income_tax['per_month'] \
                              + self.case_data.you.deductions.national_insurance['per_month'] 
            gross_income -= income_tax_and_ni
            if self.case_data.facts.should_aggregate_partner:
                income_tax_and_ni = self.case_data.partner.deductions.income_tax['per_month'] \
                                  + self.case_data.partner.deductions.national_insurance['per_month'] 
                gross_income -= income_tax_and_ni

            # maintenance 6.3
            gross_income -= self.case_data.you.deductions.maintenance['per_month']
            if self.case_data.facts.should_aggregate_partner:
                gross_income -= self.case_data.partner.deductions.maintenance['per_month']

            # housing
            mortgage_or_rent = self.case_data.you.deductions.mortgage['per_month']  # excl housing benefit
            mortgage_or_rent += self.case_data.you.deductions.rent['per_month']
            if self.case_data.facts.should_aggregate_partner:
                mortgage_or_rent += self.case_data.partner.deductions.mortgage['per_month']
                mortgage_or_rent += self.case_data.partner.deductions.rent['per_month']

            if not self.case_data.facts.dependant_children:
                mortgage_or_rent = min(mortgage_or_rent, constants.disposable_income.CHILDLESS_HOUSING_CAP)
            gross_income -= mortgage_or_rent

            if not self.case_data.you.income.self_employed:
                gross_income -= constants.disposable_income.EMPLOYMENT_COSTS_ALLOWANCE

            if self.case_data.facts.has_partner:
                if self.case_data.facts.should_aggregate_partner and not self.case_data.partner.income.self_employed:
                    gross_income -= constants.disposable_income.EMPLOYMENT_COSTS_ALLOWANCE

            # criminal
            gross_income -= self.case_data.you.deductions.criminal_legalaid_contributions  # not for now
            if self.case_data.facts.should_aggregate_partner:
                gross_income -= self.case_data.partner.deductions.criminal_legalaid_contributions

            # childcare 6.5.2
            gross_income -= self.case_data.you.deductions.childcare['per_month']
            if self.case_data.facts.should_aggregate_partner:
                gross_income -= self.case_data.partner.deductions.childcare['per_month']

            self._disposable_income = gross_income

        return self._disposable_income

    @property
    def disposable_capital_assets(self):
        if not hasattr(self, '_disposable_capital_assets'):
            # NOTE: problem in case of disputed partner (and joined savings/assets)

            disposable_capital = 0

            if not self.case_data.facts.has_disputed_partner:
                disposable_capital += self.case_data.liquid_capital

                properties_value, mortgages_left = self.case_data.property_capital

                prop_capital = properties_value - min(mortgages_left, constants.disposable_capital.MORTGAGE_DISREGARD) - constants.disposable_capital.EQUITY_DISREGARD
                prop_capital = max(prop_capital, 0)

                disposable_capital += prop_capital
            else:
                raise NotImplementedError('Not supported yet')

            if self.case_data.facts.is_you_or_your_partner_over_60:
                disposable_capital -= constants.disposable_capital.PENSIONER_DISREGARD_LIMIT_LEVELS.get(max(self.disposable_income, 0), 0)

            disposable_capital = max(disposable_capital, 0)

            self._disposable_capital_assets = disposable_capital

        return self._disposable_capital_assets

    def is_gross_income_eligible(self):
        if self.case_data.facts.on_passported_benefits:
            return True

        limit = constants.gross_income.get_limit(self.case_data.facts.dependant_children)
        return self.gross_income <= limit

    def is_disposable_income_eligible(self):
        if self.case_data.facts.on_passported_benefits:
            return True

        return self.disposable_income <= constants.disposable_income.LIMIT

    def is_disposable_capital_eligible(self):
        limit = constants.disposable_capital.get_limit(self.case_data.category)
        return self.disposable_capital_assets <= limit

    def is_eligible(self):

        if self.case_data.facts.on_nass_benefits:
            return True

        if not self.is_disposable_capital_eligible():
            return False

        if not self.is_gross_income_eligible():
            return False

        if not self.is_disposable_income_eligible():
            return False

        return True
