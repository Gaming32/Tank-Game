from __future__ import annotations
import datetime
import urllib.parse
from tank_game.promise import PromisingThread
from typing import Union
import logging

import dateparser
import requests


END_NEWSCORE_SCORE = 'http://dreamlo.com/lb/%s/add/%s/%i'
END_NEWSCORE_SCORE_TIME = 'http://dreamlo.com/lb/%s/add/%s/%i/%i'
END_NEWSCORE_SCORE_TIME_MESSAGE = 'http://dreamlo.com/lb/%s/add/%s/%i/%i/%s'
END_DELSCORE = 'http://dreamlo.com/lb/%s/delete/%s'
END_GETSCORES_JSON = 'http://dreamlo.com/lb/%s/json'


class Score:
    name: str
    score: int
    seconds: int
    text: str
    date: datetime.datetime

    def __init__(self, name, score, seconds, text, date) -> None:
        self.name = name
        self.score = score
        self.seconds = seconds
        self.text = text
        self.date = date
    
    @classmethod
    def _parsedict(self, data) -> Score:
        score = int(data['score'])
        seconds = int(data['seconds'])
        date = dateparser.parse(data['date'])
        return Score(data['name'], score, seconds, data['text'], date)

    @staticmethod
    def parse_score_dict(data) -> ScoreList:
        entries = data['dreamlo']['leaderboard']['entry']
        return [Score._parsedict(entry) for entry in entries]


ScoreList = list[Score]
ResponseWithScores = tuple[requests.Response, ScoreList]


class LeaderboardManager:
    private_code: str
    public_code: str
    next_thread_id: int

    def __init__(self, private, public) -> None:
        self.private_code = private
        self.public_code = public
        self.next_thread_id = 1

    def _newscore_inner(self, promise: PromisingThread, original_name: str, endpoint: str, include_scores: bool):
        trys = 0
        try:
            while True:
                if promise.canceled:
                    logging.info('Score upload/download canceled after %s attampts' % trys)
                    return None, 'Canceled score upload/download'
                trys += 1
                logging.info('Score upload/download attempt #%s...' % trys)
                res = requests.get(endpoint)
                if res.status_code == 200:
                    break
            logging.info('Score upload/download recieved HTTP 200 from server after %s attempts' % trys)
        except Exception as e:
            logging.error('Score upload/download failed due to network error after %s attempts' % trys, exc_info=e)
            return None, None
        if include_scores:
            try:
                parsed = Score.parse_score_dict(res.json())
            except Exception as e:
                logging.error('Score upload/download failed due to JSON error: %r' % res.text, exc_info=e)
                return res, res.text
            logging.info('Score upload/download succeeded')
            return res, parsed
        logging.info('Score upload (only) succeeded')
        return res, None

    def newscore(self, name: str, score: int, time: int = None, text: str = None, *, include_scores=False) -> Union[None, requests.Response, ResponseWithScores]:
        if text is not None and time is None:
            raise ValueError('time required')

        quote_name = urllib.parse.quote(name)
        if time is None:
            endpoint = END_NEWSCORE_SCORE % (self.private_code, quote_name,  score)
        elif text is None:
            endpoint = END_NEWSCORE_SCORE_TIME % (self.private_code, quote_name,  score, time)
        else:
            endpoint = END_NEWSCORE_SCORE_TIME_MESSAGE % (self.private_code, quote_name,  score, time, text)
        if include_scores:
            endpoint = endpoint.replace('add', 'add-json', 1)
        prom = PromisingThread(
            target=self._newscore_inner,
            args=(name, endpoint, include_scores),
            daemon=True,
            name=f'Score-Manager-{self.next_thread_id}'
        )
        self.next_thread_id += 1
        prom.start()
        return prom

    def getscores(self) -> Union[None, ResponseWithScores]:
        endpoint = END_GETSCORES_JSON % self.public_code
        try:
            while True:
                res = requests.get(endpoint)
                if res.status_code == 200:
                    break
        except Exception:
            import traceback
            traceback.print_exc()
            return None, None
        try:
            return res, Score.parse_score_dict(res.json())
        except Exception:
            import traceback
            traceback.print_exc()
            return res, None
