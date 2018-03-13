'''
Created on Jan 29, 2018
'''
import sys
import os,signal
from os.path import join
import argparse
import logging
import logging.config
import configparser

class Config(object):
    '''
    Configuration database for RIAPS tools
    Including logging configuration
    '''

    #grafana Setup
    INFLUX_DBASE_HOST='192.168.10.121'
    INFLUX_DBASE_PORT=8086
    INFLUX_DBASE_USER='riaps'
    INFLUX_DBASE_PASSWORD = 'riaps'
    INFLUX_DBASE_NAME = 'EnergyMarket'

    GRIDLAB_D_TIMEBASE="2000-01-01"
    START_INTERVAL = 28 # starting time interval for the components


    def __init__(self):
        '''
        Constructor
        '''
        pass
