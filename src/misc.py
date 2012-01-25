import time, calendar, re, subprocess

consoleRows, consoleColumns=subprocess.check_output(['stty', 'size']).strip().split()

def time_utc(tm=None):
	"""Converts a local timestamp to UTC, or returns the current timestamp in UTC"""
	tm=time.gmtime(tm)
	return calendar.timegm(tm)

def time_local(tm=None):
	"""Converts a UTC timestamp to local time, or returns the current local timestamp"""
	tm=time.localtime(tm)
	return time.mktime(tm)

def align(format, *args):
	"""Prints the supplied arguments as defined by the format string.

The following characters have special meaning in the format string:
.        The next variable in the argument list
%number  Element number (number) in the argument list
|[lcr]   Each | indicates a column boundary.  If the | is followed by any of l,
         c, or r, that indicates the alignment of that column.  The alignment
         character can also be any of the string alignment characters that
         string.format() accepts: <, ^, >."""
	alignment_chars={'l': '<', 'c': '^', 'r': '>'}
	variables=[]
	columns=[]
	currentArg=0
	for directive in re.findall("\.|%\d+|\|[lcr<>^]|[\r\n]", format):
		if directive=='.':
			variables.append(args[currentArg])
			currentArg+=1
		elif directive.startswith('%'):
			variables.append(args[int(directive.strip("%"))])
		elif directive in ("\r", "\n"):
			print directive,
		elif directive.startswith("|"):
			columns.append(directive.strip("|"))
	colwidth=int(int(consoleColumns)/len(columns))
	variables.reverse()
	out=[]
	for col in columns:
		align_char=alignment_chars[col] if alignment_chars.has_key(col) else col
		out.append(str.format("{0: "+align_char+str(colwidth)+"."+str(colwidth)+"s}", variables.pop()))
	return "".join(out)