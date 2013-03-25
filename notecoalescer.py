from collections import namedtuple
from os.path import basename
from os.path import splitext
import argparse
import re

grouper = re.compile(
    "<!--Important(?P<level>[0-9]+)-->(?P<text>((?!<!--Important[0-9]+-->).)*)<!--EndImportant-->",
    re.MULTILINE | re.DOTALL,
    )

Note = namedtuple('Note', ['level', 'text', 'linkto'])


def fileWithoutExtension(filename):
    return splitext(basename(filename))[0]


def parseInFile(inFile):
    parseList = []

    try:
        fileHandle = open(inFile, 'r')
    except:
        print("could not open file:", inFile)
    else:
        fileData = fileHandle.read()
        fileName = fileWithoutExtension(inFile)
        for it in grouper.finditer(fileData):
            tmp = Note(
                level=it.group('level'),
                text=it.group('text'),
                linkto=fileName,
                )
            parseList.append(tmp)
        fileHandle.close()

    return parseList


def createOutput(outfile, outData):
    if not outfile.endswith('.md'):
        outfile += '.md'

    footnotes = []
    finalWriteList = []
    curFootNote = 1

    for data in outData:
        text = data.text.rstrip()
        footnotes.append(data.linkto)
        text += '[^%i]\n' % curFootNote
        finalWriteList.append(text)
        finalWriteList.append('\n------------\n')
        curFootNote += 1

    finalWriteList.pop()  # get rid of uneeded linebreak

    fileHandle = open(outfile, 'w')
    for line in finalWriteList:
        fileHandle.write(line)

    fileHandle.write("\n\n\n")

    for i, footnote in enumerate(footnotes):
        noteText = "[^%i]:[%s](%s)\n" % (i+1, footnote, footnote + '.html')
        fileHandle.write(noteText)

    fileHandle.close()


def main(output, inputs):
    parseResults = []

    for inFile in inputs:
        parseResults += parseInFile(inFile)

    parseResults.sort(key=lambda x: x.level)

    createOutput(output, parseResults)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'output',
        type=str,
        help="The file to be written",
        )
    parser.add_argument(
        'inputs',
        type=str,
        nargs='+',
        help="The files to be coalesced"
        )
    args = parser.parse_args()
    main(args.output, args.inputs)
