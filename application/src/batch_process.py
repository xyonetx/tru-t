import pandas as pd
import numpy as np

BATCH_SIZE = 500


def process_row(row, solver, tmax):
    """
    A method for using with apply on the row axis
    sets up the initial conditions and runs until convergence
    returns a pandas Series with the equilibrium concentrations
    of all species

    :param row: A row (pd.Series) with the initial conditions

    :param species_set: 
    """

    sample_to_column_mapping, solution, t = solver.equilibrium_solution(
        row.to_dict(), tmax)

    final_vals = solution[-1, :]
    index = ['']*len(final_vals)
    for sample, col_idx in sample_to_column_mapping.items():
        index[col_idx] = sample
    s = pd.Series(final_vals, index=index)
    return s


def calculate(df, solver, tmax):
    """
    Calculate the equilibrium concentrations for the data
    in the passed dataframe.

    :param df: is a Pandas DataFrame instance.
    
    :param solver: an instance of src.model_solvers.Solver

    It should have column names that match the species given
    in the model file so we can map the dataframe's values to
    the initial conditions properly.

    Furthermore, the values in the dataframe should all have the same units--
    we make no consideration for the relative units here. That should all be
    cleared up prior to calling this function.
    """

    # Rather than depending on us checking the initial conditions for each
    # set of data (as we iterate through `df`), we pre-check the columns of
    # the dataframe to ensure compliance with the necessary initial
    # conditions for our model. If something is wrong, this call will
    # raise an exception
    solver.model.check_initial_conditions(df.columns)

    batch_num = int(np.ceil(df.shape[0]/float(BATCH_SIZE)))
    results = pd.DataFrame()
    for i in range(batch_num):
        start = i*BATCH_SIZE
        end = (i+1)*BATCH_SIZE
        minibatch = df.iloc[start:end]
        miniresults = minibatch.apply(process_row, args=(solver, tmax), axis=1)
        results = pd.concat([results, miniresults])
    return results
