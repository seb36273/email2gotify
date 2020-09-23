# -*- coding: utf8 -*-

import configparser

__all__ = (
           'get_configparser',
           'get_config',
           'get_rules',
          )

CFG_PATH = "/etc/gotify/imap2gotify.toml"

__CONFIG__ = None

import libi2g

log = libi2g.get_logger()

def get_configparser(path=CFG_PATH):
    global __CONFIG__
    
    if __CONFIG__ is not None:
        return __CONFIG__
        
    # Read config file - halt script on failure
    try:
        config_file = open(path,'r+')
    except IOError:
        log.critical('configuration file is missing')
        raise
        
    config = configparser.SafeConfigParser()
    config.readfp(config_file)
    
    __CONFIG__ = config
    
    return config
    
def get_config(section=None, option=None, **kwargs):
    
    config = get_configparser()
    
    if section is None and option is None:
        return config
        
    if section is None:
        raise ValueError('Section to Query must be defined!')
        
    if section.lower() == 'rules':
        return get_rules()
    
    try:
        result = config.items(section)
    except configparser.NoSectionError:
        log.exception('no %s section in configuration file', section.upper())
        
    if option is None:
        return result
        
    try:
        result = config.get(section, option)
    except configparser.NoOptionError:
        if 'default' in kwargs:
            log.warn('no %s %s specified in configuration file, set default %s', section, option, str(kwargs['default']))
            
            result = kwargs['default']
        else:
            log.exception('no %s %s specified in configuration file', section, option)
            
    # Change Type of Result
    try:
        if 'type' in kwargs: # set type explicit
            type_kw = kwargs['type']
        else:
            if 'default' in kwargs:
                type_kw = type(kwargs['default'])
                
                result = type_kw(result)
    except:
        log.exception('%s %s setting invalid - not %s', section, option, kwargs['type'])
        
    return result

def get_rules(rule=None, option=None, **kwargs):
    
    config = get_configparser()
    
    # dictionary with rules in Configfile
    rules = {
             # predefined rules
             'debug' : { 'subject':'DEBUG', 'priority':'1' },
             'info' : { 'subject':'INFO', 'priority':'2' },
             'warning' : { 'subject':'WARNING', 'priority':'3' },
             'critical' : { 'subject':'CRITICAL', 'priority':'4' },
             'error' : { 'subject':'ERROR', 'priority':'5' },
             'fatal' : { 'subject':'FATAL', 'priority':'6' },
            }
    
    # Find sections with 'rules.name'
    for section in config.sections():
        
        sid = section.split('.')
        
        if sid[0].lower() != 'rules':
            continue
            
        if len(sid) != 2:
            log.exception('invalid rule section - must be e.g. rules.name')
            
        sid_rule = sid[1].lower()
        
        # update rule options, if there are
        # options already predefined like above,
        # else update new empty dict.
        
        new_rule = rules.get(sid_rule, {})
        
        new_rule.update(dict(config.items(section)))
        
        rules[sid_rule] = new_rule
        
    if rule is None and option is None:
        return rules
        
    if rule is None:
        raise ValueError('Rule to Query must be defined!')
        
    rule = rule.lower()
    
    if option is None:
        
        if rule not in rules:
            log.critical('no rule %s specified in configuration file', rule.upper())
            
            return dict()
            
        return rules[rule.lower()]
        
    option = option.lower()
    
    if rule not in rules:
        log.exception('no rule %s specified in configuration file', rule.upper())
        
    options = rules[rule]
    
    if option not in options:
        log.exception('option %s not defined in rule %s', option.upper(), rule.upper())
        
    return options[option]
    