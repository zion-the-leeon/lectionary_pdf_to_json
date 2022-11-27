import os
import re

class TxtFile:
    """Custom class for txt files"""
    def __init__(self, input_filepath):
        self.object = open(input_filepath, 'r')
        self.text = self.read_text()

    def read_text(self):
        """Reads the text from the txt file"""
        return self.object.read()

    def get_text(self):
        """Gets the text from the txt file"""
        return self.text

SCRIPT_FOLDERPATH = os.path.dirname(os.path.realpath(__file__))
BOOKLIST_SOURCE_FILENAME_LIST = ['niv_booklist_source.txt',
'esv_booklist_source.txt']

NIV_BOOKLIST_SOURCE_FILEPATH = os.path.join(SCRIPT_FOLDERPATH, BOOKLIST_SOURCE_FILENAME_LIST[0])
NIV_BOOKLIST_SOURCE_TXTFILE = TxtFile(input_filepath=NIV_BOOKLIST_SOURCE_FILEPATH)
NIV_BOOKLIST_SOURCE_TEXT = NIV_BOOKLIST_SOURCE_TXTFILE.get_text()
NIV_BOOKLIST = re.findall('"display":"([^"]+)"', NIV_BOOKLIST_SOURCE_TEXT)[::-1]

ESV_BOOKLIST_SOURCE_FILEPATH = os.path.join(SCRIPT_FOLDERPATH, BOOKLIST_SOURCE_FILENAME_LIST[1])
ESV_BOOKLIST_SOURCE_TXTFILE = TxtFile(input_filepath=ESV_BOOKLIST_SOURCE_FILEPATH)
ESV_BOOKLIST_SOURCE_TEXT = ESV_BOOKLIST_SOURCE_TXTFILE.get_text()
ESV_BOOKLIST = re.findall('<h3>([^<]+)</h3>', ESV_BOOKLIST_SOURCE_TEXT)[::-1]

assert(len(NIV_BOOKLIST) == len(ESV_BOOKLIST))

for booklist_index in range(len(NIV_BOOKLIST)):
    niv_book = NIV_BOOKLIST[booklist_index]
    esv_book = ESV_BOOKLIST[booklist_index]
    if niv_book == esv_book:
        lectionary_no_whitespace_book = niv_book.replace(' ', '')
    elif [niv_book, esv_book] == ['Psalm', 'Psalms']:
        lectionary_no_whitespace_book = 'Psalm'
    elif [niv_book, esv_book] == ['Song of Songs', 'Song of Solomon']:
        lectionary_no_whitespace_book = 'Song of Solomon'.replace(' ', '')
    else:
        print('NIV book: {}, ESV book: {}'.format(niv_book, esv_book))
    print('|{}|{}|{}|'.format(lectionary_no_whitespace_book, niv_book, esv_book))
