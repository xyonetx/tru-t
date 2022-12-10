__author__ = 'brian'

import json

import numpy as np

from .custom_exceptions import *


class Model(object):

    def __init__(self, reaction_list, required_species, all_species):
        """
        :param reaction_list: A list of src.reacion_components.Reaction
            instances

        :param required_species: A list/set of species/symbols which are
            required to be specified as initial conditions. Without those,
            the system would not be able to be solved.

        :param all_species: A list/set giving the entire set of 
            species/symbols that in the system. 
        """
        self._reactions = reaction_list
        self._required_initial_conditions = set(required_species)
        self._all_species = set(all_species)
        self._create_species_mapping()

    def get_all_species(self):
        """
        Returns all the species in the model

        :return: A set of strings which give the species' symbols
        """
        return self._all_species

    def get_reactions(self):
        """
        Returns all the reactions in this Model instance

        :return: A list of Reaction instances
        """
        return self._reactions

    def get_required_initial_conditions(self):
        """
        Return the set of species which are required to form a reaction (e.g.
        if any of these are missing, then the reaction does not make
        sense or proceed).
        """
        return self._required_initial_conditions

    def _create_species_mapping(self):
        """
        Creates a dictionary that maps the species (symbols) to an integer
        index.  That index is used to locate the species in the matrix algebra.

        At the end of the calculations, we will typically have an array of
        floats, and the dictionary this creates is necessary to map the
        time evolutions to a particular species

        :return: None
        """
        sorted_species = sorted(list(self._all_species))
        self._species_mapping = dict(
            zip(sorted_species, range(len(sorted_species))))

    def get_species_mapping(self):
        return self._species_mapping

    def check_initial_conditions(self, symbols):
        """
        Given a list of symbols corresponding to the provided initial
        conditions, ensures that they are in compliance for the model.

        This function is silent if everything is fine. Otherwise, it 
        raises an exception.

        :param symbols: A list of strings giving the symbol/species
            which we are asserting are valid

        :return: None
        """
        # first need to check that the initial conditions are a subset
        # of the full set of species. Extra (unexpected) species are
        # not accepted
        ic_set = set(symbols)
        diff_set_1 = ic_set.difference(self._all_species)
        if len(diff_set_1) > 0:
            raise InitialConditionGivenForMissingElement(
                f'Symbol(s) {",".join(diff_set_1)} were'
                ' not in your equations.')

        # Also must ensure the provided initial conditions are a superset of
        # the set of required initial conditions. We need at least those
        # bare minimum initial conditions; extra ones are fine.
        diff_set_2 = self._required_initial_conditions.difference(ic_set)
        if len(diff_set_2) > 0:
            raise MissingRequiredInitialConditionsException(
                'You need to specify initial conditions for all'
                f' required species. Was missing: {",".join(diff_set_2)}.\n'
                f' Required: {self._required_initial_conditions}')

    def setup_initial_conditions(self, X0):
        """
        Creates and returns a numPy array which contains
        the initial conditions.  
        
        Note that the positions in the array are determined
        via the species-to-index map that was created in
        the _create_species_mapping method.

        This method does not check the validity of the initial
        conditions for the model. That should be done before
        everything else by using the `check_initial_conditions`
        method of this class

        :param X0: A dictionary maping the symbols to the
            initial condition values.

        :return: None
        """
        initial_conditions = np.zeros(len(self._species_mapping))
        for symbol, index in self._species_mapping.items():
            # species_mapping maps the symbol to the index of
            # the concentration array
            try:
                c = X0[symbol]
                if c < 0.0:
                    raise InvalidInitialConditionException('A negative'
                        f'concentration was specified for {symbol}: {c}')
                initial_conditions[index] = X0[symbol]
            except KeyError:
                pass
        return initial_conditions

    def __str__(self):
        """
        The string representation of the Model class

        :return: a string
        """
        s = ''
        for rx in self._reactions:
            s += f'{rx}\n'
        return s

    def to_json(self):
        """
        Creates a JSON-representation of the model

        :return: a JSON-formatted string
        """
        d = {}
        reaction_list = []
        for rx in self._reactions:
            rx_str, fwd_k, rev_k = rx.as_string().split(',')
            reaction_dict = {
                'reaction_expression': rx_str,
                'fwd_k': fwd_k,
                'rev_k': rev_k,
            }
            reaction_list.append(reaction_dict)
        d['reactions'] = reaction_list
        d['required_initial_conditions'] = list(self._required_initial_conditions)
        return json.dumps(d)
