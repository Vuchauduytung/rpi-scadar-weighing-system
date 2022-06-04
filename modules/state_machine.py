from enum import Enum
import signal


class STATE(Enum):
    S0 = 0
    S1 = 1
    S2 = 2
    S3 = 3
    S4 = 4
    S5 = 5
    S6 = 6
    S7 = 7
    S8 = 8
    S9 = 9
    DEFAULT = 10

def timer_ISR(signum, frame):
    global timeout
    timeout = True

signal.signal(signal.SIGALRM, timer_ISR)

def start_timer(time: float):
    signal.setitimer(signal.ITIMER_REAL, time, 0)

def stop_timer():
    start_timer(0)
    

def next_state(state, ss1, ss2, delta_w, QR):
    global timeout
    n_state = state
    if state == STATE.S0:
        if ss1:
            n_state = STATE.S1
        elif ss2:
            n_state = STATE.S2
    elif state == STATE.S1:
        if not ss1:
            n_state = STATE.S0
        elif ss2:
            n_state = STATE.S3
    elif state == STATE.S2:
        if ss1:
            n_state = STATE.S3
        elif not ss2:
            n_state = STATE.S0
    elif state == STATE.S3:
        if not ss1:
            n_state = STATE.S2
        elif not ss2:
            n_state = STATE.S1
        elif QR:
            n_state = STATE.S4
    elif state == STATE.S4:
        if not ss1:
            n_state = STATE.S7
        elif not ss2:
            n_state = STATE.S8
        elif delta_w <= 10:
            start_timer(5)
            n_state = STATE.S5
    elif state == STATE.S5:
        if timeout:
            timeout = False
            n_state = STATE.S6
        elif not ss1:
            stop_timer()
            n_state = STATE.S7
        elif not ss2:
            stop_timer()
            n_state = STATE.S8
        elif delta_w >  10:
            stop_timer()
            n_state = STATE.S4
    elif state == STATE.S6:
        if timeout:
            timeout = False
            n_state = STATE.S0
        elif not ss1:
            n_state = STATE.DEFAULT
        elif not ss2:
            n_state = STATE.DEFAULT
    elif state == STATE.S7:
        if ss1:
            n_state = STATE.S9
        elif not ss2:
            n_state = STATE.S4
    elif state == STATE.S8:
        if not ss1:
            n_state = STATE.S9
        elif ss2:
            n_state = STATE.S4
    elif state == STATE.S9:
        if timeout:
            timeout = False
            n_state = STATE.S0
    else:
        if timeout:
            n_state = STATE.S0
        else:
            n_state = STATE.DEFAULT
    return n_state

