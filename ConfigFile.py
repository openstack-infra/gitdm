#
# Stuff for dealing with configuration files.
#
#
# This code is part of the LWN git data miner.
#
# Copyright 2007-11 Eklektix, Inc.
# Copyright 2007-11 Jonathan Corbet <corbet@lwn.net>
#
# This file may be distributed under the terms of the GNU General
# Public License, version 2.
#
import sys, re, datetime, os.path
import database

class ReadConfigLine:
    """
        ReadConfigLine provides a iterator to extract line
        from an config file without comments.

        Typical use case:

            fd = open(filename, 'r')
            for line in ReadConfigLine(fd):
                parse_line(line)
            fd.close(fd)
    """

    def __init__(self, fd):
        self.fd = fd
        self.buffer = None
        self.patch = []

    def __iter__(self):
        return self

    def next(self):
        line = self.fd.readline()
        while line:
            line = line.split('#')[0] # Get rid of any comments
            line = line.strip()       # and extra white space
            if len(line) == 0:       # we got rid of everything
                line = self.fd.readline()
            else:
                break

        if not line:
            raise StopIteration

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
        fd = open (name, 'r')
    except IOError:
        croak ('Unable to open email alias file %s' % (name))

    for line in ReadConfigLine (fd):
        m = re.match ('^("[^"]+"|\S+)\s+(.+)$', line)
        if not m or len (m.groups ()) != 2:
            croak ('Funky email alias line "%s"' % (line))
        if m and m.group (2).find ('@') <= 0:
            croak ('Non-addresses in email alias "%s"' % (line))
        database.AddEmailAlias (m.group (1).replace ('"', ''), m.group (2))
 
    fd.close ()

#
# The Email/Employer map
#
EMMpat = re.compile (r'^([^\s]+)\s+([^<]+)\s*(<\s*(\d+-\d+-\d+)\s*)?$')

def ReadEmailEmployers (name):
    try:
        fd = open (name, 'r')
    except IOError:
        croak ('Unable to open email/employer file %s' % (name))

    for line in ReadConfigLine (fd):
        m = EMMpat.match (line)
        if not m:
            croak ('Funky email/employer line "%s"' % (line))
        email = m.group (1)
        company = m.group (2).strip ()
        enddate = ParseDate (m.group (4))
        database.AddEmailEmployerMapping (email, company, enddate)
 
    fd.close ()

def ParseDate (cdate):
    if not cdate:
        return None
    sdate = cdate.split ('-')
    return datetime.date (int (sdate[0]), int (sdate[1]), int (sdate[2]))


def ReadGroupMap (fname, employer):
    try:
        fd = open (fname, 'r')
    except IOError:
        croak ('Unable to open group map file %s' % (fname))

    for line in ReadConfigLine (fd):
        database.AddEmailEmployerMapping (line, employer)

    fd.close ()

#
# Read in a virtual employer description.
#
def ReadVirtual (fd, name):
    ve = database.VirtualEmployer (name)

    for line in ReadConfigLine (fd):
        sl = line.split (None, 1)
        first = sl[0]
        if first == 'end':
            ve.store ()
            return
        #
        # Zap the "%" syntactic sugar if it's there
        #
        if first[-1] == '%':
            first = first[:-1]
        try:
            percent = int (first)
        except ValueError:
            croak ('Bad split value "%s" for virtual empl %s' % (first, name))
        if not (0 < percent <= 100):
            croak ('Bad split value "%s" for virtual empl %s' % (first, name))
        ve.addsplit (' '.join (sl[1:]), percent/100.0)
    #
    # We should never get here
    #
    croak ('Missing "end" line for virtual employer %s' % (name))

#
# Read file type patterns for more fine graned reports
#
def ReadFileType (filename):
    try:
        fd = open (filename, 'r')
    except IOError:
        croak ('Unable to open file type mapping file %s' % (filename))
    patterns = {}
    order = []
    regex_order = re.compile ('^order\s+(.*)$')
    regex_file_type = re.compile ('^filetype\s+(\S+)\s+(.+)$')

    for line in ReadConfigLine (fd):
        o = regex_order.match (line)
        if o:
            # Consider only the first definition in the config file
            elements = o.group(1).replace (' ', '')
            order = order or elements.split(',')
            continue

        m = regex_file_type.match (line)
        if not m or len (m.groups ()) != 2:
            ConfigFile.croak ('Funky file type line "%s"' % (line))
        if not patterns.has_key (m.group (1)):
            patterns[m.group (1)] = []
        if m.group (1) not in order:
            print '%s not found, appended to the last order' % m.group (1)
            order.append (m.group (1))

        patterns[m.group (1)].append (re.compile (m.group (2), re.IGNORECASE))

    fd.close ()
    return patterns, order

#
# Read an overall config file.
#

def ConfigFile (name, confdir):
    try:
        fd = open (name, 'r')
    except IOError:
        croak ('Unable to open config file %s' % (name))

    for line in ReadConfigLine (fd):
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
        elif sline[0] == 'VirtualEmployer':
            ReadVirtual (file, ' '.join (sline[1:]))
        elif sline[0] == 'FileTypeMap':
            patterns, order = ReadFileType (os.path.join (confdir, sline[1]))
            database.FileTypes = database.FileType (patterns, order)
        else:
            croak ('Unrecognized config line: "%s"' % (line))


if __name__ == '__main__':
    '''Test the iterato for reading configuration files'''
    try:
        fd = open(sys.argv[1])
    except:
        croak('Usage: %s <config-file>' % sys.argv[0])
    
    for line in ReadConfigLine(fd):
        print line
        
