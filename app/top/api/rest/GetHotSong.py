from ..base import BaseApi


class GetHotSong(BaseApi):
    def __init__(self, app, id):
        BaseApi.__init__(self, app)
        self.id = id
        self.set_api('alibaba.xiami.api.artist.hotSongs.get')
