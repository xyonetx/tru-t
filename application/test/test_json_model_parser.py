__author__ = 'brian'

import unittest
import os

from src.custom_exceptions import JsonParseException, \
    MalformattedReactionDirectionSymbolException, \
    RequiredSpeciesException, \
    RateConstantFormatException, \
    InconsistentDirectionalityException, \
    MissingRateConstantException

from src.model_factories import JsonModelFactory

this_dir = os.path.dirname(os.path.abspath(__file__))


class TestJsonModelFactory(unittest.TestCase):
    '''
    Tests related to the model factory based on JSON formats
    '''

    def test_rate_constant_method(self):
        '''
        These are double-tested below in the TestJsonModelReader,
        but we also test here.
        '''
        # this is a correct model just used to get a valid factory
        f = os.path.join(this_dir, 'test_json_model_9.json')
        f = JsonModelFactory(f)

        # Now that we have the factory, we can test the method:
        rx_exp = "" # used as a placeholder-- does not matter what this is.

        # requiring fwd_k in a bidirectional
        r = f._handle_rate_constant(
            {
                "reaction_expression": rx_exp,
                "fwd_k": 1.0,
                "rev_k": 2.0
            },
            "fwd_k",
            True,
            required=True
        )
        self.assertEqual(r, 1.0)

        # requiring rev_k in a bidirectional
        r = f._handle_rate_constant(
            {
                "reaction_expression": rx_exp,
                "fwd_k": 1.0,
                "rev_k": 2.0
            },
            "rev_k",
            True,
            required=True
        )
        self.assertEqual(r, 2.0)

        # get rev_k for bidirectional even though not required.
        r = f._handle_rate_constant(
            {
                "reaction_expression": rx_exp,
                "fwd_k": 1.0,
                "rev_k": 2.0
            },
            "rev_k",
            True,
            required=False
        )
        self.assertEqual(r, 2.0)

        # For a bidirectional equation, users MUST
        # specify a rev_k (to avoid ambiguity). 
        with self.assertRaisesRegex(
                MissingRateConstantException, 'no reverse rate constant'):
            f._handle_rate_constant(
                {
                    "reaction_expression": rx_exp,
                    "fwd_k": 1.0,
                },
                "rev_k",
                True, # IS bidirectional
                required=False
            )

        # If the direction is unidirectional, but a
        # reverse k is specified, this is technically inconsistent.
        # HOWEVER, we have this logic elsewhere
        # (see test_rejects_model_with_rev_k_for_unidirectional).
        # For this function we are testing, we should not raise
        # an exception
        r = f._handle_rate_constant(
            {
                "reaction_expression": rx_exp,
                "fwd_k": 1.0,
                "rev_k": 2.0
            },
            "rev_k",
            False, # unidirectional
            required=False
        )
        self.assertEqual(r, 2.0)

        # for a unidirectional, we don't need a reverse
        # constant and this function should return zero.
        r = f._handle_rate_constant(
            {
                "reaction_expression": rx_exp,
                "fwd_k": 1.0,
            },
            "rev_k",
            False,
            required=False
        )
        self.assertEqual(r, 0.0)

        # Missing fwd_k-- never ok.
        with self.assertRaisesRegex(MissingRateConstantException, 'fwd_k'):
            f._handle_rate_constant(
                {
                    "reaction_expression": rx_exp,
                    "rev_k": 2.0
                },
                "fwd_k",
                True,
                required=True
            )

