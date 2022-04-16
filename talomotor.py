from __future__ import division
import time
import itertools
from enum import Enum
import Adafruit_PCA9685


# Initialise the PCA9685 using the default address (0x40).
pwm = Adafruit_PCA9685.PCA9685()

PMIN = 4
PMAX = 16
SERVO_SPEED = 0.35/180 # deg/s 
STROKE_ANGLE = 45
P_STROKE_ANGLE = 45
STROKE_TIME = STROKE_ANGLE * SERVO_SPEED

pwm.set_pwm_freq(60)


class Beat(Enum):
    L = 0  # Little
    R = 1  # Right
    M = 2  # Middle
    I = 3  # Index
    T = 4  # Thumb
    P = 5  # Palm
    B = 6  # Back

NADAI_MAP = {
    2: [1, 0],
    3: [1, 1, 0],
    4: [1, 0, 0, 0],
    5: [1, 0, 1, 1, 0],
    7: [1, 0, 1, 0, 1, 1, 0],
    9: [1, 0, 1, 0, 1, 0, 1, 1, 0]
}

THALAM_MAP = {
    'triputa': 'LDD',
    'eka': 'L',
    'matya': 'LDL',
    'ata': 'LLDD',
    'dhruva': 'LLLD',
    'rupaka': 'DL',
    'jumpa': 'LUD'
}

LAGHU = [Beat.P, Beat.L, Beat.R, Beat.M, Beat.I, Beat.T, Beat.L, Beat.R, Beat.M]


def play_beat(beat, nadai=4, prev_beat=None):
    is_veechu = Beat[beat] == Beat.B

    if not is_veechu:
        play_thattu(beat, nadai, prev_beat)
    else:
        play_veechu(nadai, prev_beat)


def play_veechu(nadai=4, prev_beat=None):
    strokes = NADAI_MAP[nadai]
    step_time = 180*SERVO_SPEED

    # Move both P & B simultaneously
    if prev_beat != Beat.B.name:
        stime = 180 * SERVO_SPEED
        pwm.set_pwm(Beat.P.value, 0, int(PMAX/100*4096))
        pwm.set_pwm(Beat.B.value, 0, int(PMAX/100*4096))
        time.sleep(stime)

        # Bring P down
        pwm.set_pwm(Beat.P.value, 0, int(PMIN/100*4096))
        time.sleep(stime)

    start_indx = 1 if prev_beat != Beat.B.name else 0
    for stroke in strokes[start_indx:]:
        time.sleep(step_time)
        if stroke:
            move_servo(Beat.P.value, 3*STROKE_ANGLE, stime=step_time)
    

def play_thattu(beat, nadai=4, prev_beat=None):
    channel = Beat[beat].value
    strokes = NADAI_MAP[nadai]
    step_time = 180*SERVO_SPEED

    # Move both P & B simultaneously
    if prev_beat == Beat.B.name:
        stime = 180 * SERVO_SPEED
        pwm.set_pwm(Beat.P.value, 0, int(PMAX/100*4096))
        pwm.set_pwm(Beat.B.value, 0, int(PMIN/100*4096))
        time.sleep(stime)

        # Bring P down
        pwm.set_pwm(Beat.P.value, 0, int(PMIN/100*4096))
        time.sleep(stime)

    angle = STROKE_ANGLE if Beat[beat] != Beat.P else 3*STROKE_ANGLE

    start_indx = 1 if prev_beat == Beat.B.name else 0
    for stroke in strokes[start_indx:]:
        time.sleep(step_time)
        if stroke:
            move_servo(channel, angle, stime=step_time)
  

def move_servo(channel, angle=STROKE_ANGLE, revert=True, stime=SERVO_SPEED*180):
    duty_cycle = angle/180*(PMAX-PMIN) + PMIN
    pwm.set_pwm(channel, 0, int(duty_cycle/100*4096))
    time.sleep(stime/2)
    if revert:
        pwm.set_pwm(channel, 0, int(PMIN/100*4096))    
        time.sleep(stime/2)


def get_beats(thalam, jathi, kalai=1):
    angas = THALAM_MAP.get(thalam, None)
    if not angas:
        print('Unknown thalam')
        return
    
    beats = []
    for anga in angas:
        if anga == 'L':
            anga_beats = LAGHU[:jathi]
        elif anga == 'D':
            anga_beats = [Beat.P, Beat.B]
        elif anga == 'U':
            anga_beats = [Beat.P]
        beats.extend([[beat.name]*kalai for beat in anga_beats])
    beats = list(itertools.chain(*beats))
    return beats      


def play_thalam(thalam='triputa', jathi=4, kalai=1, nadai=4, repeat=1):
    prev_beat = None
    for i in range(repeat):
        beats = get_beats(thalam, jathi, kalai)
        for b in beats:
            play_beat(b, prev_beat=prev_beat, nadai=nadai)
            prev_beat=b
        
    play_thattu('P', prev_beat=beats[-1])

def play_custom(pattern, nadai=None, repeat=1):
    prev_beat = None
    for i in range(repeat):
        if not nadai:
            beats = pattern[::2]
            nadais = pattern[1::2]
        else:
            beats = pattern
            nadais = [nadai]*len(pattern)

        for b, nadai in zip(beats, nadais):
            play_beat(b, prev_beat=prev_beat, nadai=int(nadai))
            prev_beat=b

    play_thattu('P', prev_beat=beats[-1])
    

def play_demo():
    time.sleep(5)
    print('eka, j3, n4')
    play_thalam('eka', jathi=3)
    time.sleep(3)

    print('eka, j3, n3')
    play_thalam('eka', jathi=3, nadai=3)
    time.sleep(3)

    print('eka, j3, n5')
    play_thalam('eka', jathi=3, nadai=5)
    time.sleep(3)

    print('eka, j3, n7')
    play_thalam('eka', jathi=3, nadai=7)
    time.sleep(3)

    print('eka, j3, n9')
    play_thalam('eka', jathi=3, nadai=9)
    time.sleep(3)

    print('eka, j7, n4')
    play_thalam('eka', jathi=7)
    time.sleep(3)

    print('triputa, j4, n4')
    play_thalam('triputa', jathi=4)
    time.sleep(3)

    print('ata, j3, n3')
    play_thalam('ata', jathi=5, nadai=3)
    time.sleep(3)

    print('pancha jathi')
    play_custom('P2P2L3R7M5I9')
    time.sleep(3)

    print('chanda thalam, KCKCRC')
    play_custom('P5P5P2P2B2')
    time.sleep(3)
