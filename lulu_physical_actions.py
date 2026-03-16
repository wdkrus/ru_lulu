from xgolib import XGO
import time

xgo=XGO("xgolite")

def lulu_go_forward(delay_time):
    xgo.move_x(20) 
    time.sleep(delay_time)
    xgo.stop()

def lulu_go_back(delay_time):
    xgo.move_x(-20) 
    time.sleep(delay_time)
    xgo.stop()

def lulu_move_left(delay_time):
    xgo.move_y(12) 
    time.sleep(delay_time)
    xgo.stop()

def lulu_move_right(delay_time):
    xgo.move_y(-12)
    time.sleep(delay_time)
    xgo.stop()

def lulu_turn_left(delay_time):
    xgo.turn(-30)
    time.sleep(delay_time)
    xgo.stop()

def lulu_turn_right(delay_time):
    xgo.turn(30)
    time.sleep(delay_time)
    xgo.stop()

def lulu_lay_down():
    xgo.action(1)
    time.sleep(3)

def lulu_stand_up():
    xgo.action(2)
    time.sleep(3)

def lulu_turn_around():
    xgo.action(4)
    time.sleep(5)

def lulu_crawl():
    xgo.action(3)
    time.sleep(5)

def lulu_squat():
    xgo.action(6)
    time.sleep(4)

def lulu_warm_up():
    xgo.action(10)
    time.sleep(7)

def lulu_pee():
    xgo.action(11)
    time.sleep(7)

def lulu_sit_down():
    xgo.action(12)
    time.sleep(5)

def lulu_wave_hand():
    xgo.action(13)
    time.sleep(7)

def lulu_stretch():
    xgo.action(14)
    time.sleep(10)

def lulu_wave_body():
    xgo.action(15)
    time.sleep(6)

def lulu_swing():
    xgo.action(16)
    time.sleep(6)

def lulu_handshake():
    xgo.action(19)
    time.sleep(10)

def lulu_dance():
    xgo.action(23)
    time.sleep(6)

def lulu_push_up():
    xgo.action(21)
    time.sleep(8)

def lulu_show_arm():
    xgo.action(20)
    time.sleep(9)

def lulu_arm_up():
    xgo.action(128)
    time.sleep(10)

def lulu_arm_middle():
    xgo.action(129)
    time.sleep(10)

def lulu_arm_down():
    xgo.action(130)
    time.sleep(10)

def lulu_climb_stairs():
    xgo.action(144)
    time.sleep(12)
