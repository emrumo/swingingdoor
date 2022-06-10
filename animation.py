import pdb
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from compressor import SwingingDoor 
from celluloid import Camera

# Modifying the SwingingDoor class to make an animation
class SwingingDoorAnimation(SwingingDoor):
    def __init__(self,
                compDev,
                plot_style='point'):
        super().__init__(compDev=compDev)

        fig, self.ax = plt.subplots(1)
        self.camera = Camera(fig)

        ## log variable
        self.log = []

        ## plot style
        self.plot_style = plot_style
    
    ## modifying the compression test to plot what is happening
    def compression_test(self, point, b_dump=False):

        ## animation
        self.log.append( {'point':point,'style':'cx'} )

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

            ## animation
            self.log.append( {'point':point,'style':'kx'} )

        if b_dump_snapshot:
            self.archiver.dump(self.state.snapshot)

            ### animation
            self.log.append( {'point':self.state.snapshot,'style':'kx'} )

        # FITH BLOCK
        ## update snapshot wheter is necessary
        if not b_ignore_point:
            self.state.snapshot = point      

    ## modifying the cone test to plot what is happening
    def _cone_test(self, point):

        # FLAGs 
        b_dump_snapshot = False

        ## updating the cone
        self.state.update_cone(self.archiver.last_archived(),self.state.snapshot,self.compDev)

        ## animation
        ### logged points
        for log in self.log:
            if self.plot_style == 'point':
                self.ax.plot(log['point']['time stamp'],log['point']['signal value'],log['style'])
            
            if self.plot_style == 'interval':
                self.ax.errorbar(log['point']['time stamp'],log['point']['signal value'],self.compDev,fmt='none',ecolor='c')

                if log['style'] == 'kx':
                    self.ax.plot(log['point']['time stamp'],log['point']['signal value'],log['style'])

        ### current point
        if self.plot_style == 'interval':
            self.ax.plot(point['time stamp'],point['signal value'],'cx')

        ### snapshot
        self.ax.plot(self.state.snapshot['time stamp'],self.state.snapshot['signal value'],'rx')

        ### compDev
        self.ax.errorbar(self.state.snapshot['time stamp'],self.state.snapshot['signal value'],self.compDev,fmt='none',ecolor='red')

        ### cone slopes
        t = np.linspace(self.archiver.last_archived()['time stamp'],point['time stamp'],100)
        upper_slope = self.ax.plot(t,self.state.fmax(t),'b')
        lower_slope = self.ax.plot(t,self.state.fmin(t),'b')

        ### plot customization
        self.ax.grid(visible=True)

        #### point style
        data_point = mlines.Line2D([], [], color='c', marker='x', linestyle='None', label='Data point')
        archived_point = mlines.Line2D([], [], color='k', marker='x', linestyle='None', label='Archived point')
        snapshot_point = mlines.Line2D([], [], color='r', marker='x', linestyle='None', label='Snapshot point')
        cone_slopes = mlines.Line2D([0], [0], color='b', label='Cone slopes')
        compression_deviation = mlines.Line2D([0], [0], color='r', marker='|', markersize=10, linestyle='None', label='compDev')

        #### interval style
        data_interval = mlines.Line2D([0], [0], color='c', marker='|', markersize=10, linestyle='None', label='Interval')
        center_interval = mlines.Line2D([], [], color='c', marker='x', linestyle='None', label='Interval center')

        #### plot configuration
        if self.plot_style == 'point':
            self.ax.legend(handles=[data_point,archived_point,snapshot_point,cone_slopes,compression_deviation])
        if self.plot_style == 'interval':
            self.ax.legend(handles=[data_interval,center_interval,archived_point,snapshot_point,cone_slopes,compression_deviation])
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Signal value')
        self.ax.set_title('Swingning door compression algorithm')

        ### camera snap
        self.camera.snap()

        ## checking if the data point lies inside the cone
        if point['signal value'] < self.state.fmax(point['time stamp']) and point['signal value'] > self.state.fmin(point['time stamp']):
            pass
        else:
            b_dump_snapshot = True

            ### reseting the cone
            self.state.reset_cone()
         
        return b_dump_snapshot      
         

# CODE
## generating synthetic data
time_stamps = np.linspace(0,2*np.pi,50)
signal_values = np.sin(time_stamps)
compDev = 0.2

### animation 1
compressor1 = SwingingDoorAnimation(compDev)

for x,y in zip(time_stamps,signal_values):
    point = {'time stamp':x,'signal value':y}

    compressor1.compression_test(point)

animation1 = compressor1.camera.animate()
animation1.save('animation1.gif')

### animation 2
compressor2 = SwingingDoorAnimation(compDev,plot_style='interval')

for x,y in zip(time_stamps,signal_values):

    #### quantization
    y = np.round(y/(2*compDev)) * 2 * compDev

    point = {'time stamp':x,'signal value':y}

    compressor2.compression_test(point)

animation2 = compressor2.camera.animate()
animation2.save('animation2.gif')

