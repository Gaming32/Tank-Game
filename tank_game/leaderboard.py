from __future__ import annotations
import datetime
import json
from tank_game.promise import PromisingThread
from typing import Union

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

    def __init__(self, private, public) -> None:
        self.private_code = private
        self.public_code = public

    def _newscore_inner(self, promise: PromisingThread, endpoint: str, include_scores: bool):
        try:
            while True:
                if promise.canceled:
                    print('Score upload/download canceled')
                    return None, None
                res = requests.get(endpoint)
                if res.status_code == 200:
                    break
        except Exception:
            import traceback
            traceback.print_exc()
            return None, None
        try:
            if include_scores:
                return res, Score.parse_score_dict(res.json())
            return res, None
        except Exception:
            import traceback
            traceback.print_exc()
            return res, None

    def newscore(self, name: str, score: int, time: int = None, text: str = None, *, include_scores=False) -> Union[None, requests.Response, ResponseWithScores]:
        if text is not None and time is None:
            raise ValueError('time required')
        if time is None:
            endpoint = END_NEWSCORE_SCORE % (self.private_code, name,  score)
        elif text is None:
            endpoint = END_NEWSCORE_SCORE_TIME % (self.private_code, name,  score, time)
        else:
            endpoint = END_NEWSCORE_SCORE_TIME_MESSAGE % (self.private_code, name,  score, time, text)
        if include_scores:
            endpoint = endpoint.replace('add', 'add-json', 1)
        prom = PromisingThread(target=self._newscore_inner, args=(endpoint, include_scores), daemon=True)
        prom.start()
        return prom
        # return PromisingThread(target=)
        return self._newscore_inner(endpoint, include_scores)

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
