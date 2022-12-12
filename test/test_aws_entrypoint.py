import unittest
import os
import json

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
        pass

    def test_missing_return_species(self):
        pass

    def test_good_response(self):
        '''
        Tests the case where the calculation goes as expected.
        '''
        p = os.path.join(this_dir, 'test_lambda_payload_1.json')
        with open(p) as fin:
            j = json.load(fin)
        result = lambda_entrypoint(j, {})
        self.assertEqual(result['statusCode'], 200)
        