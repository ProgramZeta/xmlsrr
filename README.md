# XML Search / Remove / Replace (XMLSRR)
Scans files in a folder to find matches, remove, and/or replace elements based off of CSS-like syntax

## Requirements
Python 3.2
lxml

## Setup


## Usage
`xmlsrr -h -i [instruction file] -l [log file] -o [output folder] -s -vvvv -V <target>`

###Required Parameters
`<target>` directory of files to scan

###Optional Parameters
`-h` displays help
`-i [instruction file]` provide a file with instructions
`-l [log file]` log file to write to
`-o [output folder]` write new files to a specific folder instead of removing o replacing in-place
`-s` silent mode
`-v` display more information (repeat for additional verbosity)
`-V` verify directory (and instruction file, if provided) but do not run scan

## Search
Unless specified otherwise, any matches are output to stdout

### Search Syntax
* `foo` will match any element named 'foo'
* `.foo` will match any element with a class 'foo'
* `#foo` will match any element with an id 'foo'
* `[foo]` will match any element with a 'foo' attribute
* `[foo=bar]` will match an element with a 'foo' attribute set to 'bar'
* `foo bar` will match any 'bar' element that is a descendant of 'foo'

You can mix and match these (like CSS selectors)

####Examples
* `h1#title` matches any 'h1' element that has the id attribute 'title'
* `img.thumbnail[src]` matches any 'img' element with the 'thumbnail' class that has a 'src' attribute
* `p.translate span[lang=en-us]` matches any 'span' element with the 'lang' attribute to 'en-us' that is a descendant
  of a 'p' element with the 'translate' class

## Remove
To remove an element, include `/` as the first character in your search line. The matching elements and their contents
are completely removed from the source file.

## Replace
To replace an element, use `->` to specify what the element should be replaced with. Note that this does not change the
contents of the element, but the element and attributes.

Replacement syntax is similar to search syntax, but you can't use a space for the replacement element - you can only
replace the targeted element with a single replacement element.

###Examples
*
*
*