__author__ = 'brian'

import sys
import os
import unittest

import numpy as np
import numpy.testing as npt

from src.custom_exceptions import InvalidInitialConditionException, \
    InitialConditionGivenForMissingElement, \
    InvalidSimulationTimeException
from src.model_solvers import ODESolver, ODESolverWJacobian
from src.models import Model
from src.reaction_components import Reaction, Reactant, Product


class TestODESolver(unittest.TestCase):

    def setUp(self):
        """
        equations:
        2*A + B <--0.2,0.5 --> C
        3*C + D --5--> E
        """

        # equation1:
        rx1 = Reaction(
            [Reactant('A', 2), Reactant('B', 1)],
            [Product('C', 1)],
            0.2,
            0.5
        )

        # equation2:
        rx2 = Reaction(
            [Reactant('C', 3), Reactant('D', 1)],
            [Product('E', 1)],
            5,
            0.0
        )
        self.reactions = [rx1, rx2]

        m = Model(self.reactions, ['A', 'B', 'D'], list('ABCDE'))
        self.solver = ODESolver(m)

    def test_rate_law_creation(self):
        """
        equations:
        2*A + B <--0.2,0.5 --> C
        3*C + D --5--> E

        Based on our equations created in the mocked Model, we have 4 rate laws:
        recall that all the forward reactions are treated first, then reverse
        r1 = 0.2*[A]^2[B]
        r2 = 5*[C]^3[D]
        r3 = 0.5*[C]
        r4 = 0*[E] = 0

        Those rate laws will be returned as a list of functions which will be used by iterative ode solver
        If we pass an array of concentrations, we can verify that the code result produced by the code matches
        the hand calculation.
        """
        # set some values on the 'concentration' array
        cc = [2.0, 1.2, 3.0, 1.3, 0.4]

        rate_funcs = self.solver._calculate_rate_law_funcs(self.reactions)

        rate_vals = []
        for f in rate_funcs:
            rate_vals.append(f(cc))

        expected_rates = [
            0.2*cc[0]**2*cc[1],
            5*cc[2]**3*cc[3],
            0.5*cc[2],
            0.0
        ]
        npt.assert_allclose(rate_vals, expected_rates)

    def test_species_mapping_func(self):
        result = self.solver.model.get_species_mapping()
        expected = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
        self.assertEqual(result, expected)

    def test_stoich_matrix_formed_correctly(self):
        result_mtx = self.solver.N

        expected_result = np.zeros((5, 4))
        expected_result[:, 0] = np.array([-2, -1, 1, 0, 0])
        expected_result[:, 1] = np.array([0, 0, -3, -1, 1])
        expected_result[:, 2] = np.array([2, 1, -1, 0, 0])
        expected_result[:, 3] = np.array([0, 0, 3, 1, -1])

        npt.assert_allclose(result_mtx, expected_result)

    def test_negative_initial_condition_raises_exception(self):
        with self.assertRaisesRegex(InvalidInitialConditionException, '-0.2'):
            self.solver.equilibrium_solution({
                'A': 0.1,
                'B': -0.2,
                'D': 3.0
            }, 30)

    def test_negative_simulation_time_raises_exception(self):
        with self.assertRaisesRegex(InvalidSimulationTimeException, '-5'):
            self.solver.equilibrium_solution({
                'A': 0.1,
                'B': 0.2,
                'D': 3.0
            }, -5)


