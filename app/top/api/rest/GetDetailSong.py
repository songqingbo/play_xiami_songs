from ..base import BaseApi


class GetSongDetail(BaseApi):
    def __init__(self, app, _id):
        BaseApi.__init__(self, app)
        self.id = _id
        self.set_api('alibaba.xiami.api.song.detail.get')
