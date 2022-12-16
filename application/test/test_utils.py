import unittest
import unittest.mock as mock
import os

import pandas as pd

from src.utils import prepare_final_result, \
    prep_input_table


this_dir = os.path.dirname(os.path.abspath(__file__))

# a mock function for testing the table prep function

FACTOR_DICT = {
    'T': 2.0,
    'SHBG': 1.0,
    'Alb': 3.0
}


def mock_get_cf(species, unit, common_unit):
    return FACTOR_DICT[species]


class TestUtilsFunctions(unittest.TestCase):

    @mock.patch('src.utils.get_conversion_factor', mock_get_cf)
    def test_prep_input_table(self):
        f = os.path.join(this_dir, 'test_table_in_different_units.tsv')
        unit_mapping = {
            'T': 'ng/dL',
            'SHBG': 'nmol/L',
            'Alb': 'g/dL'
        }
        df = prep_input_table(f, unit_mapping, 'nmol/L')
        expected_df = pd.read_table(f, index_col=0)
        for species in FACTOR_DICT.keys():
            expected_df.loc[:, species] = \
                FACTOR_DICT[species] * expected_df.loc[:, species]
        self.assertTrue(all(df == expected_df))


    @mock.patch('src.utils.get_conversion_factor')
    def test_result_prep(self, mock_get_conversion_factor):
        '''
        Tests the function that prepares the result payload
        '''
        result = pd.DataFrame([
            {
                'Tf': 1.01,
                'T': 1.1,
                'SHBG': 2.0
            },
            {
                'Tf': 2.02,
                'T': 3.1,
                'SHBG': 4.2
            }
        ], index=['subjectA', 'subjectB'])
        mock_get_conversion_factor.return_value = 2.0
        ic_dict = {
            'subjectA': {
                'X': {
                    "value": 0.2,
                    "unit": "ng/dL"
                }
            },
            'subjectB': {
                'X': {
                    "value": 0.3,
                    "unit": "ng/dL"
                }
            }
        }
        return_species = {
            'Tf': 'ng/dL'
        }
        r = prepare_final_result(result, ic_dict, return_species, True, '_Z', 'ng/dL')
        expected_result = {
            "subjectA": {
                "X_Z": {
                    "value": 0.2,
                    "unit": "ng/dL"
                },
                "Tf": {
                    "value": 2.02,
                    "unit": "ng/dL"
                }
            },
            "subjectB": {
                "X_Z": {
                    "value": 0.3,
                    "unit": "ng/dL"
                },
                "Tf": {
                    "value": 4.04,
                    "unit": "ng/dL"
                }
            }
        }
        self.assertDictEqual(r, expected_result)

        r = prepare_final_result(result, ic_dict, return_species, False, '_Z', 'ng/dL')
        expected_result = {
            "subjectA": {
                "Tf": {
                    "value": 2.02,
                    "unit": "ng/dL"
                }
            },
            "subjectB": {
                "Tf": {
                    "value": 4.04,
                    "unit": "ng/dL"
                }
            }
        }
        self.assertDictEqual(r, expected_result)

        return_species = {}
        r = prepare_final_result(result, ic_dict, return_species, False, '_Z', 'ng/dL')
        expected_result = {
            "subjectA": {},
            "subjectB": {}
        }
        self.assertDictEqual(r, expected_result)

        return_species = {}
        r = prepare_final_result(result, ic_dict, return_species, True, '_Z', 'ng/dL')
        expected_result = {
            "subjectA": {
                "X_Z": {
                    "value": 0.2,
                    "unit": "ng/dL"
                }
            },
            "subjectB": {
                "X_Z": {
                    "value": 0.3,
                    "unit": "ng/dL"
                }
            }
        }