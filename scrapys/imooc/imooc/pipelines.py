# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
from utils import rds
from imooc import items
from datetime import datetime


class ImoocPipeline(object):
    def __init__(self):
        # PostgreSQL
        host = 'localhost'
        port = 12432
        db_name = 'scrapy'
        username = db_name
        password = db_name
        self.conn = psycopg2.connect(host=host, port=port, user=username,
                                     password=password, dbname=db_name)
        self.cur = self.conn.cursor()
        # Redis
        self.redis = rds.Rds(host=host, port=12379, db=1, password='redis6379').redis_cli

    def process_item(self, item, spider):
        name = item['name']
        difficult = item['difficult']
        student = item['student']
        desc = item['desc']
        image_urls = item['image_urls'][0]
        detail = item['detail']
        duration = item['duration']
        overall_score = float(item['overall_score'])
        teacher_nickname = item['teacher_nickname']
        teacher_avatar = item.get('teacher_avatar')
        teacher_job = item['teacher_job']
        now = datetime.now()
        str_now = now.strftime('%Y-%m-%d %H:%M:%S')

        if isinstance(item, items.CourseItem):
            # 免费课程
            course_id = item['course_id']
            label = item['label']
            content_score = float(item['content_score'])
            concise_score = float(item['concise_score'])
            logic_score = float(item['logic_score'])
            summary = item['summary']
            tip = item['tip']
            can_learn = item['can_learn']

            key = 'imooc:course:{0}'.format(course_id)
            if self.redis.exists(key):
                params = (student, overall_score, content_score, concise_score, logic_score, now, course_id)
                self.cur.execute(update_course(), params)
            else:
                self.redis.set(key, str_now)
                params = (course_id, name, difficult, student, desc, label, image_urls, detail, duration,
                          overall_score, content_score, concise_score, logic_score, summary, teacher_nickname,
                          teacher_avatar, teacher_job, tip, can_learn, now, now)
                self.cur.execute(add_course(), params)
        if isinstance(item, items.CodingItem):
            # 实战课程
            price = item['price']
            coding_id = item['coding_id']
            video = item['video']
            small_title = item['small_title']
            detail_desc = item['detail_desc']

            key = 'imooc:coding:{0}'.format(coding_id)
            if self.redis.exists(key):
                params = (student, price, overall_score, now, coding_id)
                self.cur.execute(update_coding(), params)
            else:
                self.redis.set(key, str_now)
                params = (coding_id, name, difficult, student, desc, image_urls, price, detail,
                          overall_score, teacher_nickname, teacher_avatar, duration, video, small_title,
                          detail_desc, teacher_job, now, now)
                self.cur.execute(add_coding(), params)

        self.conn.commit()
        return item

    def close_spider(self, spider):
        """ Release connection
        
        :param spider: 
        :return: 
        """
        self.cur.close()
        self.conn.close()


def add_course():
    """Save data to Course
    
    :return: 
    """

    sql = 'insert into tb_imooc_course(course_id,"name",difficult,student,"desc",label,image_urls,' \
          'detail,duration,overall_score,content_score,concise_score,logic_score,summary,' \
          'teacher_nickname,teacher_avatar,teacher_job,tip,can_learn,update_time,create_time) ' \
          'values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    return sql


def update_course():
    """Update Course data
    
    :return: 
    """

    sql = 'update tb_imooc_course set student=%s,overall_score=%s,content_score=%s,concise_score=%s,' \
          'logic_score=%s,update_time=%s where course_id = %s'
    return sql


def add_coding():
    """Save data to Coding

    :return:
    """

    sql = 'insert into tb_imooc_coding(coding_id,"name",difficult,student,"desc",image_urls,price,detail,' \
          'overall_score,teacher_nickname,teacher_avatar,duration,video,small_title,detail_desc,teacher_job,' \
          'update_time,create_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    return sql


def update_coding():
    """Update Coding data

    :return:
    """

    sql = 'update tb_imooc_coding set student=%s,price=%s,overall_score=%s,update_time=%s where coding_id = %s'
    return sql
