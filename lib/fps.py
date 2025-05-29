# FPS provides an easy way to count frames per second with some smoothing, by taking
# a running average over the last N frames (approximated to ensure efficiency even with large N).
# It does not include functionality to display the frame counter, but this can be done very easily
# via the `textmode` lib. FPS also provides general timer functionality.
# 
# from fps import FPS
# fps_ctr = FPS(N)
# fps_ctr.tick()           # call once per frame
# cur_fps = fps_ctr.fps()  # floating-point value
# n_ticks = fps.frame()    # frame counter
#
# t = fps_ctr.time()       # seconds since object creation (floating-point)
# t_ms = fps_ctr.time_ms() # in milliseconds (integer)
# t = fps_ctr.frame_time() # time since start of current frame (also as .frame_time_ms())
# fps_ctr.tock()           # reset user timer
# t = fps_ctr.tock_time()  # time since last .tock() (also as .tock_time_ms())


import time

class FPS:
    def __init__(self, N=20):
        self.N = N
        self.prior_ms_per_frame = 100.0
        self.ms_per_frame_accum = 0
        self.idx = 0
        self.ticks = 0
        self.t0 = time.ticks_ms()
        self.t_frame = self.t0
        self.t_tock = self.t0

    # call fps.tick() once per frame to record number of ms since last frame
    def tick(self):
        t1 = time.ticks_ms()
        dt = time.ticks_diff(t1, self.t_frame)
        if self.idx >= self.N:
            self.prior_ms_per_frame = float(self.ms_per_frame_accum) / self.N
            self.ms_per_frame_accum = 0
            self.idx = 0
        self.ms_per_frame_accum += dt
        self.idx += 1
        self.ticks += 1
        self.t_frame = t1

    # compute running average fps (floating-point)
    def fps(self) -> float:
        total_ms = self.ms_per_frame_accum + (self.N - self.idx) * self.prior_ms_per_frame
        return self.N * 1000.0 / total_ms
    
    # frame counter
    def frame(self) -> int:
        return self.ticks
        
    # total timer (from object creation to start of current frame)
    def time_ms(self) -> int:
        return time.ticks_diff(self.t_frame, self.t0)
    
    def time(self) -> float:
        return time.ticks_diff(self.t_frame, self.t0) / 1000.0
    
    # frame timer (from start of current frame to method call)
    def frame_time_ms(self) -> int:
        t1 = time.ticks_ms()
        return time.ticks_diff(t1, self.t_frame)
    
    def frame_time(self) -> float:
        return self.frame_time_ms() / 1000.0

    # use timer (from last .tock() to start of current frame)
    def tock(self):
        self.t_tock = self.t_frame
    
    def tock_time_ms(self) -> int:
        return time.ticks_diff(self.t_frame, self.t_tock)
    
    def tock_time(self) -> float:
        return time.ticks_diff(self.t_frame, self.t_tock) / 1000.0
