from __future__ import print_function

import os, sys
import logging
from configparser import ConfigParser

class IniConfigurator():

	def __init__(self, configfilepath):
		"""Provide dictionary with global variables provided in ini file.
		Provide path to ini file to instantiate the Configurator.
		Global provides all values in a dict.
		ConfigSectionMap allows to retreive the values for the sections."""
		self.Config = ConfigParser()
		self.Config.optionxform = str
		self.Config.read(configfilepath)
		self.globals = self.__configureNodes()

	def __configureNodes(self):
		"""Returns a dictionary with all variables from ini file"""
		"Load all configuration values into an easy to use dict"""
		mydict = {}
		sections = self.Config.sections()
		print("Configuring nodes for config sections {}".format(sections))
		for section in sections:
		   mydict = dict(mydict.items() +  self.Config.items(section))
		return mydict


	def ConfigSectionMap(self,section):
		"""When given a config file section, returns a dictionary with all variables defined in ini file"""
		dict1 = {}
		options = self.Config.options(section)
		for option in options:
			try:
				dict1[option] = self.Config.get(section, option)
				if dict1[option] == -1:
					print ("skip: %s" % option)
			except:
				print("exception on %s!" % option)
				dict1[option] = None
		return dict1
