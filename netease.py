import requests
from lxml import etree
import execjs
import json
import pandas as pd
import time
from bs4 import BeautifulSoup
import traceback
from concurrent.futures import ThreadPoolExecutor
import threading
import my_proxy
import os

logs_path = './logs.txt'
comment_path = './comment.txt'
node_modules_path = './node_modules'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 Edg/108.0.1462.76",
}

cookies = {
    "os": "pc",
    "_ntes_nnid": "7e936b3b462b3199b427507c205c786e,1672924006421",
    "_ntes_nuid": "7e936b3b462b3199b427507c205c786e",
    "NMTID": "00OWtBo1kn_i3o5WUKcumsvI5Pn5uwAAAGFggqGTw",
    "WEVNSM": "1.0.0",
    "WNMCID": "qzbrlw.1672924006646.01.0",
    "WM_TID": "omzc4nMEhadBEAQUQRbUMtQcAd3EkFhR",
    "__snaker__id": "MTKlaIw5LU3BEavt",
    "YD00000558929251:WM_TID": "BypYplLemQBARUFERULEN8FYRNieOg7E",
    "ntes_kaola_ad": "1",
    "YD00000558929251:WM_NIKE": "9ca17ae2e6ffcda170e2e6eed6f674fc8f8f95db2597eb8ea2c55b829b8aadd447b196878dcc6ab4b8bf83d82af0fea7c3b92aa7b6bdb5d3218eaea685bb4ff7ac8bccaa4e978cb899d263aee788b8e63c82939eb6cf66a793b8b2b47493ae9db9cd508e8afcd3f4648e9caaace66aed8ca196fc3394f0a18bd77ba3ba009afc6381e9f994e434a6b381b4b46f9cef87d7cc398fb2f98fc63bb3aba392f580ba8a8590d047bbebbaaab84eb39bc084cd72ad999c8dd037e2a3",
    "P_INFO": "17864267822|1673206654|1|music|00&99|null&null&null#shd&371300#10#0|&0||17864267822",
    "__remember_me": "true",
    "MUSIC_U": "1cfcbe0020ad89bf7f48a313731b5e4d91b55814a216928112695aa1f0832d9e519e07624a9f005314715377828d08d5fa762ff0155526e3d953a10dc43ffbb59797a9a1f3609593d4dbf082a8813684",
    "__csrf": "459799e0c991ae85d457ea559389338d",
    "_iuqxldmzr_": "32",
    "gdxidpyhxdE": "kknSxgcvyk8Po7Uno6yJV3R8rPeTXjvRa6E29LhK93C01a1OSYvdKZ1KgwbYsjXu+/ydTu5Hxcgf8/10iUxt40t+pm4IqnKI7oSq22RcJU4ckoXiKGmPyBvB6hwDqfeekhYU/Ji4Rk10MsNOeePIPW7PT9nHj0/ie2oqA3qCZ992jAgI:1673212554935",
    "WM_NIKE": "9ca17ae2e6ffcda170e2e6ee9ad55af49081aaf762f6eb8ab7c54e878f9e82d170b497bed3dc50a3b0988ad82af0fea7c3b92a85b2af89f94ab68a84d0c462adef8dd6f234b2b68c91b4609b9f84b6c76be9b18586d459829bc0a4f37a83b199b6d15394af9b82e24bbbbe9782b2498db09bb7ea63a691fa90bb7a8f95a785cd67af9fa5acd021e98e98a4e679b5b98e8be43e8f8e8e99b27ab0eaf885f180afed9e97d76df8b8a28ec259a3e89bb3cc7be9f19c8dea37e2a3",
    "playerid": "61303519",
    "JSESSIONID-WYYY": "8by29wHRuUDIRrxT6rKutheeO2otCVq2He1ZdXmjEc9HEeKSPMWnlCrYmCjRFjNZOCe/PIDrjJnyhs/46eB\\+If05oouMWbN\\lUKa\\MPPqwsw5RksFi\\9rgSI/yllIxbz8pxS98aatI\\IIPeY9xQK5Qr1cTHfPgD8/sOnU8ycVX45i0p:1673353097535"
}

