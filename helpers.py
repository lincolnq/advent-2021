from typing import Callable
import re

class ParseFormat:
    def parse(self, data): ...
    def __pow__(self, rhs: 'ParseFormat | Callable') -> 'ParseFormat':
        # handle PF ** int or PF ** PF
        return Map(self, self._wrap(rhs))

    def __mod__(self, rhs) -> 'ParseFormat':
        # handle PF % (int, int)
        return SeparateParses(self, *map(self._wrap, rhs))

    def _wrap(self, x) -> 'ParseFormat':
        """if 'x' is a ParseFormat returns it unchanged.
        if 'x' is a Callable, wraps it in an Apply.
        """
        if isinstance(x, ParseFormat):
            return x
        if callable(x):
            return Apply(x)
        assert False, f"we don't know how to interpret {x} as a parser"

class SeparateParses(ParseFormat):
    """Parse lhs which is supposed to be of a fixed length, then handle each one
    separately according to the args provided. 
    
    Use either an arglist or a kwarglist, but not both.
    If an arglist is provided:
        - if the list is of length 1 then the result of SeparateParses is just the result of the inner parser
          (i.e., it returns the result 'unwrapped').
        - otherwise the result will be a tuple of all the parsed results from our separate parses.
    If a kwarglist is provided then the result will be a dictionary.
        
    """
    def __init__(self, lhs: ParseFormat, *args: ParseFormat, **kwargs: ParseFormat) -> None:
        super().__init__()
        self.lhs = lhs
        assert not args or not kwargs, "must provide either args or kwargs but not both"
        self.args = args
        self.kwargs = kwargs

    def parse(self, data):
        lhs_result = self.lhs.parse(data)

        if self.args:
            result = []
            for (lhs_data, fmt) in zip(lhs_result, self.args):
                result.append(fmt.parse(lhs_data))

            if len(self.args) == 1:
                return result
            else:
                return tuple(result)

        elif self.kwargs:
            result = {}
            for (lhs_data, (name, fmt)) in zip(lhs_result, self.kwargs.items()):
                result[name] = fmt.parse(lhs_data)
            return result


class Split(ParseFormat):
    """Split on a delim, returning a list.
    
    Also, unless autostrip=False, strip()s the input before parsing.
    """
    def __init__(self, delim, autostrip=True) -> None:
        super().__init__()
        self.delim = delim
        self.autostrip = autostrip

    def parse(self, data):
        if self.autostrip:
            data = data.strip()
        return data.split(self.delim)

def Sections(delim='\n\n', *args: ParseFormat, **kwargs: ParseFormat) -> None:
    """Combines a Split with a SeparateParses:
    Separate sections are treated separately. Specify section formats
    after the delim; they will each be parsed using their own format.

    Returns tuple of parsed sections.
    """
    return SeparateParses(Split(delim), *args, **kwargs)

def Lines(delim='\n'):
    """It's just a Split on newline."""
    return Split(delim)

class Tuple(Split):
    """Similar to Split on comma by default: First we split on the delim. 
    
    Unlike Split, you can specify automatic type conversion (from the default string type); and
    we returns a Python tuple, and has a comma as default delimiter."""
    def __init__(self, delim=',', conversions=None) -> None:
        super().__init__(delim)

    def parse(self, data):
        return tuple(super().parse(data))


class Apply(ParseFormat):
    """ParseFormat which just applies a function to its input."""
    def __init__(self, f) -> None:
        super().__init__()
        self.f = f

    def parse(self, data):
        return self.f(data)


class Map(ParseFormat):
    """ParseFormat created by doing `lhs ** rhs` between two ParseFormats, 
    or a ParseFormat and a simple mappable function.

    We first feed our input into the lhs, which must produce a list or iterable parse result; 
    then we map the rhs over that list."""
    def __init__(self, lhs: ParseFormat, rhs: 'ParseFormat | Callable') -> None:
        super().__init__()
        self.lhs = lhs
        self.rhs = rhs
    
    def parse(self, data):
        result = self.lhs.parse(data)
        return [self.rhs.parse(item) for item in result]

class Re(ParseFormat):
    """Regex pattern extracting a fixed number of things from a regex.
    
    Every char is taken literally except for $$ (referring to a string token like \w+) 
    and %% (referring to an integer numeric token like \d+).
    """
    def __init__(self, simple_pat) -> None:
        super().__init__()
        # compile our simple RE into a proper regex
        token_re = re.compile(r'\$\$|%%')

        proper_matcher_regex = ''
        startix = 0
        ngroups = 0
        for m in token_re.finditer(simple_pat):
            proper_matcher_regex += re.escape(simple_pat[startix:m.start()])
            if m.group(0) == '$$':
                proper_matcher_regex += '(\w+)'
                ngroups += 1
            elif m.group(0) == '%%':
                proper_matcher_regex += '(\d+)'
                ngroups += 1
            startix = m.end()
        proper_matcher_regex += re.escape(simple_pat[startix:])

        #print(f"compiled RE is: {proper_matcher_regex}")
        self.re = re.compile(proper_matcher_regex)
        self.ngroups = ngroups


    def parse(self, data):
        m = self.re.match(data)
        return tuple(m.group(g + 1) for g in range(self.ngroups))

def test1():
    sample = """6,10
0,14
9,10
0,3
10,4
4,11
6,0
6,12
4,1
0,13
10,12
3,4
3,0
8,4
1,10
2,14
8,10
9,0

fold along y=7
fold along x=5
"""

    s = Sections(
            '\n\n',
            dots=Lines() ** Tuple(',') ** int,
            folds=Lines() ** (Re('fold along $$=%%') % (str, int))
        ).parse(sample)
    print(s)
test1()