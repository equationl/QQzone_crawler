#!/usr/bin/env python3
#-*- coding:utf-8 -*-

'''
用到的工具函数、变量集合
'''

import os
import re
from urllib import parse
import requests


def get_cookie():
    '''Get cookie from cookie_file'''
    with open('cookie_file') as f:
        cookie = f.read()
    cookie = cookie.replace('\n', '')

    return cookie

cookie = get_cookie()

headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6',
    'accept-encoding': 'gzip, deflate, br',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'cookie': cookie,
    'connection': 'keep-alive'
}

def get_g_tk():
    ''' make g_tk value'''

    pskey_start = cookie.find('p_skey=')
    pskey_end = cookie.find(';', pskey_start)
    p_skey = cookie[pskey_start+7: pskey_end]

    h = 5381

    for s in p_skey:
        h += (h << 5) + ord(s)

    return h & 2147483647

g_tk = get_g_tk()


def get_qzonetoken(qqnum):
    '''获取qzonetoken，它位于空间首页的源代码中'''
    index_url = "https://user.qzone.qq.com/%s" % qqnum
    headers['referer'] = 'https://qzs.qq.com/qzone/v5/loginsucc.html?para=izone'
    headers['upgrade-insecure-requests'] = '1'
    res = requests.get(index_url, headers=headers)
    src = res.text
    search_res = re.search(r'g_qzonetoken.*return\s*"(.*)";}', src, re.S)
    return search_res.group(1) if search_res else ''


def parse_moods_url(qqnum):
    '''This method use to get every friend's mood cgi url
       So it needs the friend's qqnumber to get their url
    '''

    params = {"cgi_host": "http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6",
              "code_version": 1,
              "format": "jsonp",
              "g_tk": g_tk,
              "hostUin": qqnum,
              "inCharset": "utf-8",
              "need_private_comment": 1,
              "notice": 0,
              "num": 20,
              "outCharset": "utf-8",
              "sort": 0,
              "uin": qqnum}
    host = "https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?"

    url = host + parse.urlencode(params)
    return url

def parse_friends_url():
    '''This method only generate the friends of the owner
       So do not need to get qq number, just get it from
       self cookie
    '''

    cookie = headers['cookie']
    qq_start = cookie.find('uin=o')
    qq_end = cookie.find(';', qq_start)
    qqnumber = cookie[qq_start+5 : qq_end]
    if qqnumber[0] == '0':
        qqnumber = qqnumber[1:]
    # 先获取qzonetoken
    qzonetoken = get_qzonetoken(qqnumber)
    params = {"uin": qqnumber,
              "fupdate": 1,
              "action": 1,
              "g_tk": g_tk,
              "qzonetoken": qzonetoken}

    host = "https://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/right/get_entryuinlist.cgi?"
    url = host + parse.urlencode(params)

    return url


def parse_likes_url(mood_id, qq):
    """
    :param mood_id: 说说id
    :param begin_uid: 获取起点（qq）
    :return:
    """
    #cookie中储存的qq号似乎前面加了一个英文字母 o ？
    user_qq_num = cookie[cookie.find("uin=")+5:]
    user_qq_num = user_qq_num[:user_qq_num.find(";")]
    user_qq_num = int(user_qq_num)
    unikey =  '''http://user.qzone.qq.com/'''+qq+'''/mood/'''+mood_id
    params = {"g_tk": g_tk,
              "unikey": unikey,
              "query_count": 60,
              "uin": user_qq_num}
    host = "https://user.qzone.qq.com/proxy/domain/users.qzone.qq.com/cgi-bin/likes/get_like_list_app?"

    url = host + parse.urlencode(params)
    return url


def parse_count_data_url(mood_id, qq):
    """
    :param mood_id: 说说id
    :param qq: 所属qq
    :return:
    """
    unikey = '''http://user.qzone.qq.com/'''+qq+'''/mood/'''+mood_id
    params = {"unikey": unikey,
              "fupdate":1,
              "g_tk": g_tk}
    host = "https://user.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/user/qz_opcnt2?"

    url = host + parse.urlencode(params)
    return url


def parse_comments_url(mood_id, qq):
    """
    :param mood_id: 说说id
    :param qq: 所属qq
    :return:
    """
    topic_id = qq+"_"+mood_id
    params = {"need_private_comment": 1,
              "hostUin": qq,
              "num": 20,
              "order": 0,
              "topicId": topic_id,
              "format": "jsonp",
              "g_tk": g_tk
              }
    host = "https://h5.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_getcmtreply_v6?"

    url = host + parse.urlencode(params)
    return url


def parse_mood_data_url(qq_num, mood_id, count):
    """
    :param qq_num: 所属id
    :param mood_id: 说说id
    :param count: 查询数量
    :return:
    """
    unikey = "http%3A%2F%2Fuser.qzone.qq.com%2F754237716%2Fmood%2F"+mood_id
    params = {"g_tk": g_tk,
              "unikey": unikey,
              "begin_uid": 0,
              "query_count": count,
              "if_first_page": 1,
              "uin": qq_num}
    host = "https://user.qzone.qq.com/proxy/domain/users.qzone.qq.com/cgi-bin/likes/get_like_list_app?"

    url = host + parse.urlencode(params)
    return url


def check_path(path):
    '''This method use to check if the path is exists.
       If not, create that
    '''

    if not os.path.exists(path):
        os.mkdir(path)
