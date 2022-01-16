class Alignment:
    LEFT = 'left'
    RIGHT = 'right'
    CENTER = 'center'
    TOP = 'top'
    BOTTOM = 'bottom'

    def __init__(self, *aligns):
        self.aligns = list(set(list(aligns) + [Alignment.CENTER]))
        if Alignment.TOP in self.aligns and Alignment.BOTTOM in self.aligns:
            raise OppositeAlignmentError('Align.TOP and Align.BOTTOM can`t \
be used together')
        if Alignment.LEFT in self.aligns and Alignment.RIGHT in self.aligns:
            raise OppositeAlignmentError('Align.LEFT and Align.RIGHT can`t \
be used together')
        if (Alignment.TOP in self.aligns or Alignment.BOTTOM in self.aligns)\
                and (Alignment.LEFT in self.aligns or
                             Alignment.RIGHT in self.aligns) and\
                        Alignment.CENTER in self.aligns:
            self.aligns.remove(Alignment.CENTER)

    def __and__(self, align):
        if isinstance(align, Alignment):
            return Alignment(*align.aligns + self.aligns)
        else:
            raise NotAlignmentError('Argument is not an Align object')

    def __eq__(self, align):
        if isinstance(align, Alignment):
            return all([al in self.aligns
                        for al in align.aligns if al != Alignment.CENTER])
        else:
            raise NotAlignmentError('Argument is not an Align object')

    def __ne__(self, align):
        return not self == align


class Align:
    LEFT = Alignment(Alignment.LEFT)
    RIGHT = Alignment(Alignment.RIGHT)
    CENTER = Alignment(Alignment.CENTER)
    TOP = Alignment(Alignment.TOP)
    BOTTOM = Alignment(Alignment.BOTTOM)


class AlignmentError(Exception):
    pass


class OppositeAlignmentError(AlignmentError):
    pass


class NotAlignmentError(AlignmentError):
    pass


class ElementFunctionAtCycle(Exception):
    pass
