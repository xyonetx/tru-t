__author__ = 'brian'

import re

from .custom_exceptions import MalformattedReactionDirectionSymbolException, \
    InvalidSymbolName, \
    MalformattedReactionException, \
    MissingRateConstantException, \
    RateConstantFormatException, \
    ExtraRateConstantException
from .reaction_components import Reactant, Product


class ExpressionParser(object):
    """
    A base class to derive from.  Derived children of this
    class ideally implement methods to parse individual
    reaction 'sources'
    """
    @classmethod
    def parse(cls, item):
        raise NotImplementedError


class StringExpressionParser(ExpressionParser):
    """
    An implementation of ExpressionParser for reading strings and forming
    """
    # some compiled regular expressions for parsing
    # through reactions specified by strings
    direction_symbol_regex = re.compile('<?[-]+>')
    equation_regex = re.compile('[a-zA-Z0-9\+\s\*]+')
    symbol_regex = re.compile('[a-zA-Z][a-zA-Z0-9]*')

    BIDIRECTIONAL = 'bidirectional'
    FWD = 'fwd'
    REV = 'rev'

    @classmethod
    def _is_bidirectional(cls, s):
        """
        Determines the 'direction' of a reaction based on the
        symbol between the reactants and products.

        :param s: a string which is formatted according to our conventions

        :return: True or False
        """
        # parse out the directional symbol
        m = re.search(cls.direction_symbol_regex, s)
        if m:
            symbol = m.group(0)
            if (symbol[0] == '<') and (symbol[-1] == '>'):
                return True
            return False
        else:
            raise MalformattedReactionDirectionSymbolException(
                f'Check the directional symbol. Given as {s}. Note'
                f' that single direction relations should be written'
                f' as, e.g. A + B -> C instead of C <- A + B')

    @classmethod
    def check_symbol_name(cls, symbol):
        """
        Checks that a species symbol follows our formatting rules

        :param symbol: a string

        :return: None
        """
        m = re.match(cls.symbol_regex, symbol)
        if m is None or symbol != m.group():
            raise InvalidSymbolName(f'Symbol {symbol} is not a'
                                    ' valid symbol name.')

    @classmethod
    def _parse_components(cls, s, element_class):
        """
        Parses a string representing one half of a reaction (e.g. the
        reactants on the left side) and returns a list of species.

        :param s: a string

        :return: a list of reaction_components.ReactionElement instances
        """
        element_dict = {}
        components = [x.strip() for x in s.split('+')]
        for c in components:
            coefficient = 1
            symbol = ''
            v = c.split('*')
            if len(v) == 1:
                symbol = v[0]
                cls.check_symbol_name(symbol)
            elif len(v) == 2:
                try:
                    coefficient = int(v[0])
                    symbol = v[1]
                    cls.check_symbol_name(symbol)
                except ValueError:
                    raise MalformattedReactionException(
                        f'Equation component {c} is not formatted correctly.')
            else:
                raise MalformattedReactionException(
                    f'Equation component {c} is not formatted correctly.')
            if symbol in element_dict:
                element_dict[symbol] += coefficient
            else:
                element_dict[symbol] = coefficient
        elements = []
        for symbol, coef in element_dict.items():
            elements.append(element_class(symbol, coef))
        return elements

    @classmethod
    def _parse_reaction(cls, reaction):
        """
        Parses the two sides (reactants and products) of a reaction string

        :param reaction: a string representation of a reaction in our syntax

        :return: a tuple of list objects.  The first entry is a list of
            Reactant instances and the second is a list of Product instances
        """
        try:
            lhs, rhs = [x.strip() for x in re.split(
                cls.direction_symbol_regex, reaction)]
            lhs_match = re.match(cls.equation_regex, lhs)
            rhs_match = re.match(cls.equation_regex, rhs)
            if lhs_match and rhs_match:
                if lhs_match.group() != lhs:
                    raise MalformattedReactionException(
                        f'Left-hand side of equation ({reaction})'
                        ' was not formatted correctly')
                if rhs_match.group() != rhs:
                    raise MalformattedReactionException(
                        f'Right-hand side of equation ({reaction})'
                        ' was not formatted correctly')
                # at this point we have valid lhs and rhs in terms of
                # character content.  Still need to
                # ensure that the equation makes sense.
                reactants = cls._parse_components(lhs, Reactant)
                products = cls._parse_components(rhs, Product)
                return reactants, products

            else:
                raise MalformattedReactionException(
                        f'Equation ({reaction}) was not formatted correctly')
        except ValueError:
            raise MalformattedReactionException("""
                        Could not parse a left and right-hand side.
                        Check the directional symbol.
                        Equation was %s""" % reaction)

    @classmethod
    def parse(cls, reaction_str):
        """
        This function parses a reaction given in our defined syntax.

        :param expression_str: a formatted string which gives the reaction

        :return: a 3-ple giving 
            1) a list of Reactant instances,
            2) a list of Product instances,
            3) a boolean indicating whether the reaction occurs
               in both directions.
        """
        # strip any whitespace on the outside
        reaction_str = reaction_str.strip()

        # if the line was empty, just return a list of None's.
        if len(reaction_str) == 0:
            return [None]*3

        is_bidirectional = cls._is_bidirectional(reaction_str)

        # now parse the actual reaction string
        reactants, products = cls._parse_reaction(reaction_str)

        return reactants, products, is_bidirectional
