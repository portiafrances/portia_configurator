############## Configurator for command line programs
#### tests
# 2016 Portia Frances Limited for UBS
# Author: Thomas Haederle


import logging
logger = logging.getLogger(__name__)

import pytest
#from nose.tools import *
from configurator import Configurator

def test_configurator_initialize():
    conf = Configurator("This is a test")
    assert conf.description == "This is a test"
    
def test_configurator_standardparse():    
    conf = Configurator()
    args = conf.parser.parse_args()
    print(args)
    assert args.cobdate
    assert args.rundate
    assert args.mode

def test_configurator_commandconfig():    
    conf = Configurator()
    assert conf.commandconfig  is None
    args = conf.configureCommandline()
    assert conf.commandconfig
    
def test_configurator_setupAppconfig():    
    conf = Configurator()
    #assert conf.appconfig is None
    args = conf.setupAppconfig()
    assert conf.appconfig

def test_configurator_setuplogger():    
    conf = Configurator()
    rootlogger = conf.setupLogger()
    assert type(rootlogger) == logging.RootLogger #is returned logger of type rootlogger
    
def test_cobdate():
    conf = Configurator()
    args = conf.configureCommandline()
    assert conf.commandconfig["cobdate"]
    assert conf.commandconfig["rundate"]

    
def test_cobdate():
    conf = Configurator()
    args = conf.setupAppconfig()
    assert conf.appconfig.cobdate
    assert conf.appconfig.rundate