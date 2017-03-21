from ..base import BaseApi


class GetSimilarSongs(BaseApi):
    def __init__(self, app, _id, env='default', _limit=100):
        BaseApi.__init__(self, app, env=env)
        self.id = _id
        self.limit = _limit
        self.set_api('alibaba.xiami.api.song.similar.get')
