# -*- coding: utf8 -*-

import os
import sys
import email
import imapclient

from time import sleep

import libi2g

log = libi2g.get_logger()

class Imap:
    
    def __init__(self):
        
        # Retrieve IMAP host and login credentials
        self.hostname = libi2g.get_config('imap', 'host')
        self.username = libi2g.get_config('imap', 'username')
        self.password = libi2g.get_config('imap', 'password')
        
        # Retrieve IMAP SSL setting
        self.ssl = libi2g.get_config('imap', 'ssl', default=True)
        
        # Retrieve IMAP folder to monitor
        self.folder = libi2g.get_config('imap', 'folder', default='INBOX')
        
        # Active connection
        self.imap = None
        
    def open_connection(self):
        '''
            Establish connection to IMAP server (retry if there is an error)
            Login to account
            Select IMAP folder
        '''
        
        while True:
            log.info('connecting to IMAP server - {0}'.format(self.hostname))
            
            # Connect to the server
            try:
                imap = imapclient.IMAPClient(self.hostname, use_uid=True, ssl=self.ssl)
            except:
                log.critical('failed to connect to IMAP server - retry')
                
                sleep(10)
                
                continue
                
            else:
                log.debug('server connection established')
                
            # Hold active IMAP object
            self.imap = imap
            
            log.info('login into IMAP server - {0}'.format(self.username))
            
            # Login to IMAP account
            try:
                result = imap.login(self.username, self.password)
            except:
                log.exception('failed to login to IMAP server')
            else:
                log.debug('login successful - {0}'.format(result))
                
            # Select IMAP folder to monitor
            log.info('selecting IMAP folder - {0}'.format(self.folder))
            try:
                result = self.imap.select_folder(self.folder)
            except:
                log.exception('failed to select IMAP folder - {0}' \
                    .format(self.folder))
            else:
                log.debug('folder selected - {0}'.format(self.folder))
                
            return imap
        
    def close_connection(self):
        
        if self.imap is None:
            return
            
        log.info('logout from IMAP server')
        
        try:
            result = self.imap.logout()
        except:
            log.critical('unable to logout from IMAP server')
        else:
            log.debug('successfully logged out - {0}'.format(result))
            
        self.imap = None
        
    def idle_mail(self):
        '''
            This function retries connection, if there are errors 
            on the lower network stack (e.g. socket error). Traps 
            interrupt from keyboard (strg+c) from user.
        '''
        
        log.debug('idle_mail started')
        
        while True:
            # <--- start of connectivity loop
            
            try:
                
                if self.imap is None:
                    self.open_connection()
                    
                while True:
                    # <--- start of mail monitoring loop
                    
                    # check for new messages
                    result = self.imap.search(['UNSEEN'])
                    
                    if result:
                        log.debug('{0} new unread messages - id {1}'.format(
                            len(result), result
                            ))
                            
                        result = self.imap.fetch(result, ['RFC822'])
                        
                        for id, fetch in result.items():
                            
                            try:
                                mail = email.message_from_bytes(fetch[b'RFC822'])
                                
                                log.info('processing email {0} - {1}'.format(
                                    id, mail.get('subject')
                                    ))
                                
                                yield fetch[b'RFC822'] # message bytes
                                
                            except Exception:
                                log.error('failed to process email {0}'.format(each))
                                
                    else:
                        log.debug('no new messages seen')
                        
                    log.debug('request new idle')
                    # After all unread emails are cleared on initial login, start
                    # monitoring the folder for new email arrivals and process 
                    # accordingly. Use the IDLE check combined with occassional NOOP
                    # to refresh. Should errors occur in this loop (due to loss of
                    # connection), return control to IMAP server connection loop to
                    # attempt restablishing connection instead of halting script.
                    self.imap.idle()
                    # TODO: Remove hard-coded IDLE timeout; place in config file
                    result = self.imap.idle_check(timeout=5*60)
                    # 
                    self.imap.idle_done()
                    
                    # reset any auto-logout timers
                    self.imap.noop()
                    
                    # end of mail monitoring loop --->
                    
            except KeyboardInterrupt:
                log.info('terminated by user')
                
                self.imap.idle_done()
                
                sys.exit(1)
                
            except:
                log.debug('lost connection to server - will try again')
                
                self.imap = None
                
            finally:
                self.close_connection()
                
            # end of connectivity loop --->
            
        log.debug('idle_mail stopped')
        
if __name__ == '__main__':
    imap = Imap()
    
    imap.idle_main()
    
