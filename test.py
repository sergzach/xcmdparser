import pytest
from xcmdparser import cmdparse, CmdParseError, CmdFormatError, CmdCustomTypeError


@pytest.fixture
def parsed_int():
    """
    A fixture to create parsed with int option.
    """
    return cmdparse(    'newsubscr <cid:int> <alias>[:<passwd>] [<description>]', 
                        'newsubscr 24 myalias:pass12345 A description of a new subscription item.')      


@pytest.fixture
def parsed_float():
    """
    A fixture to create parsed with int option.
    """
    return cmdparse(    'newsubscr <cid:float> <alias>[:<passwd>] [<description>]', 
                        'newsubscr -24.34 myalias:pass12345 A description of a new subscription item.')                              


@pytest.fixture
def parsed_str():
    """
    A fixture to create parsed with int option which is interpreted as str option.
    """
    return cmdparse(    'newsubscr <cid> <alias>[:<passwd>] [<description>]', 
                        'newsubscr 24 myalias:pass12345 A description of a new subscription item.')    


def test_int1(parsed_int):
    """
    Test int in option.
    """
    assert parsed_int['cid'] == 24
    assert parsed_int['alias'] == 'myalias'
    assert parsed_int['passwd'] == 'pass12345'
    assert parsed_int['description'] == 'A description of a new subscription item.'


def test_float(parsed_float):
    """
    Test int in option.
    """
    assert parsed_float['cid'] == -24.34
    assert parsed_float['alias'] == 'myalias'
    assert parsed_float['passwd'] == 'pass12345'
    assert parsed_float['description'] == 'A description of a new subscription item.'


def test_str(parsed_str):
    """
    Test that int option could be interpreted as string.
    """
    assert parsed_str['cid'] == '24'
    assert parsed_str['alias'] == 'myalias'
    assert parsed_str['passwd'] == 'pass12345'
    assert parsed_str['description'] == 'A description of a new subscription item.'


def test_gaps():
    """
    Test extra gaps. They should be ignored.
    """
    parsed = cmdparse(    'newsubscr <cid>' + ' ' * 3 + '<alias>[:<passwd>]' + ' ' * 20 + '[<description>]', 
                        'newsubscr 24' + ' ' * 30 + 'myalias:pass12345 A description' + ' ' * 10 + 'of a new subscription item.' +
                        ' ' * 9)
    assert parsed['cid'] == '24'
    assert parsed['alias'] == 'myalias'
    assert parsed['passwd'] == 'pass12345'
    assert parsed['description'] == 'A description of a new subscription item.'


def test_raises():
    with pytest.raises(CmdParseError):
        parsed = cmdparse('client <cid:int>', 'client john')
    with pytest.raises(CmdParseError):
        parsed = cmdparse('client <cid:float>', 'client john')        
    with pytest.raises(CmdParseError):        
        parsed = cmdparse('client <cid:int>', 'client 24 description')        


def test_format_error():
    with pytest.raises(CmdFormatError):
        parsed = cmdparse('client <cid:str>', 'client john')


def test_custom_types():
    cmd = 'newsubscr <cid:float> <alias:slug>[:<passwd>] [<description>]'
    parsed = cmdparse(cmd, 'newsubscr -23.34 new-subscr:12345 a new subscription', {'slug': r'[a-z\-]+'})
    assert parsed['cid'] == -23.34
    assert parsed['alias'] == 'new-subscr'
    assert parsed['passwd'] == '12345'
    assert parsed['description'] == 'a new subscription'
    with pytest.raises(CmdParseError):
        parsed = cmdparse(cmd, 'newsubscr 24.0 new_subscr:12345 a new subscription', {'slug': r'[a-z\-]+'})
    with pytest.raises(CmdFormatError):
        parsed = cmdparse(cmd, 'newsubscr 24.0 new_subscr:12345 a new subscription')
    try:
        parsed = cmdparse(cmd, 'newsubscr 24.0 new_subscr:12345 a new subscription', {'slug': r'[+'})
    except CmdCustomTypeError as e:
        assert e.custom_types == ['slug']
    else:
        raise Exception('Wrong format for "slug" is not detected.')
        