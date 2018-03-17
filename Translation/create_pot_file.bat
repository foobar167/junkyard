:: This creates a pot file named choose_language.pot.
:: This is just a normal plaintext file that lists all the translated strings
:: it found in the source code by search for _() calls.
@echo off
py -3.6 c:\Python36\Tools\i18n\pygettext.py -d choose_language choose_language.py second_file.py
