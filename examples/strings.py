# Atoms can be constructed and inspected without text-specific rule syntax.

from peye import *

backward(label(Name, Label), atom_concat('hello_', Name, Label))
backward(characters(Text, Chars, Length), atom_chars(Text, Chars), atom_length(Text, Length))
backward(unicode_codes(Text, Codes), atom_codes(Text, Codes))
query(label('alice', Label))
query(characters('café', Chars, Length))
query(unicode_codes('😀', Codes))
