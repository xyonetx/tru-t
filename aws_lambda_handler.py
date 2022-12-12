from itertools import repeat
import json

import pandas as pd

from src.unit_conversion import precalculate_conversion_factors, \
    DISPLAY_TO_UNIT_MAP
from src.utils import prepare_final_result

from trut_main import main as trut_main

'''
Note that for an API Gateway proxy integration, the result
object should look like:
{
    "isBase64Encoded": true|false,
    "statusCode": httpStatusCode,
    "headers": { "headerName": "headerValue", ... },
    "multiValueHeaders": { "headerName": ["headerValue", "headerValue2", ...], ... },
    "body": "..."
}
https://docs.aws.amazon.com/apigateway/latest/developerguide/
set-up-lambda-proxy-integrations.html
#api-gateway-simple-proxy-for-lambda-output-format
'''

# The JSON-format model file we use:
MODEL_FILE = 'testosterone_model_spec.json'

# all the potential species in the result:
ALL_SPECIES = [
    'Alb',
    'AlbT',
    'S1',
    'S1T',
    'SHBG',
    'SHBGT'
    'SHBGT2',
    'T',
    'Tf'
]

# We only accept these species for initial conditions
ALL_IC_SPECIES = ['T', 'Alb', 'SHBG']

# convert everything to this unit when performing calc
COMMON_UNIT = 'nmol/L'

# establish accepted units. For each species, we only
# allow certain units:
accepted_units_dict = {}
accepted_units_dict['T'] = ['ng/dL', 'pg/mL', 'nmol/L']
accepted_units_dict['SHBG'] = ['nmol/L', ]
accepted_units_dict['Alb'] = ['g/dL', 'g/L', 'nmol/L']


def generate_response(status_code, body):
    return {
        "statusCode": status_code,
        "body": body
    }


def handle_args(payload):
    try:
        initial_conditions = payload['initial_conditions']
    except KeyError as ex:
        raise Exception(f'Request must include the {ex} key.')

    try:
        return_species = payload['return_species']
    except KeyError as ex:
        raise Exception(f'Request must include the {ex} key.')

    if not type(initial_conditions) is dict:
        raise Exception('The "initial_conditions" key should'
                        ' reference an object. See API docs for the'
                        ' structure')

    if not type(return_species) is dict:
        raise Exception('The "return_species" key should'
                        ' reference an object. See API docs for the'
                        ' structure')
    else:
        # check the dict. This way we don't perform the calculations
        # and THEN fail out
        for species, unit in return_species.items():
            if species not in ALL_SPECIES:
                raise Exception(f'Species {species} was not recognized and'
                                ' cannot be returned with the result.')
            if unit not in DISPLAY_TO_UNIT_MAP.keys():
                raise Exception(f'Unit {unit} for species {species} was not'
                                ' recognized and cannot be returned'
                                ' with the result.')
    try:
        return_ic = bool(payload['return_initial_conditions'])
    except KeyError:
        # If not specified, then we default to False
        return_ic = False

    try:
        ic_postfix = payload['ic_postfix']
    except KeyError:
        ic_postfix = '_0'

    return initial_conditions, \
        return_species, \
        return_ic, \
        ic_postfix


def convert_subject(subject_and_spec_tuple, conversion_factor_dict):
    '''
    Takes a tuple of (subject_id, <dict>)
    and converts the values to the common unit
    '''
    key = subject_and_spec_tuple[0]
    d = subject_and_spec_tuple[1]
    converted = {}
    for species, spec in d.items():
        if species not in ALL_IC_SPECIES:
            raise Exception('Did not recognize the'
                            f' following species: {species}')
        try:
            unit = spec['unit']
            value = spec['value']
        except KeyError as ex:
            raise Exception(f'Initial condition for {species}'
                            f' was missing {ex} key.')

        try:
            cf = conversion_factor_dict[species][unit]
        except KeyError as ex:
            raise Exception(f'Did not recognize the unit: {unit}.'
                            f' For {species}, we accept: {accepted_units_dict[species]}')
        converted[species] = cf * value
    return (key, converted)


def lambda_entrypoint(event, context):
    '''
    This is the method signature required by AWS Lambda.  

    Input args are passed as part of the `event` arg, and may be
    accessed like a dictionary.  

    Note that given a payload of 

    {"foo":{"x":1, "y":2}, "bar":"something"}

    One can get "foo" by:
    foo = event['foo']

    and variable foo itself will be a native python dictionary

    If the payload is a JSON list:
    [
        {"foo":{"x":1, "y":2}, "bar":"something"},
        {"foo":{"x":1, "y":2}, "bar":"something"},
        ...
    ]
    then `event` is a native python list.
    '''
    try:
        initial_conditions, \
            return_species, \
            return_ic, \
            ic_postfix = handle_args(event)
    except Exception as ex:
        return generate_response(400, f'{ex}')

    # convert the initial conditions to the common unit:
    conversion_factor_dict = precalculate_conversion_factors(
        ALL_IC_SPECIES, accepted_units_dict, COMMON_UNIT)
    try:
        df = pd.DataFrame.from_dict(
            dict(
                map(convert_subject,
                    initial_conditions.items(),
                    repeat(conversion_factor_dict)
                    )
            ),
            orient='index')
    except Exception as ex:
        return generate_response(400, f'{ex}')

    result = trut_main(MODEL_FILE, df, 30.0)
    result = prepare_final_result(result,
                                  initial_conditions,
                                  return_species,
                                  return_ic,
                                  ic_postfix,
                                  COMMON_UNIT)
    return generate_response(200, json.dumps(result))
