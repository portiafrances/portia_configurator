############## Configurator for command line programs
# 2016 Portia Frances Limited
# Author: Thomas Haederle

import logging
logger = logging.getLogger(__name__)

import os, sys
from datetime import datetime, timedelta 
import argparse
import tempfile

from nmrfengine.utils.ui import ArgparseUi

class Configurator:
    """Standard class to configure command line applications.
    
    Usage:
    Instantiate a configurator class.
    For your app add argsparse items to configurator.parser
    e.g.
    configurator = Configurator()
    configurator.parser.add_argument("-d", "--cobdate", help="Cobdate for which the report is created. Format is YYYYMMDD, e.g. 20151130. Default is today.", default=str(today))
    
    At runtime show the GUI and/or return the command line parameters by calling configureCommandline.
    Finally, to set up the application, call setupAppconfig.
    In the commandline application use configurator.setupAppconfig to drive the application.
    
    The application can be configured with 
    appconfig = configurator.configureApp()
    """

    def __init__(self, description="Configures the app from the command line"):
        """
        Input: 
        description    Message which is shown if the configuration dialog is invoked using the -help dialog
        
        Output:
        Configurator object which holds appconfig defintion
        """
        self.description = description
        self.parser = argparse.ArgumentParser(self.description)
        self.appconfig = lambda: None #emptyish object  http://stackoverflow.com/questions/19476816/creating-an-empty-object-in-python
        self.commandconfig = None
        self.createStandardOptions()
        
    def createStandardOptions(self):
        """Set command line options needed for almost every application, such as rundate, cobdate and logging options"""
        
        def prev_weekday(adate):
            adate -= timedelta(days=1)
            while adate.weekday() > 4: # Mon-Fri are 0-4
                adate -= timedelta(days=1)
            return adate
        
        self.appconfig.rundate = str(datetime.strftime(datetime.today(), '%Y%m%d'))
        self.appconfig.cobdate = str(datetime.strftime(prev_weekday(datetime.today()), '%Y%m%d')) # previous weekday day as default
        self.parser.add_argument("-rd", "--rundate", help="date for which the report is run", default=str(self.appconfig.rundate))
        self.parser.add_argument("-d", "--cobdate", help="Cobdate for which the report is copied. Format is YYYYMMDD, e.g. 20151130. Default is previous business day.", default=str(self.appconfig.cobdate))
        self.parser.add_argument("-g", "--gui", help="Show configuration GUI", action="store_true")
        self.parser.add_argument("-m", "--mode", help="Runmode. Can be 'prod' or 'test'. Prod uses config_prod and test uses config_test. Default is 'test'", choices=['prod', 'test'], default="test")
        self.parser.add_argument("-c", "--configfile", help="Path to the config file to be used. Will be used inst4ead of config_prod.py or config_test.py")
        self.parser.add_argument("-ll", "--loglevel", help="Loglevel - what severity is shown in log. Use 'ERROR' = 40, 'WARNING'=30, 'INFO'=20, 'DEBUG'=10. ", choices=[40, 30, 20, 10]  )
        self.parser.add_argument("-lf", "--logformat", help="Logformat - how to show logging", default='%(asctime)-15s - %(thread)-10d - %(threadName)-12s - %(name)-25s - %(funcName)-25s - %(levelname)-5s - %(message)s' )
        self.parser.add_argument("-ldir", "--logfolder", help="Logfolder - path to where logfile is written to. Default is temp directory.", default = tempfile.gettempdir() )
        self.parser.add_argument("-ln", "--logname", help="Logname - Name of the log." )
        self.parser.add_argument("-em", "--email", help="Send notification email", action="store_true")
        self.parser.add_argument("-se", "--sender", help="email sender, e.g. dada@ubs.com")
        self.parser.add_argument("-dist", "--distributionlist", help="email distributionlist as list, e.g. ['lala@ubs.com', 'dudu@ubs.com']")
        self.parser.add_argument("-errlist", "--error_distributionlist", help="error email distributionlist as list, e.g. ['lala@ubs.com', 'dudu@ubs.com']")
        self.parser.add_argument("-casrd", "--cobdateasrundate", help="if flag is set then cobdate is set to rundate, e.g. when the data is processed on the same day", action="store_true")

        
    def configureCommandline(self):
        """
        Parses the arguments in the configurator.parser.
        If the Gui is enabled, it shows the args parse gui.
        Input:
        configurator.parser
        
        Output:
        configurator.commandconfig
        """
        
        args = self.parser.parse_args() #parse arguments from command line
        
        def buildgui(args):
            if args.gui:
                try:
                    from PyQt5 import QtGui, QtWidgets
                    app = QtWidgets.QApplication(sys.argv)
                except ImportError:
                    print("Could not import PyQT5, trying PyQT4...")
                    try: 
                        from PyQt4 import QtGui
                        app = QtGui.QApplication(sys.argv)
                    except ImportError:
                        print("Could not import PyQt4, trying command line interface instead.")
                try:
                    a = ArgparseUi(self.parser)
                    a.show()
                    app.exec_()
                    print ("Ok" if a.result() == 1 else "Cancel")
                    if a.result() == 1: # Ok pressed 
                        parsed_args = a.parse_args()
                    else:    
                        parsed_args = None
                        sys.exit()
                    print ("GUI args: {}".format(parsed_args))
                    return parsed_args #overwrite args with values from GUI
                except Exception as e:
                    print("Could not create GUI. Failed with error: {}".format(e))
                    print("Run the program without the -g flag and use the command line interface.")
                    raise

        if args.gui:
            args = buildgui(args)
            
        print("Command line config:")
        commandconfig = {key: item for key, item in vars(args).items() if item is not None}
        logger.info("Custom Configuration")
        for key, item in commandconfig.items():
            #logger.info(key, item)
            if key == "password":
                print(key, "****")
            else:
                print(key, item)
            
        if 'cobdateasrundate' in commandconfig:
            if commandconfig['cobdateasrundate']:
                logger.info("OVERWRITE! Cobdate as Rundate flag set ('cobdateasrundate'). Setting Cobdate to Rundate!")
                commandconfig["cobdate"] = commandconfig["rundate"]
                print("WARNING: cobdateasrundate flag was set. COBDATE OVERWRITE. Cobdate is now {} ".format(commandconfig["cobdate"] ))
                logger.info("Cobdate is now: {}".format(commandconfig["cobdate"]))
                
        self.commandconfig = commandconfig
        
    def setupAppconfig(self):
        """Populates appconfig from file and overwrites with custom configurations from commandconfig.
        Otherwise populates parameters from test_config.py or prod_config.py, depending on run mode.
        
        """
        
        #Logger does not work at this point. Hence print is used.
        
        if not self.commandconfig:
            self.configureCommandline()  # create commandconfig if not exists
        
        #config prod or test or custom config
        if "configfile" in self.commandconfig:
            #import pdb;pdb.set_trace();
            #logger.info("Configuration file: {}".format(self.commandconfig["configfile"]))
            print("Configuration file: {}".format(self.commandconfig["configfile"]))
            configfile = self.commandconfig["configfile"] 
            
            #if config file contains a path, add that path to the python path to allow import of the file
            configpath, file  = os.path.split(configfile)
                        
            if os.path.isdir(configpath):
                sys.path.append(configpath)
            elif configpath == '':
                configpath = os.getcwd()
            else:
                logger.error("Configfile is not on a valid path. {} is not a directory.".format(configpath))
                raise
                
            #logger.debug("Configpath is: {}".format(configpath))
            print("Configpath is: {}".format(configpath))
            
            #if file has an extension, e.g. .py, split it
            configfile, ext = os.path.splitext(file)
            
        else:
            configfile = "".join(["config_",self.commandconfig["mode"]])
        #logger.info("Configuration file: {}".format(configfile))
        print("Configuration file: {}".format(configfile))
        
        
        #dynamically load different configuration files based on run mode
        try:
            self.appconfig = __import__(configfile, level=0 ) # global configuration object to hold config file settings
            #logger.info(self.appconfig)
            print(self.appconfig)
        except Exception as e:
            #logger.error("Did not import configuration file {}.".format(configfile))
            #logger.warning("Trying to import config_test")
            print("Did not import configuration file {}.".format(configfile))
            print("Trying to import config_test")
            try:
                self.appconfig = __import__("config_test", level=0 )
            except Exception as e:
                #logger.warning("Did not load any config files. Configuration from commandline only.")
                print("Did not load any config files. Configuration from commandline only.")
            
        #logger.info("Overwrite chosen configuration file with custom config from command line.")
        print("Overwrite chosen configuration file with custom config from command line.")
        for key, item in self.commandconfig.items():
            #logger.info("Value Overwrite: {}\t{}".format(key, item))
            if not key == "password":
                print("Value Overwrite: {}\t{}".format(key, item))
            else:
                print("Value Overwrite: {}\t{}".format(key, "******"))
            setattr(self.appconfig, key, item) # overwrite the items in the config file with values from the command line
        
        #logger.info("Configuration for this run:")
        print("Configuration for this run:")
        #[logger.info("Value: {}\t{}".format(key, getattr(self.appconfig, key))) for key in dir(self.appconfig)  if "__" not in key]
        [print("Value: {}\t{}".format(key, getattr(self.appconfig, key))) for key in dir(self.appconfig)  if ("__" not in key) and ("password" not in key)]
        
    def setupLogger(self, filelogging=True):
        """Configures logging with values from appconfig. Sets loglevel, logformat and filelogging.
        
        Inputs:
        Boolean Filelogging:    If logger should also log to file. If no logfolder is given in config or commandline, logs to temp directory."""
        
        # if not self.appconfig:
            # self.setupAppconfig()  # create commandconfig if not exists
        #logging standard options
        if not hasattr(self.appconfig, "loglevel"):
            self.appconfig.loglevel = 10 #default to debug mode
        if not hasattr( self.appconfig, "logformat") :    
            self.appconfig.logformat='%(asctime)-15s - %(name)-20s - %(funcName)-20s %(levelname)-5s - %(message)s' #default format
        if not hasattr(self.appconfig, "logfolder"):
            self.appconfig.logfolder = tempfile.gettempdir() #default logdir
        if not hasattr(self.appconfig, "logname"):
            #import pdb; pdb.set_trace()
            try:
                *_, appname = os.path.split(sys.argv[0])
                self.appconfig.logname = appname
            except Exception as e:
                self.appconfig.logname = __name__  #default logname
            print("Logname is {}".format(self.appconfig.logname))
       
        logging.basicConfig(level=self.appconfig.loglevel, format = self.appconfig.logformat)
        rootlogger = logging.getLogger()
        rootlogger.setLevel(self.appconfig.loglevel)
        if filelogging:
            try:
                fileloggername = os.path.join(self.appconfig.logfolder, "_".join([self.appconfig.rundate, self.appconfig.logname + ".log"]))
                formatter = logging.Formatter(self.appconfig.logformat)
                fh = logging.FileHandler(fileloggername)
                fh.setFormatter(formatter)
                rootlogger.addHandler(fh)
                logger.info("Logging to file: {}".format(fileloggername))
            except Exception as e:
                logger.warning("Could not create filelogger. Proceeding without filelogger. Error: {}".format(e))
        return rootlogger
        
    def configureApp(self, setuplogger=True,  filelogging=True):
        """Configures the app from command line and config files and logger and returns appconfig."""
        print("##################### Start Configuration #####################")
        self.configureCommandline()    
        self.setupAppconfig()
        if setuplogger:
            self.setupLogger(filelogging=filelogging)
        print("##################### End Configuration #####################")
        return self.appconfig

        
if __name__ == "__main__":
    conf = Configurator("Running configurator module")
    conf.configureApp(filelogging=False)
    