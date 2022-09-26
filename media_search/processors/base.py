class Processor():
    def process(input):
        raise NotImplementedError

class BadFormatError(Exception):
    """
    To be raised if data format is not as expected for given Processor
    """
    pass
