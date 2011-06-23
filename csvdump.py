#
# aggregate per-month statistics for people
#
import sys, datetime
import csv

class CSVStat:
    def __init__ (self, name, email, employer, date):
        self.name = name
        self.email = email
        self.employer = employer
        self.added = self.removed = 0
        self.date = date
    def accumulate (self, p):
        self.added = self.added + p.added
        self.removed = self.removed + p.removed

PeriodCommitHash = { }

def AccumulatePatch (p, Aggregate):
    date = "%.2d-%.2d-01"%(p.date.year, p.date.month)
    if (Aggregate == 'week'):
        date = "%.2d-%.2d"%(p.date.isocalendar()[0], p.date.isocalendar()[1])
    authdatekey = "%s-%s"%(p.author.name, date)
    if authdatekey not in PeriodCommitHash:
        empl = p.author.emailemployer (p.email, p.date)
        stat = CSVStat (p.author.name, p.email, empl, date)
        PeriodCommitHash[authdatekey] = stat
    else:
        stat = PeriodCommitHash[authdatekey]
    stat.accumulate (p)

def OutputCSV (file):
    if file is None:
        return
    writer = csv.writer (file, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow (['Name', 'Email', 'Affliation', 'Date',
                      'Added', 'Removed'])
    for date, stat in PeriodCommitHash.items():
        # sanitise names " is common and \" sometimes too
        empl_name = stat.employer.name.replace ('"', '.').replace ('\\', '.')
        author_name = stat.name.replace ('"', '.').replace ('\\', '.')
        writer.writerow ([author_name, stat.email, empl_name, stat.date,
                          stat.added, stat.removed])

__all__ = [ 'OutputCSV' ]
