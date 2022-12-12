__author__ = 'brian'

import unittest

from src.custom_exceptions import \
    MalformattedReactionDirectionSymbolException, \
    MalformattedReactionException, \
    InvalidSymbolName
from src import parsers


class TestStringExpressionParser(unittest.TestCase):

    # some tests related to the arrow in the equation
    def test_backwards_arrow_raises_error(self):
        bad_eqn = 'A + B <- C'
        with self.assertRaises(MalformattedReactionDirectionSymbolException):
            parsers.StringExpressionParser.parse(bad_eqn)

    def test_bad_arrow_raises_error(self):
        bad_eqn = 'A + B > C'
        with self.assertRaises(MalformattedReactionDirectionSymbolException):
            parsers.StringExpressionParser.parse(bad_eqn)

    def test_bad_eqn_raises_error(self):
        bad_eqn = 'A + -> C'
        with self.assertRaises(InvalidSymbolName):
            parsers.StringExpressionParser.parse(bad_eqn)

        bad_eqn = 'A + B-> C,'
        with self.assertRaises(MalformattedReactionException):
            parsers.StringExpressionParser.parse(bad_eqn)

        bad_eqn = '-A + B-> C'
        with self.assertRaises(MalformattedReactionException):
            parsers.StringExpressionParser.parse(bad_eqn)

        bad_eqn = 'A - B-> C'
        with self.assertRaises(MalformattedReactionException):
            parsers.StringExpressionParser.parse(bad_eqn)

    def test_unidirectional_reaction(self):
        eqn = 'A +      B -> C'
        reactants, products, is_bidirectional =\
            parsers.StringExpressionParser.parse(eqn)
        self.assertFalse(is_bidirectional)
        self.assertCountEqual([x.symbol for x in reactants], ['A', 'B'])
        self.assertCountEqual([x.symbol for x in products], ['C'])

        eqn = 'A -> C'
        reactants, products, is_bidirectional =\
            parsers.StringExpressionParser.parse(eqn)
        self.assertFalse(is_bidirectional)
        self.assertCountEqual([x.symbol for x in reactants], ['A'])
        self.assertCountEqual([x.symbol for x in products], ['C'])

    def test_bidirectional_equation(self):
        '''
        Even if the reverse constant is zero, we still treat
        the equation below as bi-directional. From a practical
        standpoint, it's the same as unidirectional. However,
        it avoids issues of rounding, etc. when we consider
        "truly zero" rate constants.
        '''
        eqn = 'A + B <-> C'
        reactants, products, is_bidirectional = \
            parsers.StringExpressionParser.parse(eqn)
        # even though the reverse rate is zero, this is technically
        # still a bi-directional equation
        self.assertTrue(is_bidirectional)
        self.assertCountEqual([x.symbol for x in reactants], ['A', 'B'])
        self.assertCountEqual([x.symbol for x in products], ['C'])

        eqn = 'A <-> C'
        reactants, products, is_bidirectional = \
            parsers.StringExpressionParser.parse(eqn)
        # even though the reverse rate is zero, this is technically
        # still a bi-directional equation
        self.assertTrue(is_bidirectional)
        self.assertCountEqual([x.symbol for x in reactants], ['A'])
        self.assertCountEqual([x.symbol for x in products], ['C'])

    # # some tests related to the rate constants- missing, non-float
    # def test_missing_reverse_rate_constant_for_bidirectional_reaction(self):
    #     bad_eqn = 'A + B <-> C,0.2'
    #     with self.assertRaises(MissingRateConstantException):
    #         parsers.StringExpressionParser.parse(bad_eqn)
    #     bad_eqn = 'A + B <-> C,0.2,'
    #     with self.assertRaises(MissingRateConstantException):
    #         parsers.StringExpressionParser.parse(bad_eqn)

    # def test_missing_rate_constant_for_unidirectional_reaction(self):
    #     bad_eqn = 'A + B -> C'
    #     with self.assertRaises(MissingRateConstantException):
    #         parsers.StringExpressionParser.parse(bad_eqn)
    #     bad_eqn = 'A + B -> C,'
    #     with self.assertRaises(MissingRateConstantException):
    #         parsers.StringExpressionParser.parse(bad_eqn)

    # def test_non_numerical_rate_constant_for_unidirectional_reaction(self):
    #     bad_eqn = 'A + B -> C,a'
    #     with self.assertRaises(RateConstantFormatException):
    #         parsers.StringExpressionParser.parse(bad_eqn)
    #     bad_eqn = 'A + B <-> C,0.1,k'
    #     with self.assertRaises(RateConstantFormatException):
    #         parsers.StringExpressionParser.parse(bad_eqn)
    #     bad_eqn = 'A + B <-> C,k,0.2'
    #     with self.assertRaises(RateConstantFormatException):
    #         parsers.StringExpressionParser.parse(bad_eqn)
    #     bad_eqn = 'A + B <-> C,k,k'
    #     with self.assertRaises(RateConstantFormatException):
    #         parsers.StringExpressionParser.parse(bad_eqn)

    # def test_missing_coefficient_in_reactants(self):
    #     bad_eqn = 'A + *B <-> C,0.1,0.1'
    #     with self.assertRaises(MalformattedReactionException):
    #         parsers.StringExpressionParser.parse(bad_eqn)

    # def test_bad_symbols_raise_exceptions(self):
    #     with self.assertRaises(InvalidSymbolName):
    #         parsers.StringExpressionParser.check_symbol_name('2A')
    #     with self.assertRaises(InvalidSymbolName):
    #         parsers.StringExpressionParser.check_symbol_name('-A')
    #     with self.assertRaises(InvalidSymbolName):
    #         parsers.StringExpressionParser.check_symbol_name('!A')
    #     with self.assertRaises(InvalidSymbolName):
    #         parsers.StringExpressionParser.check_symbol_name('A-!')

    # def test_bad_symbol_coefficient(self):
    #     bad_eqn = 'A + 2A*B <-> C,0.1,0.1'
    #     with self.assertRaises(MalformattedReactionException):
    #         parsers.StringExpressionParser.parse(bad_eqn)

    # def test_adds_repeated_symbol_coefficients(self):
    #     eqn = 'A + 2*A + B + 3*A <-> C,0.1,0.1'
    #     reactants, products, fwd_k, rev_k, is_bidirectional = parsers.StringExpressionParser.parse(
    #         eqn)
    #     for r in reactants:
    #         if r.symbol == 'A':
    #             self.assertEqual(r.coefficient, 6)

    # def test_single_reactant_equation(self):
    #     eqn = 'T <-> Tf,0.5,0.5'
    #     reactants, products, fwd_k, rev_k, is_bidirectional = parsers.StringExpressionParser.parse(
    #         eqn)
    #     self.assertEqual(len(reactants), 1)
    #     self.assertEqual(reactants[0], Reactant('T', 1))
    #     self.assertEqual(len(products), 1)
    #     self.assertEqual(products[0], Product('Tf', 1))
