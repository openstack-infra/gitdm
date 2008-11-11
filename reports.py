#
# A new home for the reporting code.
#

import sys

Outfile = sys.stdout
HTMLfile = None
ListCount = 999999


def SetOutput (file):
    global Outfile
    Outfile = file

def SetHTMLOutput (file):
    global HTMLfile
    HTMLfile = file

def SetMaxList (max):
    global ListCount
    ListCount = max


def Write (stuff):
    Outfile.write (stuff)



#
# HTML output support stuff.
#
HTMLclass = 0
HClasses = ['Even', 'Odd']

THead = '''<p>
<table cellspacing=3>
<tr><th colspan=3>%s</th></tr>
'''

def BeginReport (title):
    global HTMLclass
    
    Outfile.write ('\n%s\n' % title)
    if HTMLfile:
        HTMLfile.write (THead % title)
        HTMLclass = 0

TRow = '''    <tr class="%s">
<td>%s</td><td align="right">%d</td><td align="right">%.1f%%</td></tr>
'''

def ReportLine (text, count, pct):
    global HTMLclass
    if count == 0:
        return
    Outfile.write ('%-25s %4d (%.1f%%)\n' % (text, count, pct))
    if HTMLfile:
        HTMLfile.write (TRow % (HClasses[HTMLclass], text, count, pct))
        HTMLclass ^= 1

def EndReport ():
    if HTMLfile:
        HTMLfile.write ('</table>\n\n')
        
#
# Comparison and report generation functions.
#
def ComparePCount (h1, h2):
    return len (h2.patches) - len (h1.patches)

def ReportByPCount (hlist, cscount):
    hlist.sort (ComparePCount)
    count = 0
    BeginReport ('Developers with the most changesets')
    for h in hlist:
        pcount = len (h.patches)
        changed = max(h.added, h.removed)
        delta = h.added - h.removed
        if pcount > 0:
            ReportLine (h.name, pcount, (pcount*100.0)/cscount)
        count += 1
        if count >= ListCount:
            break
    EndReport ()
            
def CompareLChanged (h1, h2):
    return max(h2.added, h2.removed) - max(h1.added, h1.removed)

def ReportByLChanged (hlist, totalchanged):
    hlist.sort (CompareLChanged)
    count = 0
    BeginReport ('Developers with the most changed lines')
    for h in hlist:
        pcount = len (h.patches)
        changed = max(h.added, h.removed)
        delta = h.added - h.removed
        if (h.added + h.removed) > 0:
            ReportLine (h.name, changed, (changed*100.0)/totalchanged)
        count += 1
        if count >= ListCount:
            break
    EndReport ()
            
def CompareLRemoved (h1, h2):
    return (h2.removed - h2.added) - (h1.removed - h1.added)

def ReportByLRemoved (hlist, totalremoved):
    hlist.sort (CompareLRemoved)
    count = 0
    BeginReport ('Developers with the most lines removed')
    for h in hlist:
        pcount = len (h.patches)
        changed = max(h.added, h.removed)
        delta = h.added - h.removed
        if delta < 0:
            ReportLine (h.name, -delta, (-delta*100.0)/totalremoved)
        count += 1
        if count >= ListCount:
            break
    EndReport ()

def CompareEPCount (e1, e2):
    return e2.count - e1.count

def ReportByPCEmpl (elist, cscount):
    elist.sort (CompareEPCount)
    count = 0
    BeginReport ('Top changeset contributors by employer')
    for e in elist:
        if e.count != 0:
            ReportLine (e.name, e.count, (e.count*100.0)/cscount)
        count += 1
        if count >= ListCount:
            break
    EndReport ()



def CompareELChanged (e1, e2):
    return e2.changed - e1.changed

def ReportByELChanged (elist, totalchanged):
    elist.sort (CompareELChanged)
    count = 0
    BeginReport ('Top lines changed by employer')
    for e in elist:
        if e.changed != 0:
            ReportLine (e.name, e.changed, (e.changed*100.0)/totalchanged)
        count += 1
        if count >= ListCount:
            break
    EndReport ()



def CompareSOBs (h1, h2):
    return len (h2.signoffs) - len (h1.signoffs)