empty_proxy = my_proxy.Proxy(init=False)
empty_proxy.get_random_proxy = lambda: {}

def write_logs(s):
    with open(logs_path, 'a', encoding='utf-8') as f:
        f.write(s)

def write_comment(s):
    with open(comment_path, 'a', encoding='utf-8') as f:
        f.write(s)

def write_file(file_name, s):
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(s)

def get_params_comment(song_id, pageNo, pageSize, cursor):
    node = execjs.get()
    with open('get_params.js', encoding='utf-8') as f:
        js_code = f.read()
    ctx = node.compile(js_code, cwd=node_modules_path)
    params = ctx.call('get_params_comment', song_id, pageNo, pageSize, cursor)
    return params

def get_params_user(uid, type=0):
    node = execjs.get()
    with open('get_params.js', encoding='utf-8') as f:
        js_code = f.read()
    ctx = node.compile(js_code, cwd=node_modules_path)
    params = ctx.call('get_params_user', uid, type)
    return params


# 获取某首歌曲全部评论
def get_all_comment(song_name, song_id):
    try:
        url = 'https://music.163.com/weapi/comment/resource/comments/get?csrf_token='
        res = requests.post(url, data=get_params_comment(song_id, 1, 20, -1), 
                cookies=cookies, headers=headers, timeout=5)
        res_json = json.loads(res.text)
        total_count = res_json['data']['totalCount']
        write_logs(f'正在爬取{song_name}, 共有{total_count}条评论\n')

        if total_count > comment_limit:
            return

        page_count = (total_count - 1) // page_size + 1
        cursor = -1
        comment_list = []
        for page in range(1, page_count + 1):
            write_logs(f'正在爬取第{page}页\n')
            res = requests.post(url, data=get_params_comment(song_id, page, page_size, cursor), 
                    cookies=cookies, headers=headers, timeout=5)
            res_json = json.loads(res.text)
            
            while res_json['code'] == 405:
                time.sleep(6)
                res = requests.post(url, data=get_params_comment(song_id, page, page_size, cursor), 
                        cookies=cookies, headers=headers, timeout=5)
                res_json = json.loads(res.text)

            cursor = res_json['data']['cursor']
            comment_json = res_json['data']['comments']
            for comm in comment_json:
                comment_list.append({
                    'user': comm['user']['nickname'],
                    'comment': comm['content'],
                    'time': comm['timeStr']})
        df = pd.DataFrame(comment_list)
        df.to_excel('comment.xlsx', index=False)
    except Exception as e:
        print(e)

# 寻找某用户在某歌曲中的评论
def get_comment_song_user(song_name, song_id, uid, proxy=empty_proxy):
    try:
        url = 'https://music.163.com/weapi/comment/resource/comments/get?csrf_token='
        res = requests.post(url, data=get_params_comment(song_id, 1, 20, -1), 
                cookies=cookies, headers=headers, proxies=proxy.get_random_proxy(), timeout=5)
        res_json = json.loads(res.text)

        # 丑陋的处理，405 时等待 5 秒再发请求
        while res_json['code'] == 405:
            time.sleep(5)
            res = requests.post(url, data=get_params_comment(song_id, 1, 20, -1), 
                    cookies=cookies, headers=headers, proxies=proxy.get_random_proxy(), timeout=5)
            res_json = json.loads(res.text)

        total_count = res_json['data']['totalCount']
        write_logs(f'正在爬取{song_name}, 共有{total_count}条评论\n')

        if total_count > comment_limit:
            return

        page_count = (total_count - 1) // page_size + 1
        cursor = -1
        for page in range(1, page_count + 1):
            # write_logs(f'正在爬取第{page}页\n')
            res = requests.post(url, data=get_params_comment(song_id, page, page_size, cursor),
                    cookies=cookies, headers=headers, proxies=proxy.get_random_proxy(), timeout=5)
            res_json = json.loads(res.text)
            
            while res_json['code'] == 405:
                time.sleep(5)
                res = requests.post(url, data=get_params_comment(song_id, page, page_size, cursor),
                        cookies=cookies, headers=headers, proxies=proxy.get_random_proxy(), timeout=5)
                res_json = json.loads(res.text)

            cursor = res_json['data']['cursor']
            comment_json = res_json['data']['comments']
            for comm in comment_json:
                user_id = comm['user']['userId']
                comment = comm['content']
                comment_time = comm['timeStr']
                if user_id == uid:
                    print(f'歌曲：{song_name}, id: {song_id}, 评论：{comment}, 评论时间：{comment_time}')
                    write_comment(f'歌曲：{song_name}, id: {song_id}, 评论：{comment}, 评论时间：{comment_time}\n')
    except Exception as e:
        print(f'song_name = {song_name}, song_id = {song_id}, uid = {uid}')
        print(e)
        print(e.args)
        # print(traceback.format_exc())
        print('============')
        
