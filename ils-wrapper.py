#!/usr/bin/env python3

from argparse import ArgumentParser
import re
import subprocess
import sys
from threading import Thread

class ANSIColor:
    red = '\x1b[31m'
    green = '\x1b[32m'
    yellow = '\x1b[33m'
    brightblue = '\x1b[34;1m' 
    blue = '\x1b[34m'
    normal = '\x1b[0m'

class OutputProcessor(Thread):

    def __init__(self,output,output_name,options):
        self._output = output
        self._output_name = output_name
        self._options = options
        self._long1_regexp = re.compile("^(\s{2}\S+\s+)(\d+\s)(\S+\s+)(\d+\s+)(\d{4}\-\d{2}\-\d{2}\.\d{2}:\d{2}\s)(\&?\s+)([\S[\S\s]+)$")
        self._long2_regexp = re.compile("(\s{8}\S+)(\s+\/[\S\s]+)")
        Thread.__init__(self)
        self.start()

    def print_color(self,colorcode,message,line=True):
        if line:
          print(colorcode,message,ANSIColor.normal)
        else:
          print("B",colorcode,"M",message,"M",ANSIColor.normal,"E",end='')

    def process_line(self,line):
        if self._output_name == 'stdout':
            line_string = line.decode(sys.stdout.encoding).rstrip()
            match_long1 = self._long1_regexp.match(line_string)
            match_long2 = self._long2_regexp.match(line_string)
            if re.match("^\/",line_string):
                print(line_string,)
            elif self._options.A and re.match("^\s+(ACL|Inheritance)\s",line_string):
                self.print_color(ANSIColor.yellow,line_string)
            elif match_long1 and ( self._options.l or self._options.L):
                g=match_long1.groups()
                # FIXME: alignment is bad
                self.print_color(ANSIColor.blue,g[0],line=False)
                self.print_color(ANSIColor.brightblue,g[1],line=False)
                self.print_color(ANSIColor.blue,g[2],line=False)
                self.print_color(ANSIColor.brightblue,g[3],line=False)
                self.print_color(ANSIColor.blue,g[4],line=False)
                self.print_color(ANSIColor.brightblue,g[5],line=False)
                self.print_color(ANSIColor.blue,g[6])
                print()
            elif match_long2 and self._options.L:
                g=match_long2.groups()
                # FIXME: alignment is bad
                self.print_color(ANSIColor.blue,g[0],line=False)
                self.print_color(ANSIColor.brightblue,g[1],line=False)
                print()
            elif re.match("^\s{2}[CD]\S\s+\/",line_string):
                self.print_color(ANSIColor.blue,line_string)
            elif re.match("^\s{2}\S",line_string):
                self.print_color(ANSIColor.green,line_string)
            else:
                print(line_string,)
        elif self._output_name == 'stderr':
            line_string = line.decode(sys.stderr.encoding)
            self.print_color(ANSIColor.red,line_string)

    def run(self):
        while True:
            line=self._output.readline()
            if not line:
                break
            self.process_line(line)

def get_options():
    parser = ArgumentParser(add_help=False)
    parser.add_argument('-l',action='store_true')
    parser.add_argument('-L',action='store_true')
    parser.add_argument('-A',action='store_true')
    # Need to explicitly define all short options, even if the wrapper
    # ignores them, otherwise argparse will fail on combined short
    # options (e.g. "-LAr").
    parser.add_argument('-r',action='store_true')
    parser.add_argument('-t',action='store_true')
    parser.add_argument('-v',action='store_true')
    parser.add_argument('-V',action='store_true')
    parser.add_argument('-h',action='store_true')
    options , args = parser.parse_known_args()
    return options

def execute_ils(args):
    ils_arguments = sys.argv
    ils_arguments[0] = "ils" 
    ils_process = subprocess.Popen(ils_arguments , stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout_processor = OutputProcessor(ils_process.stdout,"stdout",args)
    stderr_processor = OutputProcessor(ils_process.stderr,"stderr",args)

    stdout_processor.join()
    stderr_processor.join()

    ils_process.stdout.close()
    ils_process.stderr.close()

# Main

options = get_options()
execute_ils(options)
