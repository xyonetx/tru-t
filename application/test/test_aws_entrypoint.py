import unittest
import os
import json

import pandas as pd

from aws_lambda_handler import convert_subject, \
    lambda_entrypoint

this_dir = os.path.dirname(os.path.abspath(__file__))


class TestAWSFunctions(unittest.TestCase):

    def test_data_conversion(self):
        '''
        This tests the `convert_subject` function
        which takes the complete set of data
        (in the user-supplied units) and returns
        the data in a set of common units.

        Here, we mock out the `conversion_factor_dict`
        which provides the conversion factors for each
        species + unit
        '''

        # None of the numbers here are real- just
        # mocked values
        mock_conversion_dict = {
            'T': {
                'ng/dL': 2.2,
                'pg/mL': 0.1
            },
            'SHBG': {
                'nmol/L': 2.0
            },
            'Alb': {
                'g/dL': 25.1,
                'g/L': 12.1
            }
        }

        input_dict = {
            "T": {
                "value": 566.2,
                "unit": "ng/dL"
            },
            "SHBG": {
                "value": 40.2,
                "unit": "nmol/L"
            },
            "Alb": {
                "value": 4.3,
                "unit": "g/dL"
            }
        }

        x = convert_subject(('subjectA', input_dict), mock_conversion_dict)
        expected_dict = {
            "T": 566.2*2.2,
            "SHBG": 40.2*2.0,
            "Alb": 4.3*25.1
        }
        self.assertEqual('subjectA', x[0])
        self.assertDictEqual(expected_dict, x[1])

    def test_data_conversion_with_bad_input(self):
        '''
        If an unexpected input is received, check that
        we are raising appropriate exceptions.
        '''
        # None of the numbers here are real- just
        # mocked values
        mock_conversion_dict = {
            'T': {
                'ng/dL': 2.2,
                'pg/mL': 0.1
            },
            'SHBG': {
                'nmol/L': 2.0
            },
            'Alb': {
                'g/dL': 25.1,
                'g/L': 12.1
            }
        }

        # The species "X" was not expected
        input_dict = {
            "X": {
                "value": 566.2,
                "unit": "ng/dL"
            },
            "SHBG": {
                "value": 40.2,
                "unit": "nmol/L"
            },
            "Alb": {
                "value": 4.3,
                "unit": "g/dL"
            }
        }

        with self.assertRaisesRegex(
                Exception, 'Did not recognize the following species: X'):
            convert_subject(('subjectA', input_dict), mock_conversion_dict)

        # The species "T" was given in a bad unit
        input_dict = {
            "T": {
                "value": 566.2,
                "unit": "nmol/dL" # <-- not expected
            },
            "SHBG": {
                "value": 40.2,
                "unit": "nmol/L"
            },
            "Alb": {
                "value": 4.3,
                "unit": "g/dL"
            }
        }

        with self.assertRaisesRegex(
                Exception, 'Did not recognize the unit: nmol/dL'):
            convert_subject(('subjectA', input_dict), mock_conversion_dict)

        # one of the inputs is missing a "value" key
        input_dict = {
            "T": {
                "val": 566.2, #<-- should be "value"
                "unit": "ng/dL"
            },
            "SHBG": {
                "value": 40.2,
                "unit": "nmol/L"
            },
            "Alb": {
                "value": 4.3,
                "unit": "g/dL"
            }
        }

        with self.assertRaisesRegex(
                Exception, "T was missing 'value' key"):
            convert_subject(('subjectA', input_dict), mock_conversion_dict)

        # one of the inputs is missing a "unit" key
        input_dict = {
            "T": {
                "value": 566.2
            },
            "SHBG": {
                "value": 40.2,
                "unit": "nmol/L"
            },
            "Alb": {
                "value": 4.3,
                "unit": "g/dL"
            }
        }

        with self.assertRaisesRegex(
                Exception, "T was missing 'unit' key"):
            convert_subject(('subjectA', input_dict), mock_conversion_dict)
    
    def test_missing_initial_conditions(self):
        p = os.path.join(this_dir, 'test_lambda_payload_1.json')
        with open(p) as fin:
            j = json.load(fin)
        # remove the initial_conditions dict:
        j.pop('initial_conditions')
        result = lambda_entrypoint(j, {})
        self.assertEqual(result['statusCode'], 400)
        self.assertTrue("initial_conditions" in result['body'])

    def test_missing_return_species(self):
        p = os.path.join(this_dir, 'test_lambda_payload_1.json')
        with open(p) as fin:
            j = json.load(fin)
        # remove the return_species dict:
        j.pop('return_species')
        result = lambda_entrypoint(j, {})
        self.assertEqual(result['statusCode'], 400)
        self.assertTrue("return_species" in result['body'])

    def test_good_response(self):
        '''
        Tests the case where the calculation goes as expected.
        '''
        p = os.path.join(this_dir, 'test_lambda_payload_1.json')
        with open(p) as fin:
            j = json.load(fin)
        result = lambda_entrypoint(j, {})
        self.assertEqual(result['statusCode'], 200)
        data = json.loads(result['body'])
        for subject, measurement_dict in data.items():
            for species, d in measurement_dict.items():
                self.assertTrue(d.keys() == set(["value", "unit"]))

    def test_bad_return_species_name(self):
        # if one of the return species is not recognized
        p = os.path.join(this_dir, 'test_lambda_payload_1.json')
        with open(p) as fin:
            j = json.load(fin)
        # remove the return_species dict:
        j['return_species'] = {
            'XYZ': 'ng/dL'
        }
        result = lambda_entrypoint(j, {})
        self.assertEqual(result['statusCode'], 400)
        self.assertTrue("XYZ was not recognized" in result['body'])

    def test_bad_return_species_unit(self):
        # if one of the return species has a unit that we 
        # don't understand
        p = os.path.join(this_dir, 'test_lambda_payload_1.json')
        with open(p) as fin:
            j = json.load(fin)
        # remove the return_species dict:
        j['return_species'] = {
            'Tf': 'abc'
        }
        result = lambda_entrypoint(j, {})
        self.assertEqual(result['statusCode'], 400)
        self.assertTrue("abc for species Tf was not recognized" \
                        in result['body'])

    def test_good_response_with_returned_ic(self):
        '''
        Tests the case where the calculation goes as expected AND we 
        return the initial conditions
        '''
        p = os.path.join(this_dir, 'test_lambda_payload_1.json')
        with open(p) as fin:
            j = json.load(fin)
        
        j['return_initial_conditions'] = True
        result = lambda_entrypoint(j, {})
        self.assertEqual(result['statusCode'], 200)
        result = json.loads(result['body'])
        for s, d in result.items():
            self.assertTrue(d.keys() == set(['Tf', 'T_0', 'SHBG_0', 'Alb_0']))

        j['return_initial_conditions'] = True
        j['ic_postfix'] = '_init'
        result = lambda_entrypoint(j, {})
        self.assertEqual(result['statusCode'], 200)
        result = json.loads(result['body'])
        for s, d in result.items():
            self.assertTrue(d.keys() == set(['Tf', 'T_init', 'SHBG_init', 'Alb_init']))
