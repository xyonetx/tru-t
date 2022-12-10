__author__ = 'brian'

import sys
import os
import unittest

import numpy as np
import numpy.testing as npt

from src.custom_exceptions import MissingRequiredInitialConditionsException, \
    InitialConditionGivenForMissingElement

from src.models import Model
from src.model_factories import JsonModelFactory
from src.reaction_components import Reaction, Reactant, Product

this_dir = os.path.dirname(os.path.abspath(__file__))



class TestModel(unittest.TestCase):

    def setUp(self):
        '''
        equations:
        2*A + B <--0.2,0.5 --> C
        3*C + D --5--> E
        '''
        # equation1:
        rx1 = Reaction(
            [Reactant('A', 2), Reactant('B', 1)],
            [Product('C', 1)],
            0.2,
            0.5,
            True
        )

        # equation2:
        rx2 = Reaction(
            [Reactant('C', 3), Reactant('D', 1)],
            [Product('E', 1)],
            5,
            0.0,
            False
        )

        reactions = [rx1, rx2]

        self.model = Model(reactions, ['A', 'B', 'D'], list('ABCDE'))

    def test_species_mapping_func(self):
        '''
        Tests that we create the proper mapping of symbols to array index.

        This is used in the numPy calculations-- since we don't have indexes
        (like in pandas), we need to know which array location corresponds
        to which species for our calculations and mapping back for results.
        '''
        result = self.model.get_species_mapping()
        expected = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
        self.assertEqual(result, expected)

    def test_check_ic_func(self):
        '''
        Tests that the initial condition checking method works as expected.
        '''
        # we require A,B,D for the model to make sense. Try that:
        self.model.check_initial_conditions(['A', 'B', 'D'])

        # If we give more species, that's also fine:
        self.model.check_initial_conditions(['A', 'B', 'D', 'E'])

        # if we don't give all the required, that should fail
        with self.assertRaisesRegex(
                MissingRequiredInitialConditionsException, 'D'):
            self.model.check_initial_conditions(['A', 'B'])

        # if we give a species that doesn't exist in the model,
        # that should fail.
        with self.assertRaisesRegex(
                InitialConditionGivenForMissingElement, 'X'):
            self.model.check_initial_conditions(['A', 'B', 'D', 'X'])

    def test_setup_of_ics(self):
        '''
        Test that we create the proper initial conditions array
        '''
        # the method assumes the prescribed initial conditions have
        # already been validated (e.g. no extra of missing symbols)
        x0 = {'A': 0.2, 'B': 0.3, 'D': 0.5}

        result = self.model.setup_initial_conditions(x0)
        npt.assert_allclose(result, [0.2, 0.3, 0.0, 0.5, 0.0])

    def test_json_representation(self):
        '''
        Test that the to_json method returns the proper payload
        '''
        f = os.path.join(this_dir, 'test_json_model_9.json')
        model = JsonModelFactory(f).get_model()
        result = model.to_json()