class TestODESolverWJacobian(unittest.TestCase):

    def setUp(self):
        """
        equations:
        2*A + B <--0.2,0.5 --> C
        3*C + D --5--> E
        """

        # equation1:
        rx1 = Reaction(
            [Reactant('A', 2), Reactant('B', 1)],
            [Product('C', 1)],
            0.2,
            0.5
        )

        # equation2:
        rx2 = Reaction(
            [Reactant('C', 3), Reactant('D', 1)],
            [Product('E', 1)],
            5,
            0.0
        )
        self.reactions = [rx1, rx2]

        m = Model(self.reactions, ['A', 'B', 'D'], list('ABCDE'))
        self.solver = ODESolverWJacobian(m)

    def test_negative_initial_condition_raises_exception(self):
        with self.assertRaisesRegex(InvalidInitialConditionException, '-0.2'):
            self.solver.equilibrium_solution({
                'A': 0.1,
                'B': -0.2,
                'D': 3.0
            }, 30)

    def test_negative_simulation_time_raises_exception(self):
        with self.assertRaisesRegex(InvalidSimulationTimeException, '-5'):
            self.solver.equilibrium_solution({
                'A': 0.1,
                'B': 0.2,
                'D': 3.0
            }, -5)


    def test_jacobian_value(self):
        # For a simple model where we calculate by hand, compare the hand-calculated
        # (assumed correct!) value to
        # the one calculated by the Solver.
        # equation1: A + 2*B <-> C
        rx1 = Reaction(
            [Reactant('A', 1), Reactant('B', 2)],
            [Product('C', 1)],
            0.2,
            0.5
        )
        # equation2: C + D <-> E
        rx2 = Reaction(
            [Reactant('C', 1), Reactant('D', 1)],
            [Product('E', 1)],
            5,
            2.3
        )
        reactions = [rx1, rx2]

        m = Model(reactions, ['A', 'B', 'D'], list('ABCDE'))
        solver = ODESolverWJacobian(m)

        # the equilibrium_solution method is called with this:
        X0 = {'A': 1.2,
              'B': 2.5,
              'C': 0.2,
              'D': 5.2,
              'E': 1.3
        }
        # BUT, the jacobian function gets a numpy array
        # which is prepared by the Model instance. Transform
        # X0 from a dict to array.
        X0 = m.setup_initial_conditions(X0)
        calculated_jacobian = solver._jacobian(X0)

        k = solver.kvals
        expected_jacobian = np.empty((5, 5))
        expected_jacobian[0, :] = np.array(
            [-k[0]*X0[1]**2, -2*k[0]*X0[0]*X0[1], k[2], 0, 0])
        expected_jacobian[1, :] = np.array(
            [-2*k[0]*X0[1]**2, -4*k[0]*X0[0]*X0[1], 2*k[2], 0, 0])
        expected_jacobian[2, :] = np.array(
            [k[0]*X0[1]**2, 2*k[0]*X0[0]*X0[1], -k[1]*X0[3]-k[2], -k[1]*X0[2], k[3]])
        expected_jacobian[3, :] = np.array(
            [0, 0, -k[1]*X0[3], -k[1]*X0[2], k[3]])
        expected_jacobian[4, :] = np.array(
            [0, 0, k[1]*X0[3], k[1]*X0[2], -k[3]])

        npt.assert_allclose(calculated_jacobian, expected_jacobian)

    def test_dxdt_value(self):
        # For a simple model where we calculate by hand, compare 
        # the hand-calculated (assumed correct!) value to
        # the one calculated by the Solver.
        # equation1: A + 2*B <-> C
        rx1 = Reaction(
            [Reactant('A', 1), Reactant('B', 2)],
            [Product('C', 1)],
            0.2,
            0.5
        )
        # equation2: C + D <-> E
        rx2 = Reaction(
            [Reactant('C', 1), Reactant('D', 1)],
            [Product('E', 1)],
            5,
            2.3
        )
        reactions = [rx1, rx2]

        m = Model(reactions, ['A', 'B', 'D'], list('ABCDE'))
        solver = ODESolverWJacobian(m)

        # the equilibrium_solution method is called with this:
        X0 = {'A': 1.2,
              'B': 2.5,
              'C': 0.2,
              'D': 5.2,
              'E': 1.3
        }
        # BUT, the jacobian function gets a numpy array
        # which is prepared by the Model instance. Transform
        # X0 from a dict to array.
        X0 = m.setup_initial_conditions(X0)
        calculated_dxdt = solver._dX_dt(X0)

        k = solver.kvals
        expected_dxdt = np.empty(5)
        expected_dxdt[0] = -k[0]*X0[0]*X0[1]**2 + k[2]*X0[2]
        expected_dxdt[1] = -2*k[0]*X0[0]*X0[1]**2 + 2*k[2]*X0[2]
        expected_dxdt[2] = k[0]*X0[0]*X0[1]**2 - \
            k[1]*X0[2]*X0[3] - k[2]*X0[2] + k[3]*X0[4]
        expected_dxdt[3] = -k[1]*X0[2]*X0[3] + k[3]*X0[4]
        expected_dxdt[4] = k[1]*X0[2]*X0[3] - k[3]*X0[4]

        npt.assert_allclose(calculated_dxdt, expected_dxdt)
