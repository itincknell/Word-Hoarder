# Word-Hoarder
A program for creating a searchable local language dictionary based (mainly) on dumped wiktionary data. Allows users to collect definitions which can be exported as a machine readable flashcard file. Currently supports Latin, Ancient Greek and Old English.

## Parsing Data
### dump_parser.py
This module processes wiktionary dump files which can be found at kaikki.org

<ul><li>https://kaikki.org/dictionary/Latin/</li>
<li>https://kaikki.org/dictionary/Ancient%20Greek/index.html</li>
<li>https://kaikki.org/dictionary/Old%20English/index.html</li></ul>

See https://github.com/tatuylonen/wiktextract

The module looks for the files in a subfolder the parent of the directory containing the source files, "dumps unsorted"

The module organizes the data into a standard data structure used in this program

### the word definition data structure
Definitions are made of standard python data structures
<p>Definitions:
{
"heading": unicode string of the word as spelled in its original alphabet,
"handle": heading converted to asci,
"entries":[list of entry objects, see below],
"tags":[list of identifying tag strings],
"roots": heading of a root/lemma if the definition is not itself a root
}</p>
<p>Entries:
{
"partOfSpeech": string "verb", "noun" etc.,
"principleParts": string representing principle parts,
"simpleParts": simplified version of principle parts supported for Latin,
"senses": [list of word 'sense' objects, typically displayed as an ordered list],
"etymology": string containing etymology information
}</p>
<p>Senses:
{
"gloss": string containing a word sense you would find in a typical dictionary,
"tags": tags related to a specific word sense such as "Pre-classical" or "transitive"
}</p>

### dictionary_LSJ.py and dictionary_Middle_Liddell.py
These modules are called when the language is set to Ancient Greek. They use machine readable files of two important greek lexicon's: the Middle Liddel and Liddel-Scott-Jones (LSJ). 
The data files can be found here:
<ul><li>https://github.com/gcelano/LSJ_GreekUnicode/blob/master/grc.lsj.perseus-eng6.xml</li>
<li>https://github.com/blinskey/middle-liddell</li></ul>

These files were made available by the Tufts University Perseus Digital Library

### dictionary_MLJohnson.py
This module is called when the language is set to Old English. It uses a text file containing Mary Lynch Johnson's A Modern English - Old English Dictionary.
I hope to make this file available soon.

### get_simple.py
Called when the language is set to Latin. Changes the top line of most definitions to a simple string containing the 'principle parts' for verbs, nouns and adjectives. Other parts of speech are unchanged.

### language_splitter.py
Organize parsed definitions into a datrie and saves data to a local file.

## Using the dictionary
### load_dict.py
Utility functions for creating personal dictionary files or "word hoards". 
### parser_shell.py
This is this principle module for interacting with datrie files. Contains functions for loading trie objects, searching and saving definitions to word hoards.
### word_print_edit.py and edit_entry.py
Contain functions for editing and displaying word definitions and entries respectively

## Creating a flashcard file
Allows users to export a word hoard to a text file containing seperator characters and hmtl tags. The support is currently built around the file import tool in the Anki flashcard program. 
https://apps.ankiweb.net/

### edit_dictionary.py
Contains the functions for printing formatted flashcards to a file

## Tables
This is an entire functionally seperate part of the program. It fetchs pages from wiktionary.org and parses the html text to find the morphology tables for Latin, Greek and Old English words. Supports nouns, verbs and adjectives in all three languages. The algorithms are quite involved and are not compatible across languages. The word forms are organized into nested dictionaries and saved into a template file. The template files can be used to created flashcards with various configurations. 

Example: Front: present tense of verb "x", Back: Table showing present tense forms.

### tables.py, tables_greek_ext.py, tables_latin_ext.py, tables_oe_ext.py
These modules support the morphology table functionality

