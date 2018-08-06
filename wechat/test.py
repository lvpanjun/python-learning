import re
import time
import random
import psycopg2
import requests
import wx_mps_sql
from utils import pgs
from datetime import datetime

headers = {
    'Cookie': 'pgv_pvi=6708115456; pgv_si=s4773475328; ptisp=cm; RK=XopsBML0RK; ptcz=73aac9f580839d2b9c7f634ca28f3e19c8bd037390a7f639e5332831aa13b8c4; uin=o1394223902; skey=@KWMdUovjK; pt2gguin=o1394223902; rewardsn=; wxtokenkey=777; wxuin=2089823341; devicetype=android-26; version=26060739; lang=zh_HK; pass_ticket=M7xz2Lwxxg2/8HQMNubFvBpO0NJd70CNvsBxMFErvIDKgQDX0rfCbv80yPHcQKNK; wap_sid2=CO3YwOQHEogBYk9hSVlOWm9XcTluczJRYUE5cEZJb3AwYjZOZGJZN0VHX0ZLcjRpem1NV1J2aXBRNFZwdEZwNllQdnVyRjVyTEx1aDktdDU1eUNPanRpRmVpOFE0UVYzMmxfNVJaN0QwaU1oOXFMZTQyLWFpdU10eFZ1RjZXQXF0YW9SeUpkNkR5QU1BQUF+fjCh05/bBTgNQJVO',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0; WAS-AL00 Build/HUAWEIWAS-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044203 Mobile Safari/537.36 MicroMessenger/6.6.7.1321(0x26060739) NetType/WIFI Language/zh_HK'
}
sql = "select ext_data,date_time,type,id from tb_article where ext_data->'multi_app_msg_item_list' is not null and \
       ext_data->>'multi_app_msg_item_list' <> '[]' and id >=307 order by id asc"

conn_info = "host=localhost port=15234 dbname={0} user=planet password=planet".format('wxmps')
conn = psycopg2.connect(conn_info)
cur = conn.cursor()
cur.execute(sql, ())
rows = cur.fetchall()
for r in rows:
    date_time = r[1]
    msg_type = r[2]
    ext_data = '{}'
    msg_data = ext_data
    print(r[3])
    if r[0]:
        multi_app_msg_item_list = r[0]['multi_app_msg_item_list']
        for app_msg_ext_info in multi_app_msg_item_list:
            msg_id = app_msg_ext_info['fileid']
            if msg_id == 0:
                msg_id = int(time.time() * 1000)
            title = app_msg_ext_info['title']  # 标题
            author = app_msg_ext_info['author']  # 作者
            cover = app_msg_ext_info['cover']  # 封面图
            del_flag = app_msg_ext_info.get('del_flag')  # 标志位
            digest = app_msg_ext_info['digest']  # 关键字
            source_url = app_msg_ext_info['source_url']  # 原文地址
            content_url = app_msg_ext_info['content_url']  # 微信地址

            try:
                html = requests.get(content_url, headers=headers).text
            except requests.exceptions.MissingSchema:
                print('requests.exceptions.MissingSchema = ' + content_url)
            else:
                # group(0) is current line
                comment_str = re.search(r'var comment_id = "(.*)" \|\| "(.*)" \* 1;', html)
                if comment_str:
                    comment_id = comment_str.group(1)
                    # print(comment_id, end='')

                    token_str = re.search(r'window.appmsg_token = "(.*)";', html)
                    if token_str:
                        token = token_str.group(1)
                        if token:
                            pgs.handler(wx_mps_sql.add_article(), (msg_id, date_time, msg_type, msg_data,
                                                                   title, author, cover, digest,
                                                                   content_url, source_url, comment_id,
                                                                   token, del_flag, ext_data,
                                                                   datetime.now()), db_name='wxmps')
                            print('sleep in')
                            time.sleep(random.randint(1, 3))
                            print('sleep out')
