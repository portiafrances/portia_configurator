## Config file for test
import string

#configuration for Murex copy job
sourcefiletemplate = string.Template(r"\\MYDIRTEST\mysubdir_${YYYYMMDD}.txt")
destinationdir = r"myotherdir"
logname = "test"
logfolder = "."