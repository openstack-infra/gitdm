#
# Pull together regular expressions used in multiple places.
#
# This code is part of the LWN git data miner.
#
# Copyright 2007-8 LWN.net
# Copyright 2007-8 Jonathan Corbet <corbet@lwn.net>
#
# This file may be distributed under the terms of the GNU General
# Public License, version 2.
#
import re

#
# Some people, when confronted with a problem, think "I know, I'll use regular
# expressions." Now they have two problems.
#    -- Jamie Zawinski
#
Pemail = r'\s+"?([^<"]+)"?\s<([^>]+)>' # just email addr + name
Pcommit = re.compile (r'^commit ([0-9a-f ]+)$')
Pauthor = re.compile (r'^Author:' + Pemail + '$')
Psob = re.compile (r'Signed-off-by:' + Pemail)
Pmerge = re.compile (r'^Merge:.*$')
Padd = re.compile (r'^\+[^\+].*$')
Prem = re.compile (r'^-[^-].*$')
Pdate = re.compile (r'^(Commit)?Date:\s+(.*)$')
Pfilea = re.compile (r'^---\s+(.*)$')
Pfileb = re.compile (r'^\+\+\+\s+(.*)$')
Preview = re.compile (r'Reviewed-by:' + Pemail)
Ptest = re.compile (r' tested-by:' + Pemail, re.I)
Prep = re.compile (r'Reported-by:' + Pemail)
Preptest = re.compile (r'reported-and-tested-by:' + Pemail, re.I)
#
# Merges are described with a variety of lines.
#
PExtMerge = re.compile(r'^ +Merge( branch .* of)? ([^ ]+:[^ ]+)\n$')
PIntMerge = re.compile(r'^ +(Merge|Pull) .* into .*$')
PIntMerge2 = re.compile(r"^ +Merge branch(es)? '.*$")
