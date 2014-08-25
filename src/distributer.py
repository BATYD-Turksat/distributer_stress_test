#!/usr/local/bin/python
# encoding: utf-8
'''
distributer -- Distibute the watch ids to launcher service

distributer is a description

It defines classes_and_methods

@author:     Ergin Ozekes

@copyright:  2014 Turksat. All rights reserved.

@license:    license

@contact:    eozekes@turksat.com.tr
@deffield    updated: Updated
'''

import sys
import os
import collectorOfWatchIds

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2014-08-21'
__updated__ = '2014-08-21'

global_watch_list = None
last_processed_watch_index=0
global_server_list = None

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Ergin Ozekes on %s.
  Copyright 2014 Turksat. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-u", "--url", dest="url", help="url to download. [default: %(default)s]", metavar="url" )
        parser.add_argument("-d", "--dsv", dest="dsrv", help="distributed servers. [default: %(default)s]", metavar="url", nargs="+" )
        parser.add_argument('-V', '--version', action='version', version=program_version_message)

        # Process arguments
        args = parser.parse_args()

        url = args.url
        dservers = args.dsrv
        global_server_list=dservers[0].split(',')
        
        if url == "":
            raise CLIError("url is not defined.")
        
        if dservers == None and len(dservers) == 0:
            raise CLIError("distribution servers not defined.")

        print 'url: ',url
        print 'distrubition servers: ',dservers
        
        ### do something with inpath ###
        return collectorOfWatchIds.processUrl(url,global_watch_list,last_processed_watch_index,global_server_list)
    
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    sys.exit(main())