"""
The `cmdparse()` parses command string (see ../README.md or ../tests.py for examples).
"""
import re

_RE_CMD_NAME = r'^(\S+)(?:\s.*)?$'
_RE_CMD = r'(?P<gap_before>\s)?(?P<begin_bracket>\[)?(?P<colon>:)?<(?P<cmd>[^\s:\[\]<>]+):?(?P<type>[^\s:]+)?>(?P<end_bracket>\])?'
_TYPE_INT = 'int'
_TYPE_FLOAT = 'float'
_GAP_BEFORE = ' '
_BEGIN_BRACKET = '['
_END_BRACKET = ']'
_COLON = ':'



class CmdParseError(Exception):
	"""
	It occurs when a format of the command does not correspond to a parsing string.
	"""
	pass	


class CmdFormatError(Exception):
	"""
	It occurs when fmt option of cmdparse has a wrong format.
	"""
	pass


class CmdCustomTypeError(Exception):
	"""
	It occurs when one or more custom_types option of cmdparse are wrong.
	"""
	def __init__(self, message, custom_types):
		super(CmdCustomTypeError, self).__init__(message)
		self.custom_types = custom_types


def _remove_extra_gaps(s):
	"""
	Replace every more then 2 neighbor gaps with 1 gap.
	s: str
		A string to change in.
	"""
	return re.sub(r'\s{2,}', ' ', s)


def _check_re(s):
	"""
	Return True a reg. exp in the string is correct.
	Parameters
	----------
	s: str
		A string with reg. exp. to check.
	"""
	try:
		re.compile(s)
	except re.error:
		return False
	else:
		return True


def _check_custom_types(custom_types):
	"""
	Check regular expressions for custom_types.
	Return keys for custom types which reg. exps. are incorrect.
	Parameters
	----------
	custom_types: dict
		A dict of custom types. Keys are names of the fields and values are string reg. exps. which are allowed.
	"""
	wrong_custom_types = [x[0] for x in filter(lambda x: not _check_re(x[1]), custom_types.items())]
	return wrong_custom_types



def _convert_format(fmt, custom_types):
	r"""
	Convert a format from cmd form to reg. exp. form.
	An example.
	'newsubscr <cid:int> <alias>[:<passwd>] [<description>]' ->
	r'^newsubscr\s(?P<cid>-?\d+)\s(?P<alias>[^\s:]+)(?::(?P<passwd>[^\s:]+))?(?:\s(?P<description>.+))?$'
	Return value: the converted format and custom_fields. 
	custom_fields are dict where keys are field names and values are typecast functions. 
	Typecast functions are called to convert the field to a corresponding type.
	Parameters
	----------
	fmt: str
		Source format to convert to reg. exp.
	custom_types: dict
		A dict of custom types. Keys are names of the fields and values are string reg. exps. which are allowed.
	"""
	# a integer fields to convert later
	custom_fields = {}
	m_cmd_name = re.match(_RE_CMD_NAME, fmt)
	cmd_name = m_cmd_name.group(1)
	converted = [cmd_name]
	cmds_types = re.findall(_RE_CMD, fmt)	
	i = 0
	len_cmd_types = len(cmds_types)
	for gap_before, begin_bracket, colon, cmd, typ, end_bracket in cmds_types:
		opt_template = r'{gap_before}{colon}{cmd}'
		must_exist = r'{x}'
		must_not_exist = r'(?:{x})?'
		int_cmd = r'(?P<{cmd}>-?\d+)'
		float_cmd = r'(?P<{cmd}>-?(?:\d+|\d+[\.,]\d*))'
		str_cmd = r'(?P<{cmd}>[^\s:]+)'
		custom_cmd = r'(?P<{cmd}>{re})'
		end_cmd = r'(?P<{cmd}>.+)'
		opts = dict(gap_before='', colon='', cmd='')
		if gap_before == _GAP_BEFORE:
			opts.update(gap_before=r'\s')
		if colon == _COLON:
			opts.update(colon=':')
		if len(typ) > 0:
			if typ in custom_types:
				opts.update(cmd=custom_cmd.format(cmd=cmd, re=custom_types[typ]))
				# no typecast, so, do not add into custom_fields
			elif typ == _TYPE_INT:
				opts.update(cmd=int_cmd.format(cmd=cmd))
				custom_fields.update({cmd: int})
			elif typ == _TYPE_FLOAT:
				opts.update(cmd=float_cmd.format(cmd=cmd))
				custom_fields.update({cmd: float})			
			else:
				raise CmdFormatError('A wrong format "%s".' % fmt)
		else:
			if i < len_cmd_types - 1:
				opts.update(cmd=str_cmd.format(cmd=cmd))
			else:
				opts.update(cmd=end_cmd.format(cmd=cmd))
		if end_bracket == _END_BRACKET:
			converted.append(must_not_exist.format(x=opt_template.format(**opts)))
		else:
			converted.append(must_exist.format(x=opt_template.format(**opts)))				
		i += 1
	converted_fmt = r''.join(converted)
	converted_fmt = r'^%s$' % converted_fmt
	return converted_fmt, custom_fields


def _get_parsed_dict(re_fmt, s, fmt):
	"""
	Input: parse command in reg. exp., source string.
	It returns options finally parsed.
	Parameters
	----------
	re_fmt: str
		A command to parse in reg. exp.
	s: str
		A source string.
	"""	
	m = re.match(re_fmt, s)
	if m is not None:
		parsed_dict = {k: v.strip() for k, v in m.groupdict().items() if v is not None}	
		return parsed_dict
	else:
		raise CmdParseError('The string "%s" does not correspond to the primary format "%s".' % (s, fmt))



def cmdparse(fmt, s, custom_types={}):
	"""
	Parse a string in s with command format in fmt.
	An example.
	```cmdparse('newsubscr <cid:int> <alias>[:<passwd>] [<description>]', 
	'newsubcr 24 myalias:pass12345 A description of a new subscription item.')```
	Parameters
	----------
	fmt: str
		A format of command.
	s: str
		A parsing string.
	custom_types: dict
		A dict of custom types. Keys are names of the fields and values are string reg. exps. which are allowed.
	"""
	fmt = fmt.strip()
	s = s.strip()
	wrong_custom_types = _check_custom_types(custom_types)
	if len(wrong_custom_types) > 0:
		raise CmdCustomTypeError('The regular expressions for the custom types are wrong: {}.'.format( \
			', '.join(['"{}"'.format(x) for x in wrong_custom_types])), wrong_custom_types)
	fmt = _remove_extra_gaps(fmt)
	s = _remove_extra_gaps(s)
	re_fmt, custom_fields = _convert_format(fmt, custom_types)
	d = _get_parsed_dict(re_fmt, s, fmt)
	for key, val in d.items():
		if key in custom_fields:
			typecast = custom_fields[key]
			d[key] = typecast(val)
	return d