# 寻找某用户在歌曲列表中的评论
def get_comment_with_list(list_name, song_list, uid, proxy):
    write_logs(f'正在获取{list_name}中的评论，共{len(song_list)}首歌曲\n')
    for song_name, song_id in song_list:
        get_comment_song_user(song_name, song_id, uid, proxy)
    write_logs('\n')

# 获取用户所有歌单（创建与收藏）
def get_playlist(uid):
    url = 'https://music.163.com/weapi/user/playlist?csrf_token='
    res = requests.post(url, data=get_params_user(uid), cookies=cookies, headers=headers, timeout=5)
    res_json = json.loads(res.text)
    playlist_created = []
    playlist_favorite = []
    for pl in res_json['playlist']:
        if pl['creator']['userId'] == uid:
            playlist_created.append((pl['name'], pl['id']))
        else:
            playlist_favorite.append((pl['name'], pl['id']))

    return playlist_created, playlist_favorite

# 获取歌单内所有歌曲
def get_playlist_song(playlist_id):
    url = 'https://music.163.com/playlist?id=' + str(playlist_id)
    res = requests.get(url, cookies=cookies, headers=headers, timeout=5)
    soup = BeautifulSoup(res.text, 'lxml')
    if soup.find(id="song-list-pre-cache") == None:
        return []
    song_html = soup.find(id="song-list-pre-cache").find_all('a')

    song_list = []
    for s in song_html:
        song_list.append((s.get_text(), s.get('href').lstrip('/song?id=')))
    return song_list

# 获取听歌排行所有歌曲
def get_rank_song(uid):
    url = 'https://music.163.com/weapi/v1/play/record?csrf_token='
    res = requests.post(url, data=get_params_user(uid, -1), cookies=cookies, headers=headers, timeout=5)
    res_json = json.loads(res.text)

    all_song = []
    week_song = []
    for song in res_json['allData']:
        all_song.append((song['song']['name'], song['song']['id']))
    for song in res_json['weekData']:
        week_song.append((song['song']['name'], song['song']['id']))
    return all_song, week_song

# 获取某用户所有评论
def get_comment_from_user(uid, favorite=False, is_proxy=False):
    write_logs(f'\n开始时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}\n')
    write_logs(f'ID: {uid}\n\n')
    
    # 代理
    if is_proxy:
        proxy = my_proxy.Proxy()
    else:
        proxy = empty_proxy

    # 获取听歌排行歌曲评论
    all_song, week_song = get_rank_song(uid)
    get_comment_with_list('全部排行', all_song, uid, proxy)
    get_comment_with_list('每周排行', week_song, uid, proxy)

    # 获取歌单中歌曲评论
    playlist_created, playlist_favorite = get_playlist(uid)
    for playlist_name, playlist_id in playlist_created:
        get_comment_with_list('创建歌单：' + playlist_name, get_playlist_song(playlist_id), uid, proxy)

    if favorite:
        for playlist_name, playlist_id in playlist_favorite:
            get_comment_with_list('收藏歌单：' + playlist_name, get_playlist_song(playlist_id), uid, proxy)
        
    
comment_limit = 10000
page_size = 1000
uid = 0

if __name__ == '__main__':
    # Todo: 异常处理

    get_comment_from_user(uid, favorite=True, is_proxy=False)
