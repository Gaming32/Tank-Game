# NOTE: This file is the location for music assets, instead of asstes.py
# This decision was made in order to reduce clutter in assets.py


import logging
import random
import os

import pygame.mixer

from tank_game import global_vars, config


have_music = config.ENABLE_MUSIC

if global_vars.use_sound:
    logging.info('Loading music...')
    try:

        songs = [
            ('music/Dream_Sweet_in_Sea_Major.ogg', 0.25),
            ('music/The_undergrounds_1.ogg', 0.25),
        ]

        toremove = []
        for (song, volume) in songs:
            if not os.path.exists(song):
                logging.warning(f'Music file "{song}" does not exist, removing from playlist')
                toremove.append((song, volume))
            else:
                try:
                    pygame.mixer.music.load(song)
                except Exception:
                    logging.warning(f'Music file "{song}" unable to be loaded, removing from playlist', exc_info=True)
                    toremove.append((song, volume))
        for rem in toremove:
            songs.remove(rem)

        if not songs:
            logging.warning('All songs failed to load! Disabled music for game')
            have_music = False

        def play_random_song():
            song, volume = random.choice(songs)
            logging.debug(f'Playing song "{song}" at volume {volume}...')
            pygame.mixer.music.load(song)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(fade_ms=500)

        def stop_music():
            pygame.mixer.music.fadeout(500)
            logging.debug('Stopped music')

    except Exception:
        have_music = False
        logging.warning('Error while loading music', exc_info=True)
else:
    have_music = False


if have_music:
    logging.info('Music loaded!')
else:
    logging.warning('Music was unable to be loaded, generating stub functions')

    def play_random_song():
        pass

    def stop_music():
        pass
