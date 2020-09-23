# -*- coding: utf8 -*-

import os
import requests
import simplejson as json

import libi2g

log = libi2g.get_logger()

class Gotify:
    
    def __init__(self):
        
        self.gotify_server = libi2g.get_config('gotify', 'host')
        self.gotify_token = libi2g.get_config('gotify', 'token')
        self.verbose = libi2g.get_config('main', 'verbose', default=False)
        
    def push(self, mail):
        
        log.info('push message to gotify')
        
        gotify_server = self.gotify_server
        
        if 'token' in mail:
            gotify_token = mail['token']
        else:
            gotify_token = self.gotify_token
        
        params = {
            'title': mail['subject'],
            'message': mail['body'],
            'priority': mail['priority'],
        }
        
        if 'extras' in mail:
            params['extras'] = mail['extras']
            
        # debug message to gotify
        log.debug('dump: %s', json.dumps(params))
        
        push = requests.post('{0}/message?token={1}' \
            .format(gotify_server,gotify_token), json=params)
        
        if push.status_code != 200:
            log.error('error %s occured while sending message to gotify', 
                push.status_code)
            
            return False
            
        log.debug('message "{0}" with priority "{1}" pushed to gotify' \
            .format(params['title'], params['priority']))
        
if __name__ == '__main__':
    pass