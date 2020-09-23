#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os
import email
import html2text

import libi2g

log = libi2g.get_logger()

class Imap2Gotify:
    
    def __init__(self):
        
        self.verbose = libi2g.get_config('main', 'verbose', default=False)
        
        self.imap = libi2g.Imap()
        self.gotify = libi2g.Gotify()
        
    def process_mail(self, mail):
        '''
            receive each mail as byte message (libi2g.imap --> idle_mail)
        '''
        
        mail = email.message_from_bytes(mail)
        
        # get from
        sender = mail.get('from')
        
        # get body
        if mail.is_multipart():
            body = get_body(mail.get_payload(0))
            try:
                body = body.decode('latin-1').encode('utf8')
            except:
                pass
        else:
            body = mail.get_payload(None, True)
            
        # formatting mark_down of body
        
        h = html2text.HTML2Text()
        h.ignore_links = False
        
        body = h.handle(body.decode())
        
        # get subject
        try:
            h = email.decode_header(mail.get('subject'))
            subject = h[0][0].decode('latin-1').encode('utf8')
        except:
            subject = mail.get('subject')
            
        mail = {
                'body': body,
                'from': sender,
                'subject': subject,
                'priority': 1
               }
        
        return mail
        
    def process_rules(self, mail):
        
        rules = libi2g.get_config('rules')
        
        for sid, rule in rules.items():
            
            match = False
            
            if all(k in rule for k in ('from', 'subject')):
                if rule['from'] in mail['from']:
                    if rule['subject'] in mail['subject']:
                        match = True
                        
            elif any(k in rule for k in ('from', 'subject')):
                if 'subject' in rule and rule['subject'] in mail['subject']:
                    match = True
                    
                elif 'from' in rule and rule['from'] in mail['from']:
                    match = True
                    
            if not match:
                continue
                
            if 'priority' in rule:
                mail['priority'] = int(rule['priority'])
            else:
                log.warn('priority missing in the rule {r}, fallback to 2')
                # TODO: check if flag exists or priority header in the mail
                mail['priority'] = 2
                
            if 'token' in rule:
                log.debug('token in rule: %s', rule['token'])
                mail['token'] = rule['token']
                
            if 'extras' in rule:
                log.debug('extras in rule: %s', rule['extras'])
                mail['extras'] = rule['extras']
                
            log.debug('email processed, from: "{0}", subject: "{1}", priority: "{2}"' \
                .format(mail['from'], mail['subject'], mail['priority']))
            
            return mail
            
        log.info('ignoring mail - no rule matches')
        
    def main_loop(self):
        
        log.debug('enter main loop')
        
        mails = self.imap.idle_mail()
        
        for mail in mails:
            
            mail = self.process_mail(mail)
            mail = self.process_rules(mail)
            
            if mail: # send notication
                self.gotify.push(mail)
                
        log.debug('exit main loop')
        
if __name__ == '__main__':
    main = Imap2Gotify()
    
    main.main_loop()