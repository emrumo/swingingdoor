import pdb
import numpy as np


class SwingingDoorState:
    """ The objects of this class track the swinging door algorithm state, that is: the snapshot and the slopes of the compression cone
    """

    def __init__(self):

        self.snapshot = None
        self.reset_cone()

    def reset_cone(self):
        self.fmax = lambda t: float('inf')
        self.fmin = lambda t: -float('inf')
    
    def update_cone(self,A,S,D):
        """ A: last archived point
            S: snapshot
            D: compression deviation (compDev)
        """

        ## fmax
        slope_max = (S['signal value'] + D - A['signal value'])/(S['time stamp'] - A['time stamp'])
        bias_max = A['signal value']
        fmax = lambda t, m = slope_max, n = bias_max: m * (t - A['time stamp']) + n

        ## fmin
        slope_min = (S['signal value'] - D - A['signal value'])/(S['time stamp'] - A['time stamp'])
        bias_min = A['signal value']
        fmin = lambda t, m = slope_min, n = bias_min: m * (t - A['time stamp']) + n

        ## updating cone slopes if necessary
        if fmax(S['time stamp']) < self.fmax(S['time stamp']):
            self.fmax = fmax
        
        if fmin(S['time stamp']) > self.fmin(S['time stamp']):
            self.fmin = fmin


class SwingingDoorArchiver:
    """ The objects of this class manage the swinging door memory (where the compressed samples are stored).
        Also they allow to recover the compressed signal from the memory.
    """

    def __init__(self):
        self.reset_memory()

    def reset_memory(self):
        self.memory = []

    def dump(self,point):
            self.memory.append( point )
    
    def last_archived(self):
        if self.memory:
            return self.memory[-1]
        else:
            return None

    ## functions to recover the signal from the archive
    def time_stamps(self):
        return [point['time stamp'] for point in self.memory]
    
    def signal_values(self):
        return [point['signal value'] for point in self.memory]

# Swinging door trending class
class SwingingDoor:
    """This class produces a swinging door trending compressor object

    Attributes:
        compDev: Defines the half-width of the compression deviation
        compMax: Maximum time interval without archived values
        compMin: Minimum time interval where no value is archived"""

    def __init__(self,
                compDev,
                compMax = float('inf'),
                compMin = 0):
        
        self.compDev = compDev
        self.compMax = compMax
        self.compMin = compMin

        # State 
        self.state = SwingingDoorState()
        # Archiver
        self.archiver = SwingingDoorArchiver()

    # PUBLIC
    def compression_test(self,point,b_dump=False):

        # FLAGs
        b_dump_point = False
        b_dump_snapshot = False
        b_ignore_point = False

        # FIRST BLOCK
        ## the first data point is always archived
        ## the last point (or any point) is stored if the boolean b_dump is set to True (externally)
        if self.archiver.last_archived() is None or b_dump:
            b_dump_point = True

        else:
            # SECOND BLOCK
            ## If the last archived point and the snapshot are the same the point is not
            if self.archiver.last_archived() == self.state.snapshot:
                pass
            # THIRD BLOCK
            else:
                b_dump_point,b_ignore_point = self._inspection_test(point)

                if not b_dump_point and not b_ignore_point:
                    b_dump_snapshot = self._cone_test(point)


        # FOURTH BLOCK
        ## store depending on the flags
        if b_dump_point:
            self.archiver.dump(point)

        if b_dump_snapshot:
            self.archiver.dump(self.state.snapshot)
        
        # FITH BLOCK
        ## update snapshot whether is necessary
        if not b_ignore_point:
            self.state.snapshot = point


    # PRIVAT
    def _inspection_test(self,point):

        # FLAGs
        b_dump_point = False
        b_ignore_point = False

        ## tests whether the point violates the compMax deviation
        if point['time stamp'] - self.archiver.last_archived()['time stamp'] >= self.compMax:
            b_dump_point = True
        
        ## tests whether the point violates the compMin deviation
        if point['time stamp'] - self.archiver.last_archived()['time stamp'] < self.compMin:
            b_ignore_point = True
        
        return b_dump_point,b_ignore_point
    
    def _cone_test(self,point):

        # FLAGs 
        b_dump_snapshot = False

        ## updating the cone
        self.state.update_cone(self.archiver.last_archived(),self.state.snapshot,self.compDev)

        ## checking if the data point lies inside the cone
        if point['signal value'] < self.state.fmax(point['time stamp']) and point['signal value'] > self.state.fmin(point['time stamp']):
            pass
        else:
            b_dump_snapshot = True

            ### reseting the cone
            self.state.reset_cone()
        
        return b_dump_snapshot










    