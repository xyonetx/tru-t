__author__ = 'brianlawney'

from .custom_exceptions import InconsistentDirectionalityException

class Reaction(object):
    """
    This class holds all the components of a reaction-
    the constitutive species, rate constants, the direction of reaction
    """
    def __init__(self,
                 reactants,
                 products,
                 fwd_k,
                 rev_k=None,
                 is_bidirectional=False):
        """

        :param reactants: A list of Reactant instances

        :param products:
        :param fwd_k:
        :param rev_k:
        :param is_bidirectional:
        :return:
        """

        self._reactant_list = reactants
        self._product_list = products
        self._fwd_k = fwd_k
        self._rev_k = rev_k
        self.is_bidirectional = is_bidirectional

    def get_reactants(self):
        return self._reactant_list

    def get_products(self):
        return self._product_list

    def get_fwd_k(self):
        return self._fwd_k

    def get_rev_k(self):
        return self._rev_k

    def is_bidirectional_reaction(self):
        return self.is_bidirectional

    def get_all_species(self):
        """
        A set of the symbols (Strings)
        :return:
        """
        species_set = set()
        for r in self._reactant_list:
            species_set.add(r.symbol)
        for r in self._product_list:
            species_set.add(r.symbol)
        return species_set

    def reactant_str(self):
        return '+'.join([f' {x} ' for x in self._reactant_list])

    def product_str(self):
        return '+'.join([f' {x} ' for x in self._product_list])

    def as_string(self):
        reactant_str = '+'.join([f' {x} ' for x in self._reactant_list])
        product_str = '+'.join([f' {x} ' for x in self._product_list])
        direction = '<-->' if self.is_bidirectional else '-->'
        s = reactant_str + direction + product_str
        s += f',{self._fwd_k}'
        if self._rev_k is not None:
            s += f',{self._rev_k}'
        else:
            s += ',0'
        return s

    def __str__(self):
        reactant_str = '+'.join([f' {x} ' for x in self._reactant_list])
        product_str = '+'.join([f' {x} ' for x in self._product_list])
        if self._rev_k is not None:
            return (f'{reactant_str} <--{self._rev_k},'
                    f' {self._fwd_k}--> {product_str}')
        else:
            return f'{reactant_str} --{self._fwd_k}--> {product_str}'


class ReactionElement(object):
    def __init__(self,
                 symbol,
                 coefficient,
                 verbose_name=''):
        self.symbol = symbol
        self.coefficient = coefficient
        self.verbose_name = verbose_name

    def __str__(self):
        s = ''
        if self.coefficient > 1:
            s = f'{self.coefficient}*'
        s += self.symbol
        return s

    def __eq__(self, other):
        return (self.symbol == other.symbol) & \
               (self.coefficient == other.coefficient)


class Reactant(ReactionElement):
    pass


class Product(ReactionElement):
    pass
