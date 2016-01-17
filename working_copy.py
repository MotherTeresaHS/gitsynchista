import webbrowser as wb
import urllib
import time
import keychain
import console

import log
import util
import sync_config

reload(log)
reload(util)
reload(sync_config)

PARAM_IGNORE_WAKEUP = 'IGNORE_WAKEUP'

global logger

logger = log.open_logging(__name__)

class WorkingCopySupport (object):
  
  def __init__(self, config):
    
    self.config = config
    self.key = util.get_password_from_keychain('Working Copy', 'X-URL-Callback')
    
  def _get_key(self):
    ''' Retrieve the working copy key or prompt for a new one. See https://github.com/ahenry91/wc_sync
    '''
  
    key = keychain.get_password('wcSync', 'xcallback')
    if not key:
      key = console.password_alert('Working Copy Key')
      keychain.set_password('wcSync', 'xcallback', key)
    return key  
  
  def _send_to_working_copy(self, action, payload, x_callback_enabled=True):
    
    # see https://github.com/ahenry91/wc_sync
    
    global logger
    
    x_callback = 'x-callback-url/' if x_callback_enabled else ''
    payload['key'] = self.key
    payload = urllib.urlencode(payload).replace('+', '%20')
    fmt = 'working-copy://{x_callback}{action}/?{payload}'
    url = fmt.format(x_callback=x_callback, action=action, payload=payload)
    
    logger.debug("Issuing callback '%s'" % url)
    
    wb.open(url)  
    
  def wakeup_webdav_server(self):
    
    payload = { 'cmd' : 'start',
                'x-success' : 'pythonista://gitsynchista/gitsynchista?action=run&argv=%s' % PARAM_IGNORE_WAKEUP}
    self._send_to_working_copy(action='webdav', payload=payload)
    #time.sleep(1)
    
  def open_repository(self):
    
    payload = { 'repo' : self.config.repository.remote_path[1:]}
    self._send_to_working_copy(action='open', payload=payload, x_callback_enabled=False)    
    