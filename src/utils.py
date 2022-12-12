import pandas as pd

from .unit_conversion import get_conversion_factor


def prep_input_table(table_path, unit_mapping, common_unit):
    '''
    Most often, we have a table of measurements where each column
    has a different, but consistent measurement. This is more constrained
    than the payloads we allow via the lambda function endpoint.

    This function helps by preparing the table to have consistent units
    and allows us to interface with the lambda endpoint more easily
    '''
    df = pd.read_table(table_path, index_col=0)
    for species, unit in unit_mapping.items():
        cf = get_conversion_factor(species, unit, common_unit)
        df.loc[:, species] = cf * df.loc[:, species]
    return df


def prepare_final_result(result,
                         ic_dict,
                         return_species,
                         return_ic,
                         ic_postfix,
                         common_unit):
    '''
    Modifies a result dataframe to be in accordance with
    the arguments. Often these arguments are taken from a JSON
    request to an API, but this function is not concerned with
    that. Rather, it modifies and returns a dictionary. See unit tests
    for structure, etc.

    `result` is the dataframe of all species 
        (the result of an equilibrium calculation)
    `ic_dict` is the dict used for initial conditions
    `return_species` is a dict giving the desired species to return
        (e.g. only free T in units of ng/dL)
    `return_ic` is a boolean indicating whether the request would like
        the initial conditions to be echoed back with the result 
    `ic_postfix` is a string to append to the initial conditions so that
        they are not confused with the equilibrium values.
    '''
    subset_result = result.loc[:, return_species.keys()]

    # Now convert the units to those desired:
    for species, desired_unit in return_species.items():
        cf = get_conversion_factor(species, common_unit, desired_unit)
        subset_result[species] = cf * subset_result[species]

    # if they have requested the initial conditions be returned, append those:
    if return_ic:
        result_payload = {}
        for subject_id, subject_dict in ic_dict.items():
            updated_dict = {}
            for species, measurement_dict in subject_dict.items():
                updated_dict[species + ic_postfix] = measurement_dict
            for species, unit in return_species.items():
                updated_dict[species] = {
                    "value": subset_result.loc[subject_id, species],
                    "unit": unit
                }
            result_payload[subject_id] = updated_dict
        return result_payload
    else:
        result_payload = subset_result.to_dict(orient='index')
        for subject_id, measurement_dict in result_payload.items():
            # measurement_dict looks like: {'Tf': 18.23, ...}
            updated_dict = {}
            for species, unit in return_species.items():                
                updated_dict[species] = {
                    "value": measurement_dict[species],
                    "unit": unit
                }
            result_payload[subject_id] = updated_dict
        return result_payload