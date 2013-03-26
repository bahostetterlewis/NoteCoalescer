from collections import namedtuple
from os.path import basename
from os.path import splitext
import argparse
import re
import markdown2

grouper = re.compile(
    "<!--Important(?P<level>[0-9]+)-->(?P<text>((?!<!--Important[0-9]+-->).)*)<!--EndImportant-->",
    re.MULTILINE | re.DOTALL,
    )

Note = namedtuple('Note', ['level', 'text', 'linkto', 'title'])


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
            text = it.group('text').strip()
            tmp = Note(
                level=it.group('level'),
                text=text,
                linkto=fileName,
                title=text.split('\n')[0].replace('#', '').replace('*', ''),
                )
            parseList.append(tmp)
        fileHandle.close()

    return parseList


def createOutput(outfile, outData):
    if not outfile.endswith('.html'):
        outfile += '.html'

    finalWriteList = []
    footnotes = []
    curFootNote = 1
    markdownFootnotes = []

    for data in outData:
        text = data.text.rstrip()
        text += '[^%i]\n' % curFootNote
        footnotes.append((data.title, data.linkto))
        finalWriteList.append(text)
        finalWriteList.append('\n------------\n')
        curFootNote += 1

    finalWriteList.pop()  # get rid of uneeded linebreak

    # turn footnotes into markdown style footnotes
    for i, footnote in enumerate(footnotes):
        noteText = "[^%i]:[%s](%s)\n" % (i+1, footnote[0], footnote[1] + '.html')
        markdownFootnotes.append(noteText)

    # combine all strings into a single string to be parsed
    finalText = "%s%s%s" % (
        ''.join(finalWriteList),
        '\n\n\n',
        ''.join(markdownFootnotes)
        )

    finalText = markdown2.markdown(finalText, extras=['footnotes'])

    fileHandle = open(outfile, 'w')
    fileHandle.write(finalText)
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
