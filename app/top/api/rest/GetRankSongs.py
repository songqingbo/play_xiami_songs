from ..base import BaseApi


class GetRankSongs(BaseApi):
    def __init__(self, app, type):
        BaseApi.__init__(self, app)
        self.type = type
        self.set_api('alibaba.xiami.api.rank.songs.get')
