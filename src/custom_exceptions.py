__author__ = 'brian'


class FileSourceNotFound(Exception):
    pass


class NoReactionParser(Exception):
    pass


class MissingRateConstantException(Exception):
    pass


class RateConstantFormatException(Exception):
    pass


class ExtraRateConstantException(Exception):
    pass


class MalformattedReactionDirectionSymbolException(Exception):
    pass


class MalformattedReactionException(Exception):
    pass


class InconsistentDirectionalityException(Exception):
    pass


class InvalidSymbolName(Exception):
    pass


class MalformattedReactionFileException(Exception):
    pass


class MissingInitialConditionsException(Exception):
    pass


class MissingRequiredInitialConditionsException(Exception):
    pass


class InvalidSimulationTimeException(Exception):
    pass


class InitialConditionGivenForMissingElement(Exception):
    pass


class InvalidInitialConditionException(Exception):
    pass


class RequiredSpeciesException(Exception):
    pass


class JsonParseException(Exception):
    pass


class ReactionErrorWithTrackerException(Exception):

    def __init__(self, error_index, detailed_message):
        self.error_index = error_index
        self.detailed_message = detailed_message
