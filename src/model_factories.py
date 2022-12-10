import json

from .custom_exceptions import JsonParseException, \
    MalformattedReactionFileException, \
    RequiredSpeciesException, \
    RateConstantFormatException, \
    InconsistentDirectionalityException, \
    MissingRateConstantException
from . import parsers
from .reaction_components import Reaction
from .models import Model

from functools import reduce


class ModelFactory(object):
    """
    A base class to derive from.  Derived children of ModelFactory
    should provide a mechanism to ingest information
    and create Model instances to populate a Model.
    """

    def get_model(self):
        return Model(self._reaction_list,
                     self._required_species_set,
                     self._all_species_set)


class JsonModelFactory(ModelFactory):

    def __init__(self, model_file):
        """
        :param model_file: Path to a JSON-format file defining the full model
        """
        try:
            with open(model_file) as fin:
                j = json.load(fin)
        except Exception as ex:
            raise JsonParseException(
                'Could not parse the JSON-format model definition.'
                f' File was {model_file}')

        self._expression_parser = parsers.StringExpressionParser
        self._handle_equations(j)
        self._determine_all_species()
        self._handle_required_initial_conditions(j)

    def _handle_rate_constant(self,
                              reaction_dict,
                              key,
                              is_bidirectional,
                              required=False):
        try:
            c = reaction_dict[key]
            c = float(c)
            if c < 0:
                raise RateConstantFormatException('Rate constants'
                            f' must be positive. Found {key}={c}')
        except KeyError as ex:
            if required:
                raise MissingRateConstantException(f'The "{key}" is required.')

            if is_bidirectional:
                raise MissingRateConstantException('The equation was specified'
                        ' as bidirectional (<-->) but no reverse rate constant'
                        ' was provided.')
            c = 0.0
        except ValueError:
            raise RateConstantFormatException('Could not parse'
                f' the reverse rate constant {c} as a number.')
        return c

    def _handle_equations(self, j):
        # rather than create an entirely new parser,
        # take the objects in the 'reactions' key and make strings
        # that match those required by the original model definition file:
        try:
            reactions = j['reactions']
        except KeyError as ex:
            raise JsonParseException(
                'Your JSON model needs to have a "reactions" key')

        if not type(reactions) is list:
            raise JsonParseException('The "reactions" key should address'
                                     ' a list')

        reaction_list = []
        for reaction_dict in reactions:
            try:
                reaction_expression = reaction_dict['reaction_expression']
            except KeyError as ex:
                raise JsonParseException(
                    'Your JSON model needs to have a'
                    ' "reaction_expression" key')

            reactants, products, is_bidirectional = \
                self._expression_parser.parse(reaction_expression)

            fwd_k = self._handle_rate_constant(reaction_dict,
                                               'fwd_k',
                                               is_bidirectional,
                                               required=True)

            rev_k = self._handle_rate_constant(reaction_dict,
                                               'rev_k',
                                               is_bidirectional,
                                               required=False)

            if not is_bidirectional and rev_k > 0:
                raise InconsistentDirectionalityException('The equation'
                                                          f' {reaction_expression} was unidirectional, but a'
                                                          f' reverse rate constant {rev_k} was specified.')

            reaction_list.append(
                Reaction(
                    reactants, products, fwd_k, rev_k, is_bidirectional
                )
            )

        if len(reactions) == 0:
            raise MalformattedReactionFileException(
                'Could not parse any reactions from the input file.')
        self._reaction_list = reaction_list

    def _determine_all_species(self):
        self._all_species_set = reduce(lambda x, y: x.union(
            y), [rx.get_all_species() for rx in self._reaction_list])

    def _handle_required_initial_conditions(self, j):
        try:
            required_species_set = set(j['required_initial_conditions'])
        except KeyError as ex:
            raise JsonParseException(
                'Your JSON model needs to specify a list of required'
                f' initial conditions via the {ex} key')

        # now check that those species are represented
        # in the original reactions
        diff_set = required_species_set.difference(self._all_species_set)
        if len(diff_set) > 0:
            raise RequiredSpeciesException(
                'You specified a required initial condition(s)'
                f' not found in the set of reactions. {",".join(diff_set)}')
        self._required_species_set = required_species_set
