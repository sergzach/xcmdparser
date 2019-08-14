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
	It raises when a format of the command does not correspond to a parsing string.
	"""
	pass	


class CmdFormatError(Exception):
	"""
	It rases when fmt option of cmdparse has a wrong format.
	"""
	pass


def _remove_extra_gaps(s):
	return re.sub(r'\s{2,}', ' ', s)


def _convert_format(fmt):
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
		end_cmd = r'(?P<{cmd}>.+)'
		opts = dict(gap_before='', colon='', cmd='')
		if gap_before == _GAP_BEFORE:
			opts.update(gap_before=r'\s')
		if colon == _COLON:
			opts.update(colon=':')
		if len(typ) > 0:
			if typ == _TYPE_INT:
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



def cmdparse(fmt, s):
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
	"""
	fmt = fmt.strip()
	s = s.strip()
	fmt = _remove_extra_gaps(fmt)
	s = _remove_extra_gaps(s)
	re_fmt, custom_fields = _convert_format(fmt)
	d = _get_parsed_dict(re_fmt, s, fmt)
	for key, val in d.items():
		if key in custom_fields:
			typecast = custom_fields[key]
			d[key] = typecast(val)
	return d



