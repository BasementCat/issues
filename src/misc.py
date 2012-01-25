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
         string.format() accepts: <, ^, >.
_##      Print a horizontal line made up of _ characters, optionally ## percent
         the width of the screen.  Default width is 100%.
-##      Print a horizontal line made up of - characters, optionally ## percent
         the width of the screen.  Default width is 100%."""
	alignment_chars={'l': '<', 'c': '^', 'r': '>'}
	variables=[]
	#columns=[]
	lines=[[]]
	currentArg=0
	currentLine=0
	for directive in re.findall("\.|%\d+|\|[lcr<>^]|[\r\n]|[-_](?:\d+)?", format):
		#print directive
		if directive=='.':
			variables.append(args[currentArg])
			currentArg+=1
		elif directive.startswith('%'):
			variables.append(args[int(directive.strip("%"))])
		elif directive in ("\r", "\n"):
			lines.append([])
			currentLine+=1
		elif directive.startswith("|"):
			lines[currentLine].append(('align', directive.strip("|")))
		elif len(directive) and directive[0] in ("-", "_"):
			hrchar=directive[0]
			directive=directive.strip("-_")
			hrwidth=(100 if len(directive)==0 else int(directive))/100.0
			lines[currentLine].append(('hr', hrchar, hrwidth))
	variables.reverse()
	out_final=[]
	for line in lines:
		colwidth=int(int(consoleColumns)/len(line))
		out_temp=[]
		for col in line:
			if col[0]=="align":
				align_char=alignment_chars[col[1]] if alignment_chars.has_key(col[1]) else col[1]
				out_temp.append(str.format("{0: "+align_char+str(colwidth)+"."+str(colwidth)+"s}", variables.pop()))
			elif col[0]=="hr":
				out_temp.append(str.format("{0: ^"+str(colwidth)+"."+str(colwidth)+"s}", col[1]*int(col[2]*colwidth)))
		out_final.append("".join(out_temp))
	return "\n".join(out_final)