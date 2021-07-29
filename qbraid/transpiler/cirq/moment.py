from ..moment import MomentWrapper
from .instruction import CirqInstructionWrapper

from cirq.ops import Moment as CirqMoment

class CirqMomentWrapper(MomentWrapper):

    def __init__(self, moment: CirqMoment, instructions = None):
        
        if not instructions:
            self._instructions = [CirqInstructionWrapper(i) for i in \
                moment.instructions]
        else:
            self._instructions = instructions
        self.moment = moment


    @property
    def instructions(self):
        return self._instructions