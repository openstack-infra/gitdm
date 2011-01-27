#
# Stuff for dealing with configuration files.
#
#
# This code is part of the LWN git data miner.
#
# Copyright 2007-10 LWN.net
# Copyright 2007-10 Jonathan Corbet <corbet@lwn.net>
#
# This file may be distributed under the terms of the GNU General
# Public License, version 2.
#
import sys, re, datetime, os.path
import database

#
# Read a line and strip out junk.
#
def ReadConfigLine (file):
    line = file.readline ()
    if not line:
        return None
    line = line.split('#')[0] # Get rid of any comments
    line = line.strip () # and extra white space
    if len (line) == 0: # we got rid of everything
        return ReadConfigLine (file)
    return line

#
# Give up and die.
#
def croak (message):
    sys.stderr.write (message + '\n')
    sys.exit (1)

#
# Read a list of email aliases.
#
def ReadEmailAliases (name):
    try:
        file = open (name, 'r')
    except IOError:
        croak ('Unable to open email alias file %s' % (name))
    line = ReadConfigLine (file)
    while line:
        m = re.match ('^("[^"]+"|\S+)\s+(.+)$', line)
        if not m or len (m.groups ()) != 2:
            croak ('Funky email alias line "%s"' % (line))
        if m and m.group (2).find ('@') <= 0:
            croak ('Non-addresses in email alias "%s"' % (line))
        database.AddEmailAlias (m.group (1).replace ('"', ''), m.group (2))
        line = ReadConfigLine (file)
    file.close ()

#
# The Email/Employer map
#
EMMpat = re.compile (r'^([^\s]+)\s+([^<]+)\s*(<\s*(\d+-\d+-\d+)\s*)?$')

def ReadEmailEmployers (name):
    try:
        file = open (name, 'r')
    except IOError:
        croak ('Unable to open email/employer file %s' % (name))
    line = ReadConfigLine (file)
    while line:
        m = EMMpat.match (line)
        if not m:
            croak ('Funky email/employer line "%s"' % (line))
        email = m.group (1)
        company = m.group (2).strip ()
        enddate = ParseDate (m.group (4))
        database.AddEmailEmployerMapping (email, company, enddate)
        line = ReadConfigLine (file)
    file.close ()

def ParseDate (cdate):
    if not cdate:
        return None
    sdate = cdate.split ('-')
    return datetime.date (int (sdate[0]), int (sdate[1]), int (sdate[2]))


def ReadGroupMap (fname, employer):
    try:
        file = open (fname, 'r')
    except IOError:
        croak ('Unable to open group map file %s' % (fname))
    line = ReadConfigLine (file)
    while line:
        database.AddEmailEmployerMapping (line, employer)
        line = ReadConfigLine (file)
    file.close ()

#
# Read an overall config file.
#

def ConfigFile (name, confdir):
    try:
        file = open (name, 'r')
    except IOError:
        croak ('Unable to open config file %s' % (name))
    line = ReadConfigLine (file)
    while line:
        sline = line.split (None, 2)
        if len (sline) < 2:
            croak ('Funky config line: "%s"' % (line))
        if sline[0] == 'EmailAliases':
            ReadEmailAliases (os.path.join (confdir, sline[1]))
        elif sline[0] == 'EmailMap':
            ReadEmailEmployers (os.path.join (confdir, sline[1]))
        elif sline[0] == 'GroupMap':
            if len (sline) != 3:
                croak ('Funky group map line "%s"' % (line))
            ReadGroupMap (os.path.join (confdir, sline[1]), sline[2])
        else:
            croak ('Unrecognized config line: "%s"' % (line))
        line = ReadConfigLine (file)
        
