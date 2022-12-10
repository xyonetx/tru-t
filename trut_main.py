import argparse

import pandas as pd

from src.model_factories import JsonModelFactory
from src.model_solvers import ODESolverWJacobian
from src.batch_process import calculate


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

    parser.add_argument('-o',
                        '--output',
                        dest='output_file',
                        required=False,
                        help='Path to output results table.')

    parser.add_argument('-t',
                        '--time',
                        dest='tmax',
                        required=False,
                        default = 30,
                        help=('A dimensionless time controlling how long the'
                             ' simulation should run for.'))

    return parser.parse_args()


def main(model_file, input_file, tmax):
    '''

    Calculates the equilibrium concentrations for the model system
    specified and initial conditons provided.

    :param model_file: Path to a JSON-format file specifying
    the desired model.

    :param input_file: Path to a tab-delimited table of initial
    conditions.
    '''
    model = JsonModelFactory(model_file).get_model()
    solver = ODESolverWJacobian(model)
    df = pd.read_table(input_file, index_col=0)

    # for the Tru-T model with SHBG, we need to halve the
    # SHBG to reflect dimer status:
    df['SHBG'] = 0.5 * df['SHBG']

    return calculate(df, solver, tmax)


if __name__ == '__main__':
    args = parse_commandline_args()
    results = main(args.model_file, args.input_file, args.tmax)
    if args.output_file:
        results.to_csv(args.output_file, sep='\t')
    else:
        print(results)
        