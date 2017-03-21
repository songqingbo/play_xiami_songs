# -*- coding:utf-8 -*-
from app.helpers.xiami_helper import get_rank_songs
import time
import MySQLdb


class WorkXiamiSongs():
    def __init__(self, sleep=86400):
        self.host = '101.200.159.42'
        self.user = 'java'
        self.pw = 'inspero'
        self.database = 'musicnew'
        self.sleep_time = sleep
        self.time_stamp = []
        self.database = MySQLdb.connect(self.host, self.user, self.pw, self.database, charset='utf8')
        self.cursor = self.database.cursor()
        self.cursor.execute('select version()')
        data = self.cursor.fetchone()
        print int(time.time()), 'Database version : %s' % data
        del data

    def get_new_music_all(self):
        '''
        :return:the list contains all songs
        '''
        response_huayu = get_rank_songs('newmusic_huayu')
        response_oumei = get_rank_songs('newmusic_oumei')
        response_ri = get_rank_songs('newmusic_ri')
        response_han = get_rank_songs('newmusic_han')
        new_huayu_songs = response_huayu['user_get_response']['data']['songs']
        new_oumei_songs = response_oumei['user_get_response']['data']['songs']
        new_ri_songs = response_ri['user_get_response']['data']['songs']
        new_han_songs = response_han['user_get_response']['data']['songs']
        songs_all = new_huayu_songs + new_oumei_songs + new_ri_songs + new_han_songs
        return songs_all

    def process_songs_list(self, songs_all):
        '''
        :param songs_all:the list contains all songs
        :return: each of the list named songs can be inserted into mysql
        '''
        songs = []
        exist_ids = []
        fn = open('inserted_song_ids.txt', 'r')
        ids_lines = fn.readlines()
        for id_line in ids_lines:
            id = int(id_line.strip())
            exist_ids.append(id)
        fn.close()
        for song in songs_all:
            song_id = song['song_id']
            if song_id not in exist_ids:
                try:
                    songs.append(song)
                except:
                    pass
            else:
                pass
        return songs

    def get_insert_list(self, songs):
        '''
        :param songs:list which contains all songs to be inserted into mysql
        :return: list of tuple
        '''
        data_list = []
        for song in songs:
            try:
                song_name = str(song['song_name'].encode('utf-8'))
            except:
                song_name = None
            try:
                album_name = str(song['album_name'].encode('utf-8'))
            except:
                album_name = None
            try:
                artist_name = str(song['artist_name'].encode('utf-8'))
            except:
                artist_name = None
            try:
                lyric_text = str(song['lyric_text'].encode('utf-8'))
            except:
                lyric_text = None
            try:
                lyric = str(song['lyric'].encode('utf-8'))
            except:
                lyric = None
            try:
                logo = str(song['logo'].encode('utf-8'))
            except:
                logo = None
            try:
                artist_logo = str(song['artist_logo'].encode('utf-8'))
            except:
                artist_logo = None
            try:
                singers = str(song['singers'].encode('utf-8'))
            except:
                singers = None
            try:
                listen_file = str(song['listen_file'].encode('utf-8'))
            except:
                listen_file = None
            try:
                title = str(song['title'].encode('utf-8'))
            except:
                title = None
            try:
                name = str(song['name'].encode('utf-8'))
            except:
                name = None
            try:
                album_logo = str(song['album_logo'].encode('utf-8'))
            except:
                album_logo = None
            try:
                lyric_file = str(song['lyric_file'].encode('utf-8'))
            except:
                lyric_file = None
            try:
                song_id = str(song['song_id'])
            except:
                song_id = None
            try:
                album_id = str(song['album_id'])
            except:
                album_id = None
            try:
                artist_id = str(song['artist_id'])
            except:
                artist_id = None
            try:
                recommends = str(song['recommends'])
            except:
                recommends = None
            try:
                length = str(song['length'])
            except:
                length = None
            try:
                play_count = str(song['play_count'])
            except:
                play_count = None
            try:
                play_seconds = str(song['play_seconds'])
            except:
                play_seconds = None
            try:
                demo = str(song['demo'])
            except:
                demo = None
            try:
                play_authority = str(song['play_authority'])
            except:
                play_authority = None
            try:
                width = str(song['width'])
            except:
                width = None
            try:
                favourite = str(song['favourite'])
            except:
                favourite = None
            insert_timestamp = str(int(time.time()))
            data_list.append((
                insert_timestamp, song_name, album_name, artist_name, lyric_text, lyric, logo, artist_logo,
                singers, listen_file, title, name, album_logo, lyric_file, song_id, album_id, artist_id,
                recommends, length, play_count, play_seconds, demo))
        return data_list

    def insert_function(self, data_list, songs):
        '''
        :param data_list:list to be inserted into mysql
        :return: None
        '''
        sql = 'insert into xiami_songs(insert_timestamp,song_name,album_name,artist_name,lyric_text,lyric,' \
              'logo,artist_logo,singers,listen_file,title,name_var,album_logo,lyric_file,song_id,album_id,artist_id,' \
              'recommends,length_var,play_count,play_seconds,demo) values ' \
              '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        try:
            self.cursor.executemany(sql, data_list)
            self.database.commit()

            fn = open('inserted_song_ids.txt', 'a')
            for s in songs:
                temp_id = s['song_id']
                fn.write(str(temp_id))
                fn.write('\n')
                fn.flush()
            fn.close()

            fx = open('work_log.log', 'a')
            timestamp = time.time()
            fx.write(str(timestamp) + '\t' + '插入%d条' % len(songs))
            fx.write('\n')
            fx.flush()
            fx.close()
        except Exception, e:
            fb = open('error.log', 'w')
            fb.write(str(e))
            fb.write('\n')
            fb.close()
            self.database.rollback()

    def controller(self):
        songs_all = self.get_new_music_all()
        songs = self.process_songs_list(songs_all=songs_all)
        if len(songs) > 0:
            data_list = self.get_insert_list(songs=songs)
            self.insert_function(data_list=data_list, songs=songs)
        else:
            fn = open('work_log.log', 'a')
            timestamp = time.time()
            fn.write(str(timestamp) + '\t' + '插入0条')
            fn.write('\n')
            fn.flush()
            fn.close()


def work(sleep):
    while True:
        obj = WorkXiamiSongs()
        obj.controller()
        time.sleep(sleep)


if __name__ == '__main__':
    work(86400)
