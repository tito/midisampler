#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Midi Sampler
============
"""

import io
import os
import json
import rtmidi
import threading
import traceback
from time import time, sleep
from rtmidi.midiconstants import (ALL_SOUND_OFF, CONTROL_CHANGE,
                                  RESET_ALL_CONTROLLERS, NOTE_ON,
                                  NOTE_OFF, SONG_START,
                                  SONG_CONTINUE, SONG_STOP)
from sdl2 import *
from sdl2.ext import Resources
from sdl2.ext.compat import byteify
from sdl2.sdlmixer import *

RESOURCES = Resources(__file__, "assets")


class Sampler(object):

    def __init__(self):
        self.midiin = rtmidi.MidiIn()
        self.initaudio()
        self.search()
        self.loop()

    def loop(self):
        while True:
            sleep(1)

    def initaudio(self):
        if SDL_Init(SDL_INIT_AUDIO) != 0:
            raise RuntimeError("Cannot initialize audio system: {}".format(SDL_GetError()))

        if Mix_OpenAudio(44100, MIX_DEFAULT_FORMAT, 2, 1024):
            raise RuntimeError("Cannot open mixed audio: {}".format(Mix_GetError()))

        self.sounds = {}
        for index in range(36, 101):
            try:
                sound_file = RESOURCES.get_path("{}.wav".format(index))
            except KeyError:
                continue
            sample = Mix_LoadWAV(byteify(sound_file, "utf-8"))
            if sample is None:
                raise RuntimeError("Cannot open audio file: {}".format(Mix_GetError()))
            self.sounds[index] = sample
            print("Loaded {}".format(sound_file))

        # channel = Mix_PlayChannel(-1, sample, 0)
        # if channel == -1:
        #     raise RuntimeError("Cannot play sample: {}".format(Mix_GetError()))
        #
        # while Mix_Playing(channel):
        #     SDL_Delay(100)
        #
        # Mix_CloseAudio()
        # SDL_Quit(SDL_INIT_AUDIO)


    def search(self):
        port = None

        while True:

            for index, name in enumerate(self.midiin.get_ports()):
                if "Through" in name:
                    continue
                port = index
                break

            if port is not None:
                break

            sleep(1)
            continue

        self.midiin.open_port(port)
        midiin_name = self.midiin.get_port_name(port)
        self.midiin.set_callback(self.midiin_callback)
        print("Connected: in={}".format(midiin_name))

    def midiin_callback(self, blob, data):
        print("MIDI IN: {}".format(blob))
        message, deltatime = blob

        action = message[0] & 0xF0
        if not (action == NOTE_ON or action == NOTE_OFF):
            return

        note, velocity = message[1:]
        if action == NOTE_ON:
            self.play(note, velocity)
        else:
            self.stop(note, velocity)

    def play(self, note, velocity):
        if note in self.sounds:
            sample = self.sounds[note]
            print("Play {}".format(sample))
            Mix_VolumeChunk(sample, max(64, velocity))
            Mix_PlayChannel(-1, sample, 0)

    def stop(self, note, velocity):
        pass


if __name__ == "__main__":
    Sampler()
