import argparse
import json

import pandas as pd

from src.model_factories import JsonModelFactory
from src.model_solvers import ODESolverWJacobian
from src.batch_process import calculate
from src.utils import prep_input_table
from src.unit_conversion import get_conversion_factor


COMMON_UNIT = 'nmol/L'

def parse_commandline_args():
    '''
    This function handles the parsing of command line arguments passed 
    via stdin
    '''

    parser = argparse.ArgumentParser()

    parser.add_argument('-m',
                        '--model',
                        dest='model_file',
                        required=True,
                        help='The model file in JSON format.')

    parser.add_argument('-i',
                        '--input',
                        dest='input_file',
                        required=True,
                        help='Path to a table containing initial conditions.')

    parser.add_argument('-u',
                        '--units',
                        dest='units_mapping',
                        required=True,
                        help=('JSON-format string giving the units of each column'
                              ' in the input table.'))

    parser.add_argument('-o',
                        '--output',
                        dest='output_file',
                        required=False,
                        help='Path to output results table.')

    parser.add_argument('-t',
                        '--time',
                        dest='tmax',
                        required=False,
                        default=30,
                        help=('A dimensionless time controlling how long the'
                              ' simulation should run for.'))

    return parser.parse_args()


def main(model_file, input_df, tmax):
    '''

    Calculates the equilibrium concentrations for the model system
    specified and initial conditons provided. Note that the initial
    conditions NEED to be in a single, consistent unit of measure.

    :param model_file: Path to a JSON-format file specifying
    the desired model.

    :param input_df: A pandas DataFrame of initial conditions.

    :param tmax: The length of the simulation-- in dimensionless time.
    '''
    model = JsonModelFactory(model_file).get_model()
    solver = ODESolverWJacobian(model)

    # for the Tru-T model with SHBG, we need to halve the
    # SHBG to reflect dimer status:
    input_df['SHBG'] = 0.5 * input_df['SHBG']

    return calculate(input_df, solver, tmax)


if __name__ == '__main__':
    args = parse_commandline_args()

    unit_mapping = json.loads(args.units_mapping)
    df = prep_input_table(args.input_file, unit_mapping, COMMON_UNIT)
    results = main(args.model_file, df, args.tmax)

    # rather than having tons of input args, simply tailor this
    # to our most common use-case here. This is, after all,
    # only used when we invoke from a command prompt

    # The outputs from the calculation. This is in addition
    # to the inputs supplied.
    # Note that we map the free T to the same unit as the input T
    # for ease.
    output_mapping = {
        'Tf': unit_mapping['T']
    }
    keepcols = list(output_mapping.keys())

    # subset the results and convert units:
    results = results.loc[:, keepcols]
    for species in results.columns:
        cf = get_conversion_factor(species, COMMON_UNIT, output_mapping[species])
        results.loc[:, species] = cf * results.loc[:, species]

    # append the inputs/initial conditions
    orig_input = pd.read_table(args.input_file, index_col=0)

    final_results = pd.merge(results, orig_input, left_index=True, right_index=True)

    final_results['pct_ft'] = 100 * (final_results['Tf']/final_results['T'])

    if args.output_file:
        final_results.to_csv(args.output_file, sep='\t')
    else:
        print(final_results)
