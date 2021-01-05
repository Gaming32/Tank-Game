from __future__ import annotations
import datetime
import json

import dateparser
import requests


END_NEWSCORE_SCORE = 'http://dreamlo.com/lb/%s/add/%s/%i'
END_NEWSCORE_SCORE_TIME = 'http://dreamlo.com/lb/%s/add/%s/%i/%i'
END_NEWSCORE_SCORE_TIME_MESSAGE = 'http://dreamlo.com/lb/%s/add/%s/%i/%i/%s'
END_DELSCORE = 'http://dreamlo.com/lb/%s/delete/%s'
END_CLEARALL = 'http://dreamlo.com/lb/%s/clear'
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


class LeaderboardManager:
    private_code: str
    public_code: str

    def __init__(self, private, public) -> None:
        self.private_code = private
        self.public_code = public

    def _parse_scores(self, data):
        entries = data['dreamlo']['leaderboard']['entry']
        return [Score._parsedict(entry) for entry in entries]

    def newscore(self, name: str, score: int, time: int = None, text: str = None) -> requests.Response:
        if text is not None and time is None:
            raise ValueError('time required')
        if time is None:
            endpoint = END_NEWSCORE_SCORE % (self.private_code, name,  score)
        elif text is None:
            endpoint = END_NEWSCORE_SCORE_TIME % (self.private_code, name,  score, time)
        else:
            endpoint = END_NEWSCORE_SCORE_TIME_MESSAGE % (self.private_code, name,  score, time, text)
        while True:
            res = requests.get(endpoint)
            if res.status_code == 200:
                break
        return res
    
    def getscores(self) -> tuple[requests.Response, list[Score]]:
        endpoint = END_GETSCORES_JSON % self.public_code
        while True:
            res = requests.get(endpoint)
            if res.status_code == 200:
                break
        return res, self._parse_scores(res.json())
