#!/usr/bin/python2
# -*- coding: utf-8 -*-

MAX_THROTTLE = 85
NO_THROTTLE = 90
MIN_THROTTLE = 95

MAX_STEERING = 120
MID_STEERING = 90
MIN_STEERING = 60

DEAD_ZONE = 5

import pygame
from socket import socket

pygame.init()

window = pygame.display.set_mode((320, 240))
pygame.display.set_caption("ORC")


class Buffer(object):
    DEFAULT_COUNTER = 10

    def __init__(self, sock):
        self.last = ""
        self.sock = sock
        self.counter = self.DEFAULT_COUNTER

    def send(self, data):
        self.counter -= 1
        if self.counter <= 0 or self.last != data:
            self.sock.send(data)
            self.last = data
            self.counter = self.DEFAULT_COUNTER


class Prog(object):
    def __init__(self):
        self.sock = None
        self.keys = [False] * 4
        self.axis = [0] * 3
        self.throttle = NO_THROTTLE
        self.steering = MID_STEERING
        self.buff = None
        self.joystickMode = True

    def handleEventKeyboard(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.keys[0] = True
                elif event.key == pygame.K_DOWN:
                    self.keys[1] = True
                elif event.key == pygame.K_LEFT:
                    self.keys[2] = True
                elif event.key == pygame.K_RIGHT:
                    self.keys[3] = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.keys[0] = False
                elif event.key == pygame.K_DOWN:
                    self.keys[1] = False
                elif event.key == pygame.K_LEFT:
                    self.keys[2] = False
                elif event.key == pygame.K_RIGHT:
                    self.keys[3] = False        
        if self.keys[0] == self.keys[1]:
            self.throttle = NO_THROTTLE
        elif self.keys[0]:
            self.throttle = MAX_THROTTLE
        elif self.keys[1]:
            self.throttle = MIN_THROTTLE
        if self.keys[2] == self.keys[3]:
            self.steering = MID_STEERING
        elif self.keys[2]:
            self.steering = MAX_STEERING
        elif self.keys[3]:
            self.steering = MIN_STEERING
        return True

    def handleEventJoy(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.JOYAXISMOTION:
                if event.axis == 0:
                    self.axis[0] = event.value
                elif event.axis == 2:
                    self.axis[1] = event.value
                elif event.axis == 5:
                    self.axis[2] = event.value
        if abs(self.axis[0]) < .15:
            self.axis[0] = 0
        if self.axis[0] > 0:
            self.steering = MID_STEERING - int((MID_STEERING - MIN_STEERING) * self.axis[0])
        else:
            self.steering = MID_STEERING + int((MAX_STEERING - MID_STEERING) * -(self.axis[0]))
        tmp = self.axis[1] - self.axis[2]
        if tmp > 0:
            self.throttle = NO_THROTTLE - int((NO_THROTTLE - MIN_THROTTLE) * tmp)
        else:
            self.throttle = NO_THROTTLE + int((MAX_THROTTLE - NO_THROTTLE) * -(tmp))
        return True

    def handleEvent(self):
        if self.joystickMode:
            return self.handleEventJoy()
        return self.handleEventKeyboard()

    def eventLoop(self):
        clock = pygame.time.Clock()
        while True:
            if not self.handleEvent():
                return False
            self.buff.send("T%d\nS%d\n" % (self.throttle, self.steering))
            clock.tick(30)
        return True
        

    def main(self):
        ret = True
        if self.joystickMode:
            for x in range(pygame.joystick.get_count()):
                joy = pygame.joystick.Joystick(x)
                print joy
                joy.init()
        while ret:
            self.sock = socket()
            print "Trying to connect"
            self.sock.connect(("192.168.0.100", 4242))
            print "Connected"
            self.buff = Buffer(self.sock)
            ret = self.eventLoop()
            self.sock.close()


if __name__ == "__main__":
    prog = Prog()
    prog.main()
