# unit constants:
DECI = 'd'
MILLI = 'm'
PICO = 'p'
NANO = 'n'

PREFIX_DICT = {
    DECI: 0.1,
    MILLI: 0.001,
    PICO: 1e-12,
    NANO: 1e-9,
}

GRAM = 'g'
LITER = 'L'
MOL = 'm'

NANOGRAM = NANO + GRAM
PICOGRAM = PICO + GRAM
DECILITER = DECI + LITER
MILLILITER = MILLI + LITER
NANOMOL = NANO + MOL
PICOMOL = PICO + MOL
PER = '_'

G_PER_L = GRAM + PER + LITER
G_PER_DL = GRAM + PER + DECILITER
NG_PER_DL = NANOGRAM + PER + DECILITER
NG_PER_ML = NANOGRAM + PER + MILLILITER
PG_PER_ML = PICOGRAM + PER + MILLILITER
NMOL_PER_L = NANOMOL + PER + LITER
G_PER_MOL = GRAM + PER + MOL
G_PER_G = GRAM + PER + GRAM  # dummy value to avoid special handling of SHBG

UNIT_DISPLAY_MAP = {
    G_PER_L: 'g/L',
    G_PER_DL: 'g/dL',
    NG_PER_DL: 'ng/dL',
    NG_PER_ML: 'ng/mL',
    PG_PER_ML: 'pg/mL',
    NMOL_PER_L: 'nmol/L'
}

# create a reverse mapping:
DISPLAY_TO_UNIT_MAP = {}
for key, val in UNIT_DISPLAY_MAP.items():
    DISPLAY_TO_UNIT_MAP[val] = key

MOL_WT_MAP = {
    'T': (288.42, G_PER_MOL),
    # while free T is not any different than T, this saves
    # extra work when converting (e.g. rather than making an
    # additional map of Tf --> T)
    'Tf': (288.42, G_PER_MOL),
    'Alb': (66500.0, G_PER_MOL),
    'SHBG': (1.0, G_PER_G),  # dummy value to avoid special handling of SHBG
}

COMMON_DENOMINATOR = LITER
COMMON_NUMERATOR = NANOMOL
COMMON_UNIT = COMMON_NUMERATOR + PER + COMMON_DENOMINATOR


def get_prefix_and_measure(s):
    '''
    s is a string, such as "ng", "L", "g", etc.

    This function returns a tuple giving the "base" measurement
    (e.g. "g", "L", "m") and the numeric prefix.

    As an example, if given "ng", it will return (1e-9, "g")
    if given "L", it will return (1.0, "L") since it's already the base unit
    '''

    if len(s) == 2:
        # e.g. if s="ng", then split so that
        # prefix="n" and measure="g"
        prefix, measure = s
        if prefix not in PREFIX_DICT:
            raise Exception(f'Unrecognized prefix: {prefix}')
        # using that value, get the numeric value
        # e.g. if prefix="n" then
        # prefix becomes 1e-9
        prefix = PREFIX_DICT[prefix]
    elif len(s) == 1:
        # this is the case when we have s="g".  The
        # measure is already in the "base" measurement
        # and the prefix is simply 1.0
        measure = s
        prefix = 1.0
    else:
        raise Exception(f'What is this unit specifying: {s}')
    return (prefix, measure)


def convert_unit(species, orig_unit, target_unit):
    '''
    orig_val is the VALUE of the original unit.
    For example, if given 20 nMol/Lm then orig_val = 20.  

    orig_unit would be nMol/L, except in our specialized syntax, it would be
    NMOL_PER_L which is the string "nM_L"

    target_unit is similar.  If we were converting from nMol/L to ng/dL, then
    target_unit would be NG_PER_DL, which is the string value "ng_dL"

    species is a string, so we use the correct conversion constant. 
    Needs to be one of the keys in the MOL_WT_MAP above.
    '''

    if orig_unit == target_unit:
        return 1.0

    orig_numerator_unit, orig_denominator_unit = orig_unit.split(PER)
    target_numerator_unit, target_denominator_unit = target_unit.split(PER)
    conversion_factor, conversion_unit = MOL_WT_MAP[species]
    conversion_numerator_unit, \
        conversion_denominator_unit = conversion_unit.split(PER)

    # handle numerators:
    orig_numerator_prefix, \
        orig_numerator_measure = \
        get_prefix_and_measure(orig_numerator_unit)
    target_numerator_prefix, \
        target_numerator_measure = \
        get_prefix_and_measure(target_numerator_unit)
    conversion_numerator_prefix, \
        conversion_numerator_measure \
        = get_prefix_and_measure(conversion_numerator_unit)

    # handle denominators
    orig_denominator_prefix, \
        orig_denominator_measure = \
        get_prefix_and_measure(orig_denominator_unit)
    target_denominator_prefix, \
        target_denominator_measure = \
        get_prefix_and_measure(target_denominator_unit)
    conversion_denominator_prefix, \
        conversion_denominator_measure = \
        get_prefix_and_measure(conversion_denominator_unit)

    if (orig_numerator_measure == conversion_numerator_measure) \
            and \
            (target_numerator_measure == conversion_denominator_measure):
        # e.g. converting from ng to nM and conversion is given as x g/M
        numerator_factor = (
            (orig_numerator_prefix * conversion_denominator_prefix)/(target_numerator_prefix * conversion_numerator_prefix))*(1.0/conversion_factor)

    if (orig_numerator_measure == conversion_denominator_measure) \
            and \
            (target_numerator_measure == conversion_numerator_measure):  # e.g. converting from M to g and conversion is given as x g/M
        numerator_factor = ((orig_numerator_prefix * conversion_numerator_prefix)/(
            target_numerator_prefix * conversion_denominator_prefix))*conversion_factor

    if (orig_numerator_measure == conversion_numerator_measure) \
            and \
            (target_numerator_measure == conversion_numerator_measure):  # just scaling
        numerator_factor = orig_numerator_prefix / target_numerator_prefix

    # denominator is volumetric no matter what (i.e. the base measure is "L")
    # Hence, just need to deal with the numeric "prefix" factors
    denominator_factor = orig_denominator_prefix / target_denominator_prefix

    return (numerator_factor / denominator_factor)


def get_conversion_factor(species, orig_unit, return_unit):
    '''
    This is ultimately a thin wrapper around the `convert_unit` function.
    It allows us to use, e.g. 'ng/dL' as orig_unit rather than NG_PER_DL

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


def precalculate_conversion_factors(ic_species,
                                    accepted_units_dict,
                                    common_unit):
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
    for species in ic_species:
        conversion_factor_dict[species] = {}
        for unit in accepted_units_dict[species]:
            cf = get_conversion_factor(species, unit, common_unit)
            conversion_factor_dict[species].update({unit: cf})
    return conversion_factor_dict