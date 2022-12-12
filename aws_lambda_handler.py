from itertools import repeat

import pandas as pd

from src.unit_conversion import DISPLAY_TO_UNIT_MAP, \
    convert_unit
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

# We only accept these species for initial conditions
ALL_SPECIES = ['T', 'Alb', 'SHBG']

# convert everything to this unit when performing calc
COMMON_UNIT = 'nmol/L'

# establish accepted units. For each species, we only
# allow certain units:
accepted_units_dict = {}
accepted_units_dict['T'] = ['ng/dL', 'pg/mL', 'nmol/L']
accepted_units_dict['SHBG'] = ['nmol/L', ]
accepted_units_dict['Alb'] = ['g/dL', 'g/L', 'nmol/L']


def precalculate_conversion_factors():
    '''
    Creates a pre-calculated dict for quick lookups of conversion
    factors. This avoids having to perform repeated calls
    to the conversion functions.

    We create a two-level dict. The first level addresses the species
    and the second level addresses the unit. 

    For example, given the dict d:
    d['T']['ng/dL'] would give you the conversion factor to convert T
    # from ng/dL to the common unit.
    # Note that this is only for the free-T calcs we are concerned with
    in this lambda function handler.
    '''
    conversion_factor_dict = {}
    for species in ALL_SPECIES:
        conversion_factor_dict[species] = {}
        for unit in accepted_units_dict[species]:
            cf = get_conversion_factor(species, unit, COMMON_UNIT)
            conversion_factor_dict[species].update({unit: cf})
    return conversion_factor_dict


def get_conversion_factor(species, orig_unit, return_unit):
    '''
    `species` is a string for the entity (e.g. "T", or "Alb")
    `orig_unit` is something like 'ng/dL'
    return_unit is a unit string (e.g. 'nmol/L')
    that it should be converted to

    returns the conversion factor (a float). Thus, you
    will need to take the result of this function
    and multiply it by the value (in the orig_unit)
    '''
    # if SHBG, we do NOT convert units
    # Note that we handle dimer conversion (i.e. multiply by 0.5)
    # in the call to the calculation. Just check that it's given
    # in the canonical unit of nmol/L here
    if species == 'SHBG':
        if orig_unit != 'nmol/L':
            raise Exception('SHBG needs to be in nmol/L')
        return 1.0
    else:
        orig_unit = DISPLAY_TO_UNIT_MAP[orig_unit]
        target_unit = DISPLAY_TO_UNIT_MAP[return_unit]
        return convert_unit(species, orig_unit, target_unit)


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

    try:
        return_ic = bool(payload['return_initial_conditions'])
    except KeyError:
        # If not specified, then we default to False
        return_ic = False

    try:
        ic_postfix = payload['ic_postfix']
    except KeyError:
        ic_postfix = '_0'

    return initial_conditions, return_species, return_ic, ic_postfix


def convert_subject(subject_and_spec_tuple, conversion_factor_dict):
    '''
    Takes a tuple of (subject_id, <dict>)
    and converts the values to the common unit
    '''
    key = subject_and_spec_tuple[0]
    d = subject_and_spec_tuple[1]
    converted = {}
    for species, spec in d.items():
        if species not in ALL_SPECIES:
            raise Exception('Did not recognize the'
                            f' following species: {species}')
        try:
            unit = spec['unit']
            value = spec['value']
        except KeyError as ex:
            raise Exception(f'Initial condition was missing {ex} key.')

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

    # convert the initial conditions:
    conversion_factor_dict = precalculate_conversion_factors()
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
    print(result)
