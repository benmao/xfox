#!/usr/bin/env python
# coding:utf-8

"""
Created by ben on 2010/8/24 .
Copyright (c) 2010 http://sa3.org All rights reserved. 
"""

import random


STR = 'abcdefghijklmnopqrstuvwxyz0123456789-'
def random_url():
    return ''.join(random.sample(STR,random.randint(3,30)))

def random_date():
    return '%s-%s-%s' % (random.randint(2000,2100),random.randint(1,12),random.randint(1,31))

TEMPLATE = '''<url>
		<loc>http://xfox.appspot.com/%s</loc>
		<lastmod>%s</lastmod>
		<changefreq>weekly</changefreq>
	</url>'''

from StringIO import StringIO
import gzip

def gen_data(limit=1000):
    f = gzip.open('sitemap-%s.gz' % limit,'wb')
    f.write(''.join([TEMPLATE % (random_url(),random_date()) for i in range(limit)]))
    f.close()
    

if __name__=='__main__':
    for i in range(1,20):
        gen_data(i*1000)
        