class TestJsonModelReader(unittest.TestCase):
    '''
    Tests related to parsing models specified by JSON files.
    '''

    def test_bad_json(self):
        '''
        Test the case where it's not correct JSON format (extra comma)
        '''
        f = os.path.join(this_dir, 'test_json_model_4.json')
        with self.assertRaises(JsonParseException):
            JsonModelFactory(f)

    def test_missing_reaction_section(self):
        '''
        Tests that a missing reactions section raises an exception
        '''

        # this file has 'reaction', not the required 'reactions'
        f = os.path.join(this_dir, 'test_json_model_1.json')
        with self.assertRaisesRegex(JsonParseException, 'needs to have a "reactions" key'):
            JsonModelFactory(f)

        # this file has no 'reactions' section
        f = os.path.join(this_dir, 'test_json_model_2.json')
        with self.assertRaisesRegex(JsonParseException, 'needs to have a "reactions" key'):
            JsonModelFactory(f)

    def test_missing_required_init_section(self):
        '''
        Tests that we raise an exception if we are missing the
        required initial conditions section
        '''
        f = os.path.join(this_dir, 'test_json_model_3.json')
        with self.assertRaisesRegex(JsonParseException, "'required_initial_conditions' key"):
            JsonModelFactory(f)

    def test_bad_reactions_section(self):
        '''
        The "reactions"  key should address a list. If not,
        we raise an exception
        '''
        f = os.path.join(this_dir, 'test_json_model_5.json')
        with self.assertRaisesRegex(JsonParseException, 'should address a list'):
            JsonModelFactory(f)

    def test_badly_formatted_reaction(self):
        '''
        Tests that poorly formatted reaction objects cause an
        exception to be raised.
        '''
        f = os.path.join(this_dir, 'test_json_model_6.json')
        with self.assertRaises(MalformattedReactionDirectionSymbolException):
            JsonModelFactory(f)

    def test_extra_keys_ignored(self):
        '''
        Tests that extra keys in the model file are ignored.
        '''
        f = os.path.join(this_dir, 'test_json_model_7.json')
        JsonModelFactory(f)

    def test_rejects_model_with_extra_initial_condition(self):
        '''
        Tests the situation where we specify an extra required initial condition
        (SHBG in this case) for a model system where that is not represented.
        '''
        f = os.path.join(this_dir, 'test_json_model_8.json')
        with self.assertRaisesRegex(RequiredSpeciesException, 'SHBG'):
            JsonModelFactory(f)

    def test_rejects_model_with_negative_rate_constant(self):
        '''
        Tests the situation where we specify a rate constant that is negative
        and hence non sensible.
        '''
        f = os.path.join(this_dir, 'test_json_model_10.json')
        with self.assertRaisesRegex(RateConstantFormatException, 'fwd_k=-0.1'):
            JsonModelFactory(f)

    def test_rejects_model_with_rev_k_for_unidirectional(self):
        '''
        Tests the situation where we specify a "rev_k" rate constant
        when the equation provided is unidirectional. If the constant
        is zero, however, it's acceptable
        '''
        f = os.path.join(this_dir, 'test_json_model_11.json')
        with self.assertRaisesRegex(
                InconsistentDirectionalityException, 'reverse rate constant'):
            JsonModelFactory(f)

        # this has a 0.0 reverse constant specified, so it's fine
        f = os.path.join(this_dir, 'test_json_model_12.json')
        JsonModelFactory(f)

    def test_backwards_specification_is_rejected(self):
        '''
        If a reaction is written as A + B <- C (even with sensible
        rate constants), we reject.
        '''
        f = os.path.join(this_dir, 'test_json_model_13.json')
        with self.assertRaises(
                MalformattedReactionDirectionSymbolException):
            JsonModelFactory(f)

    def test_non_numeric_rate_constant_rejected(self):
        '''
        If a rate constant is a non-number, reject it
        '''
        # this has a bad fwd_k
        f = os.path.join(this_dir, 'test_json_model_14.json')
        with self.assertRaises(
                RateConstantFormatException):
            JsonModelFactory(f)

        # this has a bad rev_k
        f = os.path.join(this_dir, 'test_json_model_15.json')
        with self.assertRaises(
                RateConstantFormatException):
            JsonModelFactory(f)

    def test_missing_rate_constant_rejected(self):
        '''
        If the reverse direction is missing in a bi-directional
        reject that.
        '''
        f = os.path.join(this_dir, 'test_json_model_16.json')
        with self.assertRaisesRegex(
                MissingRateConstantException, 'no reverse rate'):
            JsonModelFactory(f)

    def test_zero_forward_rate_constant_rejected(self):
        '''
        If the forward rate constant is missing, then we reject
        '''
        f = os.path.join(this_dir, 'test_json_model_17.json')
        with self.assertRaisesRegex(
                MissingRateConstantException, '"fwd_k" is required'):
            JsonModelFactory(f)

    def test_bidirectional_with_zero_fwd_k_is_ok(self):
        '''
        If the forward rate constant is zero in a bidirectional,
        then this is not technically wrong. It just ends up being
        a unidirectional in practice
        '''
        f = os.path.join(this_dir, 'test_json_model_18.json')
        JsonModelFactory(f)

    def test_zero_fwd_rate_constant_is_ok(self):
        '''
        If the forward rate constant is zero in a unidirectional,
        this is not incorrect. It just won't do anything.
        '''
        f = os.path.join(this_dir, 'test_json_model_19.json')
        JsonModelFactory(f)