def ReportBySOBs (hlist):
    hlist.sort (CompareSOBs)
    totalsobs = 0
    for h in hlist:
        totalsobs += len (h.signoffs)
    count = 0
    BeginReport ('Developers with the most signoffs (total %d)' % totalsobs)
    for h in hlist:
        scount = len (h.signoffs)
        if scount > 0:
            ReportLine (h.name, scount, (scount*100.0)/totalsobs)
        count += 1
        if count >= ListCount:
            break
    EndReport ()

#
# Reviewer reporting.
#
def CompareRevs (h1, h2):
    return len (h2.reviews) - len (h1.reviews)

def ReportByRevs (hlist):
    hlist.sort (CompareRevs)
    totalrevs = 0
    for h in hlist:
        totalrevs += len (h.reviews)
    count = 0
    BeginReport ('Developers with the most reviews (total %d)' % totalrevs)
    for h in hlist:
        scount = len (h.reviews)
        if scount > 0:
            ReportLine (h.name, scount, (scount*100.0)/totalrevs)
        count += 1
        if count >= ListCount:
            break
    EndReport ()

#
# tester reporting.
#
def CompareTests (h1, h2):
    return len (h2.tested) - len (h1.tested)

def ReportByTests (hlist):
    hlist.sort (CompareTests)
    totaltests = 0
    for h in hlist:
        totaltests += len (h.tested)
    count = 0
    BeginReport ('Developers with the most test credits (total %d)' % totaltests)
    for h in hlist:
        scount = len (h.tested)
        if scount > 0:
            ReportLine (h.name, scount, (scount*100.0)/totaltests)
        count += 1
        if count >= ListCount:
            break
    EndReport ()

def CompareTestCred (h1, h2):
    return h2.testcred - h1.testcred

def ReportByTestCreds (hlist):
    hlist.sort (CompareTestCred)
    totaltests = 0
    for h in hlist:
        totaltests += h.testcred
    count = 0
    BeginReport ('Developers who gave the most tested-by credits (total %d)' % totaltests)
    for h in hlist:
        if h.testcred > 0:
            ReportLine (h.name, h.testcred, (h.testcred*100.0)/totaltests)
        count += 1
        if count >= ListCount:
            break
    EndReport ()



#
# Reporter reporting.
#
def CompareReports (h1, h2):
    return len (h2.reports) - len (h1.reports)

def ReportByReports (hlist):
    hlist.sort (CompareReports)
    totalreps = 0
    for h in hlist:
        totalreps += len (h.reports)
    count = 0
    BeginReport ('Developers with the most report credits (total %d)' % totalreps)
    for h in hlist:
        scount = len (h.reports)
        if scount > 0:
            ReportLine (h.name, scount, (scount*100.0)/totalreps)
        count += 1
        if count >= ListCount:
            break
    EndReport ()

def CompareRepCred (h1, h2):
    return h2.repcred - h1.repcred

def ReportByRepCreds (hlist):
    hlist.sort (CompareRepCred)
    totalreps = 0
    for h in hlist:
        totalreps += h.repcred
    count = 0
    BeginReport ('Developers who gave the most report credits (total %d)' % totalreps)
    for h in hlist:
        if h.repcred > 0:
            ReportLine (h.name, h.repcred, (h.repcred*100.0)/totalreps)
        count += 1
        if count >= ListCount:
            break
    EndReport ()



def CompareESOBs (e1, e2):
    return e2.sobs - e1.sobs

def ReportByESOBs (elist):
    elist.sort (CompareESOBs)
    totalsobs = 0
    for e in elist:
        totalsobs += e.sobs
    count = 0
    BeginReport ('Employers with the most signoffs (total %d)' % totalsobs)
    for e in elist:
        if e.sobs > 0:
            ReportLine (e.name, e.sobs, (e.sobs*100.0)/totalsobs)
        count += 1
        if count >= ListCount:
            break
    EndReport ()


def DevReports (hlist, totalchanged, cscount, totalremoved):
    ReportByPCount (hlist, cscount)
    ReportByLChanged (hlist, totalchanged)
    ReportByLRemoved (hlist, totalremoved)
    ReportBySOBs (hlist)
    ReportByRevs (hlist)
    ReportByTests (hlist)
    ReportByTestCreds (hlist)
    ReportByReports (hlist)
    ReportByRepCreds (hlist)

def EmplReports (elist, totalchanged, cscount):
    ReportByPCEmpl (elist, cscount)
    ReportByELChanged (elist, totalchanged)
    ReportByESOBs (elist)
    
