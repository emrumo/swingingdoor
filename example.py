import pdb
import numpy as np
import matplotlib.pyplot as plt
from compressor import SwingingDoor as sd

# Generating synthetic data
time_stamps = np.linspace(0,2*np.pi,100)
signal_values = np.sin(time_stamps)

## Higher resolution
fine_time_stamps = np.linspace(0,2*np.pi,1000)
fine_signal_values = np.sin(fine_time_stamps)

# Synthetic data
plt.plot(time_stamps,signal_values,'cx',label='Original samples')
plt.plot(fine_time_stamps,fine_signal_values,'c',label='Original signal')

compDev = 0.05
compressor = sd(compDev)

for x,y in zip(time_stamps,signal_values):
    point = {'time stamp':x,'signal value':y}

    if x == time_stamps[-1]:
        compressor.compression_test(point,b_dump=True)
    else:
        compressor.compression_test(point)

compressed_time_stamps = np.array( compressor.archiver.time_stamps() )
compressed_signal_values = np.array( compressor.archiver.signal_values() )

## compression rate
crate = len(time_stamps)/len(compressed_time_stamps)
print('Compression rate:',f'x{crate} times')

## plots
plt.plot(compressed_time_stamps,compressed_signal_values,'kx',label='Compressed samples')
plt.plot(compressed_time_stamps,compressed_signal_values,'k',label='Compressed signal')
plt.fill_between(compressed_time_stamps,
                compressed_signal_values-compDev,
                compressed_signal_values+compDev,
                alpha=0.2,
                color='r',
                label='compDev')
plt.xlabel('Time')
plt.ylabel('Signal value')
plt.legend()
plt.grid()
plt.show()      