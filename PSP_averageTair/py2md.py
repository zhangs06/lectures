#!/usr/bin/env python
# coding=utf-8

# <a class="btn btn-default pull-right" href="https://gist.github.com/TylerShaw/48ead56c19ce905ac513"><i class="fa fa-git"></i> Download the gist here!</a>
# Py2Md started as a little project to do the magical "self documenting code". After thinking about it, I realized self documenting code is great, but it's really not the point.
# Commenting code properly, if only better, is the point.
# This script evolved from me wanting to code better. I often look at other peoples code, or even old code I've written, and it takes me a few minutes to even figure out what each section is doing.
# This will hopefully solve that, not only by forcing me to comment code better, but to publish my code with decent comments.
# This script reads in a python file (either itself, or anything it's
# imported into) and converts the python file into a markdown file. It
# does this by turning all the comments into markdown format, and turning
# all the code into markdown code blocks. It also removes the `import
# py2md` from the imports list so it doesn't throw off any readers.

# Things I still need to do:
#
# * Block comments `'''` to markdown (shouldn't be hard)
# * Inline comments that happen after code (still undecided about this one)
# * Refactor
# * Try/Except statements to catch possible errors
# * Options for things like ReStructuredText
# * Options for different flavors of markdown
# * Automatic git add/commit/push and link the repo at the bottom (or top)
#       * Or gist maybe?

# Imports
import __main__ as main
import datetime
from time import strftime
import os
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

# Global Variables
pelican = True
path = '/Users/ts/Dropbox/Workspace/Websites/TylerShaw.codes/TSC_pelican/content/'

# Auto config stuffs
dtg = strftime('%Y-%m-%d %H:%M')  # date time group
target = main.__file__  # The filename of the python file running
filename = str(path + str(target.split('.py')[0]) + '.md')  # replaces the .py extension with a .md extension
metadata_file = str(path + str(target.split('.py')[0]) + '.metadata')  # replaces the .py extension with a .metadata extension

# This reads in the current file being run


def ReadIn(file_to_open=target):
    with open(file_to_open, 'r') as f:  # Read in file
        return f.readlines()

# Cleans it up some, removing line breaks


def Clean(content):
    for line in content:
        if line.rstrip():
            yield line.rstrip()

# Converts to Markdown Format and does code fencing (blocks)


def Convert2Markdown(code):
    start = '\n<div class="highlight"><pre>'  # Start of codeblock
    end = '</pre></div>\n'  # End of codeblock
    markdown = []
    in_code_block = False
    for codeline in code:
        line = codeline.strip()
        if line[0:2] == '#!':  # Strips env
            print('removing environmental variable line')
        elif line[0:14] == '# coding=utf-8':  # Strips encoding
            print('removing encoding line')
        elif line[0:2] == '# ':  # Finds code comments
            if in_code_block == True:
                markdown.append(end)
            markdown.append(line.split('# ')[1])
            in_code_block = False
        elif line[0] == '#':  # Finds code comments
            if in_code_block == True:
                markdown.append(end)
            markdown.append(line.split('#')[1])
            in_code_block = False
        elif line[0:12] == 'import py2md':
            print('removing import py2md from import list')
        else:
            if in_code_block == False and pelican == True:
                markdown.append(start)
            pyg = str('<span class="codeline">' + highlight(codeline, PythonLexer(), HtmlFormatter())[28:-13].strip('\n') + '</span>').strip('\n')
            markdown.append(pyg)
            in_code_block = True
    return markdown

# Adds Article headers for Pelican. If the article already exists, then it
# will load the metadata in from the previous version and update it with a
# "Modified" date time group, that way it will keep previous metadata and
# the previous post date.


def PelicanArticle(markdown):
    metadata = {}
    metadata['Title'] = 'Title: ' + target.split('.py')[0]
    metadata['Date'] = 'Date: ' + dtg
    metadata['Tags'] = 'Tags: python'
    metadata['Category'] = 'Category: python'
    metadata['Authors'] = 'Authors: Tyler Shaw'
    metadata['Modified'] = ''
    if os.path.isfile(metadata_file):
        md = Clean(ReadIn(metadata_file))
        for line in md:
            key = line.split(':')[0]
            value = line
            metadata[key] = value
        metadata['Modified'] = 'Modified: ' + dtg
        os.remove(metadata_file)

    article = []
    article.append(metadata['Title'])
    article.append(metadata['Date'])
    article.append(metadata['Tags'])
    article.append(metadata['Category'])
    article.append(metadata['Authors'])
    article.append(metadata['Modified'])
    article.append('')
    Write2File(article, metadata_file)
    for line in markdown:
        article.append(line)
    return article

# Writes markdown to a file


def Write2File(markdown, file):
    with open(file, 'w') as f:
        for line in markdown:
            f.write(line)  # python will convert \n to os.linesep
            f.write('\n')

# Runs everything


def py2md():
    me = ReadIn()
    cleaned = Clean(me)
    converted = Convert2Markdown(cleaned)
    if pelican:
        converted = PelicanArticle(converted)
    Write2File(converted, filename)
    print("Exported Markdown")

py2md()

# <a class="btn btn-default pull-right" href="https://gist.github.com/TylerShaw/48ead56c19ce905ac513"><i class="fa fa-git"></i> Download the gist here!</a>