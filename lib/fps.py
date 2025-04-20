# FPS provides an easy way to count frames per second with some smoothing, by taking
# a running average over the last N frames. It does not include functionality to display
# the frame counter, but this can be done very easily via the `textmode` lib.
# 
# from fps import FPS
# fps_ctr = FPS(N)
# fps_ctr.tick() # call once per frame
# cur_fps = fps_ctr.fps() # floating-point value

import time

class FPS:
    def __init__(self, N=20):
        self.N = N
        self.ms_per_frame = [100, ] * N
        self.idx = 0
        self.t0 = time.ticks_ms()
    

    # call fps.tick() once per frame to record number of ms since last frame
    def tick(self):
        t1 = time.ticks_ms()
        dt = time.ticks_diff(t1, self.t0)
        self.t0 = t1
        if self.idx >= self.N:
            self.idx = 0
        self.ms_per_frame[self.idx] = dt
        self.idx += 1
    
    # compute running average fps (floating-point)
    def fps(self) -> float:
        return self.N * 1000 / sum(self.ms_per_frame)
    