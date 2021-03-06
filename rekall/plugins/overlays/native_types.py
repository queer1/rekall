"""Data types for various compilers.

Different models:
http://www.unix.org/version2/whatsnew/lp64_wp.html
http://en.wikipedia.org/wiki/64-bit_computing

Python standard types:
http://docs.python.org/2/library/struct.html#format-characters
"""

from rekall import obj

# Model on 64 bit unix like operating systems.
LP64 = {
    'bool' : obj.Curry(obj.Bool, type_name='bool', format_string='<c'),

    # Char is 8 bits.
    'char' : obj.Curry(obj.NativeType, type_name='char', format_string='<c'),
    'unsigned char' : obj.Curry(
        obj.NativeType, type_name='unsigned char', format_string='<B'),

    # Shorts are 16 bits.
    'short' : obj.Curry(obj.NativeType, type_name='short', format_string='<h'),
    'unsigned short' : obj.Curry(
        obj.NativeType, type_name='unsigned short', format_string='<H'),

    # ints are 32 bits.
    'int' : obj.Curry(obj.NativeType, type_name='int', format_string='<i'),
    'unsigned int' : obj.Curry(
        obj.NativeType, type_name='unsigned int', format_string='<I'),

    # Both long and long long are 64 bits.
    'long': obj.Curry(obj.NativeType, type_name='long', format_string='<q'),
    'unsigned long' : obj.Curry(
        obj.NativeType, type_name='unsigned long', format_string='<Q'),

    'long long': obj.Curry(
        obj.NativeType, type_name='long long', format_string='<q'),

    'unsigned long long' : obj.Curry(
        obj.NativeType, type_name='unsigned long long', format_string='<Q'),

    # Pointers are 64 bits.
    'address' : obj.Curry(
        obj.NativeType, type_name='address', format_string='<Q'),

    'unsigned be short' : obj.Curry(
        obj.NativeType, type_name='unsigned be short', format_string='>H'),
    'unsigned be int' : obj.Curry(
        obj.NativeType, type_name='unsigned be int', format_string='>I'),
}


# Model on 64 bit Windows.
LLP64 = {
    'bool' : obj.Curry(obj.Bool, type_name='bool', format_string='<c'),

    # Char is 8 bits.
    'char' : obj.Curry(obj.NativeType, type_name='char', format_string='<c'),
    'unsigned char' : obj.Curry(
        obj.NativeType, type_name='unsigned char', format_string='<B'),

    # Shorts are 16 bits.
    'short' : obj.Curry(obj.NativeType, type_name='short', format_string='<h'),
    'unsigned short' : obj.Curry(
        obj.NativeType, type_name='unsigned short', format_string='<H'),

    # ints are 32 bits.
    'int' : obj.Curry(obj.NativeType, type_name='int', format_string='<i'),
    'unsigned int' : obj.Curry(
        obj.NativeType, type_name='unsigned int', format_string='<I'),

    # long is also 32 bits.
    'long': obj.Curry(obj.NativeType, type_name='long', format_string='<i'),
    'unsigned long' : obj.Curry(
        obj.NativeType, type_name='unsigned long', format_string='<I'),

    # But long long is 64 bits.
    'long long': obj.Curry(
        obj.NativeType, type_name='long long', format_string='<q'),

    'unsigned long long' : obj.Curry(
        obj.NativeType, type_name='unsigned long long', format_string='<Q'),

    # Pointers are 64 bits.
    'address' : obj.Curry(
        obj.NativeType, type_name='address', format_string='<Q'),

    'unsigned be short' : obj.Curry(
        obj.NativeType, type_name='unsigned be short', format_string='>H'),
    'unsigned be int' : obj.Curry(
        obj.NativeType, type_name='unsigned be int', format_string='>I'),
}

# Model on 32 bit systems.
ILP32 = {
    'bool' : obj.Curry(obj.Bool, type_name='bool', format_string='<c'),

    # Char is 8 bits.
    'char' : obj.Curry(obj.NativeType, type_name='char', format_string='<c'),
    'unsigned char' : obj.Curry(
        obj.NativeType, type_name='unsigned char', format_string='<B'),

    # Shorts are 16 bits.
    'short' : obj.Curry(obj.NativeType, type_name='short', format_string='<h'),
    'unsigned short' : obj.Curry(
        obj.NativeType, type_name='unsigned short', format_string='<H'),

    # ints are 32 bits.
    'int' : obj.Curry(obj.NativeType, type_name='int', format_string='<i'),
    'unsigned int' : obj.Curry(
        obj.NativeType, type_name='unsigned int', format_string='<I'),

    # long is also 32 bits.
    'long': obj.Curry(obj.NativeType, type_name='long', format_string='<i'),
    'unsigned long' : obj.Curry(
        obj.NativeType, type_name='unsigned long', format_string='<I'),

    # But long long is 64 bits.
    'long long': obj.Curry(
        obj.NativeType, type_name='long long', format_string='<q'),

    'unsigned long long' : obj.Curry(
        obj.NativeType, type_name='unsigned long long', format_string='<Q'),

    # Pointers are 32 bits.
    'address' : obj.Curry(
        obj.NativeType, type_name='address', format_string='<I'),

    'unsigned be short' : obj.Curry(
        obj.NativeType, type_name='unsigned be short', format_string='>H'),
    'unsigned be int' : obj.Curry(
        obj.NativeType, type_name='unsigned be int', format_string='>I'),
}

# These are aliases for the same things
for model in [LP64, ILP32, LLP64]:
    for old, new in [
        ['char', 'signed char'],
        ['unsigned char', 'byte'],

        ['short', 'short int'],
        ['unsigned short', 'unsigned short int'],

        ['long', 'long int'],
        ['unsigned long', 'unsigned long int'],
        ['unsigned long', 'long unsigned int'],

        ['long long', 'long long int'],
        ['unsigned long long', 'unsigned long long int'],

        # Some weird combinations we sometimes see.
        ['unsigned long long', 'long long unsigned int'],
        ['unsigned short', 'short unsigned int'],
        ]:
        model[new] = model[old]
