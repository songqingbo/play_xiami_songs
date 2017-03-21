from ..base import BaseApi


class GetPromotionAlbums(BaseApi):
    def __init__(self, app, type, limit, page):
        BaseApi.__init__(self, app)
        self.type = type
        self.limit = limit
        self.page = page
        self.set_api('alibaba.xiami.api.rank.promotion.albums.get')
