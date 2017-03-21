# -*- coding:utf-8 -*-
from ..top import api
from ..top import AppInfo

domain = 'gw.api.tbsandbox.com'
port = 80

app_key = '23064829'
secret = '29ed3de5990627239d0fdbddd3e94b51'

app = AppInfo(app_key, secret)


def get_similar_songs(_id, _limit):
    r = api.GetSimilarSongs(app, _id=_id, env='default', _limit=_limit)
    print r
    response = r.get_response()
    return response


def get_song_detail(_id):
    r = api.GetSongDetail(app, _id=_id)
    response = r.get_response()
    return response


def get_hot_song(_id):
    r = api.GetHotSong(app=app, id=_id)
    response = r.get_response()
    return response


def get_rank_songs(type):
    r = api.GetRankSongs(app=app, type=type)
    response = r.get_response()
    return response


def get_promotion_albums(type, limit, page):
    '''
    :param type:类型，分为huayu,oumei,ri,han
    :param limit: limit
    :param page: page
    :return:新碟首发返回的数据
    '''
    r = api.GetPromotionAlbums(app=app, type=type, limit=limit, page=page)
    response = r.get_response()
    return response
