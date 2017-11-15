## Config file for test
### Copy TV Murex File Job

import string

#configuration for Murex copy job
sourcefiletemplate = string.Template(r"\\ldnroot\data\FIRC\DATA\LDN\IRD\BROIL\PROD\CVA\_Dynamic\${YYYYMMDD}\Inputs\TVs\Murex\MUREX_TVS_${YYYYMMDD}.txt")
destinationdir = r"\\Zurroot\Data\FIRC\data\ZUR\FX-CCT\fxglobal\FXCCTRiskBM\STIR BM\Counterparty exposure\Credit Radar\FX Credit risk\MurexTransformer\Input"
logname = "test"
logfolder = "."