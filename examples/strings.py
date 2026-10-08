# Atoms can be constructed and inspected without text-specific rule syntax.

from peye import *

implied_by(label(Name, Label), atom_concat('hello_', Name, Label))
implied_by(characters(Text, Chars, Length), atom_chars(Text, Chars) & atom_length(Text, Length))
implied_by(unicode_codes(Text, Codes), atom_codes(Text, Codes))
query(label('alice', Label))
query(characters('café', Chars, Length))
query(unicode_codes('😀', Codes))
