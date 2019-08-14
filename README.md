## What's xcmdparser?
A very simple tool to parse command line string within it's options.

### *An example*
```python
from xcmdparser import cmdparse
parsed = cmdparse('newsubscr <cid:int> <alias>[:<passwd>] [<description>]', 'newsubscr 24 myalias:pass12345 A description of a new subscription item.')
print('Parsed fields: cid={cid}, alias={alias}, passwd={passwd}, description="{description}"'.format(**parsed))
```
<b>The output.</b>
```python
Parsed fields: cid=24, alias=myalias, passwd=pass12345, description="A description of a new subscription item."
```

### The supported type qualifiers
You may refer to a field as <cid:int> to parse it as integer or <cid:float> to parse it as float. Other qualifiers are not supported. Negative values are supported.

By default (without any qualifier) a field is str.

### Supported Python versions
* 2.7
* 3.x

### How to install
`pip install https://github.com/sergzach/xcmdparser/archive/master.zip`

