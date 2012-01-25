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
	variables=[a for a in args]
	variables.reverse()
	lines=[[]]
	currentLine=0
	currentCol=-1
	for directive in re.findall("\.|\|(?:c(?:\d+)?)?[<>^]?|[\r\n]|[-_](?:\d+)?", format):
		if directive in ("\r", "\n"):
			lines.append([])
			currentLine+=1
			currentCol=-1
		elif directive==".":
			var=variables.pop()
			lines[currentLine][currentCol]['contents'].append(('fixed', var))
			if lines[currentLine][currentCol]['width'] is not None: lines[currentLine][currentCol]['width']+=len(var)
		elif directive.startswith("|"):
			lines[currentLine].append({'width': 0, 'contents': []})
			currentCol+=1
			collapse, cpad, alignment=re.match("\|(c(\d+)?)?([<>^])?", directive).groups()
			collapse=True if collapse else False
			cpad=int(cpad) if cpad else 0
			alignment=alignment if alignment else "<"
			lines[currentLine][currentCol]['collapse']=collapse
			lines[currentLine][currentCol]['cpad']=cpad
			lines[currentLine][currentCol]['alignment']=alignment
		elif len(directive) and directive[0] in ("-", "_"):
			hrchar=directive[0]
			directive=directive.strip("-_")
			if lines[currentLine][currentCol]['collapse']:
				lines[currentLine][currentCol]['contents'].append(('fixed', hrchar*3))
				lines[currentLine][currentCol]['width']+=3
			else:
				hrwidth=(100 if len(directive)==0 else int(directive))/100.0
				lines[currentLine][currentCol]['contents'].append(('variable', hrchar, hrwidth))
				lines[currentLine][currentCol]['width']=None
	out_final=[]
	for line in lines:
		fixed_col_len=0
		fixed_col_count=0
		#Find the len of all collapsed columns in this line
		for column in line:
			if column['collapse']:
				fixed_col_count+=1
				fixed_col_len+=(column['width']+(column['cpad']*2))
		#now, with the len of fixed columns+padding:
		colwidth=int((int(consoleColumns)-fixed_col_len)/(len(line)-fixed_col_count))
		out_temp=[]
		for column in line:
			col_temp=[]
			if column['collapse']:
				col_temp.append(" "*column['cpad'])
			for obj in column['contents']:
				if obj[0]=="fixed":
					col_temp.append(obj[1])
				elif obj[0]=="variable":
					col_temp.append(obj[1]*int(obj[2]*colwidth))
			if column['collapse']:
				col_temp.append(" "*column['cpad'])
			col_temp="".join(col_temp)
			if not column['collapse']:
				col_temp=str.format("{0: "+column['alignment']+str(colwidth)+"."+str(colwidth)+"s}", col_temp)
			out_temp.append(col_temp)
		out_final.append("".join(out_temp))
	return "\n".join(out_final)