# run guard
if __name__ == "__main__":
    from os import _exit
    _exit(0)

# To quickly and visually determine the heirarchy and utility of different variables/functions,
# the following style is maintained throughout fygenlib files.

# Large Divider 
# "# -(x96) #"
# Used for separating unrelated sections, i.e. separate classes, different function trees
# ---------------------------------------------------------------------------------------------------- #

# Short Divider
# "# -(x46)" #"
# Used for separating related sections, i.e. functions within a class, related helper functions
# -------------------------------------------------- #

# Scoped Variable
# snake_case

# Global Variable
# MACRO_CASE

# Function Parameter Variable
# Pascal_Snake_Case

# Class
# PascalCase

# Functions
# camelCase(Parameter_Variable : ParameterType) -> ReturnType:
#
# camelCase(
#   Parameter_Variable : ParameterType,
#   Parameter_Variable : ParameterType,
#   Default_Variable : ParameterType = Value,
# ) -> (
#   tuple[
#       ReturnType,
#       ReturnType,
#       ReturnType
#   ]
# ):

# Helper/internal Functions
# _underscoreCamelCase() -> ReturnType
# see above for multiline

# Calling Functions
# Note that used default variables usually have a space separating the equals sign
# functionName(scoped_variable, scoped_variable, Default_Variable = scoped_variable)
# 
# functionName(
#   scoped_variable,
#   scoped_variable
#   Default_Variable = scoped_variable
# )
#
# functionName(
#   scoped_variable, scoped_variable, scoped_variable,
#   Default_Variable = scoped_variable, Default_Variable = scoped_variable
# )

# The following is an annotated example of code organization:
# ---------------------------------------------------------------------------------------------------- #
#spacer line before ascii header
#tab▄▄ ▄▄ ▄▄▄▄▄  ▄▄▄  ▄▄▄▄  ▄▄▄▄▄ ▄▄▄▄    ▄▄▄▄  ▄▄ ▄▄ 
#tab██▄██ ██▄▄  ██▀██ ██▀██ ██▄▄  ██▄█▄   ██▄█▀ ▀███▀ 
#tab██ ██ ██▄▄▄ ██▀██ ████▀ ██▄▄▄ ██ ██ ▄ ██      █  
#spacer line after ascii header
# ---------------------------------------------------------------------------------------------------- #
#spacer before development history table
#tab----------------------------------------------------------------------------
#   Development History & Contacts                  Table width = last char pos
#   ----------------------------------------------------------------------------
#   Role Name Goes Here                         |   Name
#   Longest Role Name Determines Table Length   |   Name, Name, Name, Name, Name
#   ----------------------------------------------------------------------------
#   Last Updated: Month/Day/Year
#spacer after development history table
# ---------------------------------------------------------------------------------------------------- #
#spacer before desctription section
#tabOverall Description of the file's purpose, and key changes from legacy files if applicable
#
#   Information Header like ClassName
#       - Bulletpoint list
#       - of information
#spacer before desctription section
# ---------------------------------------------------------------------------------------------------- #
import collections # in alphabetic order
import itertools
import os
# spacer between 'import' and 'from X import Y'
from csv import get_dialect as camelCaseFunction # alphabetic order of module name, not imported items
from datetime import datetime as PascalCaseClass
# spacer before import of nonstandard modules
import selfmademodule                                    # pyright: ignore[reportMissingImports]
from selfmademodule.submodule import selfMadeFunction    # pyright: ignore[reportMissingImports]
# ---------------------------------------------------------------------------------------------------- #
def functionOne(Parameter_One : type, Parameter_Two : type | type = None) -> type | None:
    '''
    # functionOne

    The description of functionOne goes here. If the line length exceeds 100 characters, split \
    it before or at the 100th character using a backslash.

    Parameters
    ----------
    `Parameter_One` : *type*
        - Description of ParameterOne goes here. If the line length exceeds 100 characters, split \
        it across multiple using a backslash.
    `Parameter_Two` : *type* | *None*, optional
        - Description of ParameterTwo goes here. If the line length exceeds 100 characters, split \
        it across multiple using a backslash.

    Returns
    -------
    *type*
        - A description of why this type would be returned, and what value it represents
    *None*
        - A description of why this type would be returned, and what value it represents

    Examples
    --------
    >>> functionOne(4)
    value
    >>> functionOne(4, 8)
    value
    '''
    # spacer line after docstring
    if Parameter_Two is None:
        return None
    return _helperFunctionOne(Parameter_One, Parameter_Two)
# -------------------------------------------------- #
def _helperFunctionOne(
    Parameter_One : type, 
    Parameter_Two : type
) -> (
    tuple[
        type,
        type
    ]
):
    '''
    A docstring should be provided here and under all functions, but for the sake of saving \
    time and space when reading this document, this placeholder is provided instead.
    '''
    # spacer line after docstring
    return (
        Parameter_One is Parameter_Two, 
        Parameter_Two
    )
# ---------------------------------------------------------------------------------------------------- #
class ClassName(PascalCaseClass):
    '''
    # ClassName

    The description of ClassName goes here. If the line length exceeds 100 characters, split it \
    before or at the 100th character using a backslash.

    Member Variables
    ----------------
    `variable_one` : *type*
        - What it is and why its relevant and what it is meant to do and not do
    
    Member Functions
    ----------------
    `functionOne`
        - Description of what its purpose is. An in-depth explanation is not required, since each \
        function is expected to have its own descriptive docstring

    Instantiation
    -------------
    >>> variable_of_class = ClassName(ParameterInInit, ParameterInInit)
    '''
# -------------------------------------------------- #
    variable_one : type
# -------------------------------------------------- #
    __slots__ = [       # While slots is generally used for class optimization, here, we use slots
        'variable_one'  # to prevent the class itself from having dynamic variable additions. If
    ]                   # it's desired, a dynamically sized member variable should instead be used.
# -------------------------------------------------- #
    def __init__(this, Parameter_One : type, Parameter_Two : type | None = None) -> None:
        '''
        A docstring should be provided here and under all functions, but for the sake of saving \
        time and space when reading this document, this placeholder is provided instead.
        '''
        # spacer line after docstring
        this.variable_one = Parameter_One + Parameter_Two
# -------------------------------------------------- #
    def functionOne(this) -> None:
        '''
        A docstring should be provided here and under all functions, but for the sake of saving \
        time and space when reading this document, this placeholder is provided instead.
        '''
        # spacer line after docstring
        return this.variable_one
# ---------------------------------------------------------------------------------------------------- #
def main() -> None:
    class_name = ClassName("parameter_one", Parameter_Two = "parameter_two")
    value = class_name.functionOne()
    print_value = functionOne(value, Parameter_Two = value)
    print(print_value)

    try: # we fail loudly instead of letting a silent error occur
        class_name.mispelled_member_variable = "oops"
    except: # Saves time, makes the fix rapid and self evident
        print("An error would be thrown above since it's not a valid variable of ClassName!")
# -------------------------------------------------- #
if __name__ == "__main__":
    # auxiliary setup here if necessary
    main()
# ---------------------------------------------------------------------------------------------------- #