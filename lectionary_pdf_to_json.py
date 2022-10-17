# PdfFile custom class
import PyPDF2

# Phase 1: Extract text from PDF file
class PdfFile:
    """Custom class for PDF files"""
    def __init__(self, input_filepath):
        self.object = open(input_filepath, 'rb')
        self.file_reader = PyPDF2.PdfFileReader(self.object)

    def get_num_pages(self):
        """Get the number of pages in the PDF file"""
        return self.file_reader.numPages

    def get_page(self, input_page_index):
        """Get the page object of a page with the specific input page index"""
        return self.file_reader.getPage(input_page_index)

    def get_page_text(self, input_page_index):
        """Get the text in a page with the specific input page index"""
        return self.get_page(input_page_index).extractText()

    def get_page_text_list(self):
        """Get a list of the text in the pages of the PDF file"""
        return [self.get_page_text(page_index) for page_index in range(self.get_num_pages())]

    def get_full_text(self):
        """Get the full text of the PDF file"""
        return ' '.join(self.get_page_text_list())

    def get_full_text_no_newline(self):
        """Get the full text of the PDF file with all newlines removed"""
        return self.get_full_text().replace('\n', ' ')

import os
SCRIPT_FOLDERPATH = os.path.dirname(os.path.realpath(__file__))

PDF_SOURCE_FILEPATH = os.path.join(SCRIPT_FOLDERPATH, 'YearC_21-22_ALL.pdf')
PDF_SOURCE_FILE = PdfFile(input_filepath=PDF_SOURCE_FILEPATH)
PDF_SOURCE_FILE_TEXT_NO_NEWLINE = PDF_SOURCE_FILE.get_full_text_no_newline()

# Phase 2: Extract date and date contents from PDF file text
import datetime
import calendar

def get_month_abbr_name_re_pattern_group(input_month):
    """Returns the regex pattern of a group searches for either the month_abbr or month_name attribute of a particular input month"""
    month_abbr = calendar.month_abbr[input_month]
    month_name = calendar.month_name[input_month]
    month_abbr_whitespace = '\s*'.join(month_abbr)
    month_name_whitespace = '\s*'.join(month_name)
    month_abbr_name_whitespace_list = [month_abbr_whitespace, month_name_whitespace]
    return '({})'.format('|'.join(month_abbr_name_whitespace_list))

def get_day_re_pattern_group(input_day):
    """Returns the regex pattern for an particular input day"""
    input_day = str(input_day)
    return '({})'.format('\s*'.join(input_day))

def convert_date_to_re_pattern(input_date):
    """Convert a given date to the date's respective regex pattern"""
    month = input_date.month
    day = input_date.day
    calendar_day_abbr_whitespace_list = ['\s*'.join(day_abbr) for day_abbr in calendar.day_abbr]
    calendar_day_abbr_re_pattern_group = '({})'.format('|'.join(calendar_day_abbr_whitespace_list))
    month_abbr_name_re_pattern_group = get_month_abbr_name_re_pattern_group(month)
    day_re_pattern_group = get_day_re_pattern_group(day)
    date_re_pattern_group_list = [calendar_day_abbr_re_pattern_group, month_abbr_name_re_pattern_group, day_re_pattern_group]
    return '\W*'.join(date_re_pattern_group_list)

def convert_date_list_to_re_pattern(input_list):
    """Convert a list of dates to the dates' respective regex pattern"""
    date_re_pattern_list = []
    for date in input_list:
        date_re_pattern = convert_date_to_re_pattern(date)
        date_re_pattern_list.append(date_re_pattern)
    return '({})'.format('|'.join(date_re_pattern_list))

def convert_month_abbr_name_to_month(input_str):
    """Convert a month_abbr/month_name to the month number"""
    month_abbr_name_list = list(calendar.month_abbr) + list(calendar.month_name)
    return month_abbr_name_list.index(input_str) % 13

def remove_char(input_str, input_char):
    """Returns the input string with the input character removed"""
    return input_str.replace(input_char, '')

def convert_date_str_to_date(input_str, input_in_memory_date):
    """Convert a string of a date to a date object"""
    input_str = remove_char(input_str, ' ')
    date_str_search = re.search('([A-Z][a-z]+)\W*([1-3]*[0-9])', input_str)
    output_month_abbr_name = date_str_search.group(1)
    output_month = convert_month_abbr_name_to_month(output_month_abbr_name)
    output_day = int(date_str_search.group(2))
    if input_in_memory_date.month == 12 and output_month == 1:
        output_year = input_in_memory_date.year + 1
    else:
        output_year = input_in_memory_date.year
    return datetime.date(output_year, output_month, output_day)

import re

def process_phase_2a(input_date, input_str):
    """Custom function to run phase 2a of the PDF scrapping"""
    date_list = [input_date, input_date + datetime.timedelta(days=1)]
    date_list_re_pattern = convert_date_list_to_re_pattern(date_list)
    date_list_re_search = re.search(date_list_re_pattern, input_str)
    if date_list_re_search:
        output_date_str = date_list_re_search.group(0)
        output_date = convert_date_str_to_date(output_date_str, input_date)
        output_content = input_str[date_list_re_search.end():].strip()
        return output_date_str, output_date, output_content

def replace_chars(input_str, input_dict):
    """Custom function to replace all char in an input string in the input dictionary's keys with the corresponding value in the dictionary"""
    output_str = input_str
    for char in input_dict.keys():
        new_char = input_dict[char]
        output_str = output_str.replace(char, new_char)
    return output_str

def push_to_dict(input_dict, input_key, input_val):
    """Custom function to append an input value to the list of the input key's value in a dictionary"""
    if input_key in input_dict.keys():
        input_dict[input_key].append(input_val)
    else:
        input_dict[input_key] = [input_val]

def process_phase_2b(input_dict, input_date_str, input_in_memory_date, input_in_memory_content):
    """Custom function to run phase 2b of the PDF scrapping"""
    value = input_in_memory_content.split(input_date_str)[0]
    lectionary_year_re_pattern = replace_chars('\W*'.join('(YearA'), {'(': '[(]?', 'A': '[ABC]'})
    value = re.split(lectionary_year_re_pattern, value, flags=re.I)[0].strip()
    push_to_dict(input_dict, input_in_memory_date, LectionaryItem(value))

def process_phase_2_to_4(input_str):
    """Custom function to run phase 2, 3 and 4 of the PDF scrapping"""
    date = datetime.date(2021, 11, 25)
    in_memory_date = None
    in_memory_content = None
    output_dict = {}
    while process_phase_2a(date, input_str):
        date_str, date, content = process_phase_2a(date, input_str)
        if in_memory_date:
            process_phase_2b(output_dict, date_str, in_memory_date, input_str)
        in_memory_date = date
        input_str = content
    push_to_dict(output_dict, date, LectionaryItem(content))
    return output_dict

# Phase 3: Classify date contents into feasts and daily readings
# Phase 4: Separate the feast name, readings, prayer, acclamation and color(s)
class LectionaryItem:
    """Custom class for a lectionary item"""
    def __init__(self, input_str):
        self.input_str = input_str
        self.is_feast = self.get_is_feast()
        if self.is_feast:
            self.feast = Feast(input_str)

    def get_is_feast(self):
        """Returns the regex match object for the lectionary item being a feast"""
        feast_header_list = ['Readings', 'PrayeroftheDay', 'GospelAcclamation', 'Color']
        feast_header_whitespace_list = ['\s*'.join(header) for header in feast_header_list]
        feast_re_pattern = '.+'.join(feast_header_whitespace_list)
        return bool(re.search(feast_re_pattern, self.input_str))

    def get_html(self):
        """Returns a the string representing the lectionary item when it's printed for HTML"""
        if self.is_feast:
            output_str = self.feast.get_html()
        else:
            output_str = '<h2>Daily Lectionary</h2>' + Readings(self.input_str).get_html()
        return output_str

    def __str__(self):
        """Returns a the string representing the lectionary item when it's printed"""
        if self.is_feast:
            output_str = str(self.feast)
        else:
            output_str = str(Readings(self.input_str))
        return output_str

class Feast:
    """Custom class for a feast item"""
    def __init__(self, input_str):
        self.input_str = input_str
        self.re_match = self.get_re_match()
        self.raw_content_list = self.get_raw_content_list()

    def get_re_match(self):
        """Returns the regex match object for the content being a feast"""
        header_list = ['Readings', 'PrayeroftheDay', 'GospelAcclamation', 'Color']
        header_whitespace_list = ['\s*'.join(header) for header in header_list]
        section_re_list = ['{}\W*(\w.+\S)'.format(header) for header in header_whitespace_list]
        re_pattern = '([A-Z].+\S)\s*{}'.format('\s*'.join(section_re_list))
        return re.search(re_pattern, self.input_str)

    def get_raw_content_list(self):
        """Gets the raw content list of the feast"""
        return self.re_match.groups()

    def get_content_dict(self):
        """Cleans up the content list"""
        raw_content_list = self.get_raw_content_list()
        full_header_list = ['Feast name', 'Readings', 'Prayer of the Day', 'Gospel Acclamation', 'Color']
        output_dict = {}
        for index in range(len(full_header_list)):
            header = full_header_list[index]
            raw_content = raw_content_list[index]
            if header in ['Prayer of the Day', 'Gospel Acclamation']:
                content = re.split('\s+[Oo][Rr]\s+(?=[A-Z])', raw_content)
            elif header == 'Readings':
                ev_re_compile = re.compile(EV_READING_PART_RE_PATTERN)
                ev_part_match = ev_re_compile.search(raw_content)
                ev_part_header_list = ev_re_compile.findall(raw_content)
                ev_part_content_list = ev_re_compile.split(raw_content)[1:]
                content = []
                if ev_part_match:
                    ev_part_list = []
                    for ev_part_content_index in range(len(ev_part_content_list)):
                        ev_part_content = ev_part_content_list[ev_part_content_index]
                        ev_part_list.append(ev_part_header_list[ev_part_content_index].strip())
                        read_respond_re_compile = re.compile('|'.join(['[A-Za-z\s]+' + '\s*'.join('Reading:'), '\s*'.join('Response:')]))
                        read_respond_match = read_respond_re_compile.search(ev_part_content)
                        read_respond_header_list = read_respond_re_compile.findall(ev_part_content)
                        read_respond_content_list = read_respond_re_compile.split(ev_part_content)[1:]
                        if read_respond_match:
                            for read_respond_content_index in range(len(read_respond_content_list)):
                                read_respond_part_list = []
                                read_respond_part_list.append(read_respond_header_list[read_respond_content_index].strip())
                                read_respond_part_list.append(str(Readings(read_respond_content_list[read_respond_content_index])))
                                ev_part_list.append(' '.join(read_respond_part_list))
                        else:
                            ev_part_list.append(str(Readings(ev_part_content)))
                    content.append('\n\n'.join(ev_part_list))
                else:
                    content = Readings(raw_content)
            else:
                content = raw_content
            output_dict[header] = content
        return output_dict

    def get_content_dict_html(self):
        """Cleans up the content list for HTML"""
        raw_content_list = self.get_raw_content_list()
        full_header_list = ['Feast name', 'Readings', 'Prayer of the Day', 'Gospel Acclamation', 'Color']
        output_dict = {}
        for index in range(len(full_header_list)):
            header = full_header_list[index]
            raw_content = raw_content_list[index]
            if header in ['Prayer of the Day', 'Gospel Acclamation']:
                content = re.split('\s+([Oo][Rr])\s+(?=[A-Z])', raw_content)
            elif header == 'Readings':
                ev_re_compile = re.compile(EV_READING_PART_RE_PATTERN)
                ev_part_match = ev_re_compile.search(raw_content)
                ev_part_header_list = ev_re_compile.findall(raw_content)
                ev_part_content_list = ev_re_compile.split(raw_content)[1:]
                content = []
                if ev_part_match:
                    ev_part_list = []
                    for ev_part_content_index in range(len(ev_part_content_list)):
                        ev_part_content = ev_part_content_list[ev_part_content_index]
                        ev_part_list.append('<h4>{}</h4>'.format(ev_part_header_list[ev_part_content_index].strip()))
                        read_respond_re_compile = re.compile('|'.join(['[A-Za-z\s]+' + '\s*'.join('Reading:'), '\s*'.join('Response:')]))
                        read_respond_match = read_respond_re_compile.search(ev_part_content)
                        read_respond_header_list = read_respond_re_compile.findall(ev_part_content)
                        read_respond_content_list = read_respond_re_compile.split(ev_part_content)[1:]
                        if read_respond_match:
                            for read_respond_content_index in range(len(read_respond_content_list)):
                                read_respond_part_list = []
                                read_respond_part_list.append('<h5>{}</h5>'.format(read_respond_header_list[read_respond_content_index].strip()))
                                read_respond_part_list.append(''.join(Readings(read_respond_content_list[read_respond_content_index]).get_html()))
                                ev_part_list.append(' '.join(read_respond_part_list))
                        else:
                            ev_part_list.append(Readings(ev_part_content).get_html())
                    content.append('\n\n'.join(ev_part_list))
                else:
                    content = Readings(raw_content).get_html()
            else:
                content = raw_content
            output_dict[header] = content
        return output_dict

    def get_html(self):
        """Returns a the string representing the feast when it's printed in HTML"""
        output_line_list = []
        content_dict = self.get_content_dict_html()
        for key in content_dict:
            content = content_dict[key]
            if key == 'Feast name':
                output_line_list.append('<h2>{}</h2>'.format(content))
            elif key == 'Readings':
                output_line_list.append('<h3>{}</h3>'.format(key))
                if type(content) == list:
                    output_line_list += content
                else:
                    output_line_list.append(content)
            else:
                output_line_list.append('<h3>{}</h3>'.format(key))
                if type(content) == list:
                    output_line_list += ['<p>{}</p>'.format(element) for element in content]
                else:
                    output_line_list.append('<p>{}</p>'.format(content))
            output_line_list.append('')
        return '\n'.join(output_line_list)

    def __str__(self):
        """Returns a the string representing the feast when it's printed"""
        output_line_list = []
        content_dict = self.get_content_dict()
        for key in content_dict:
            content = content_dict[key]
            if type(content) == list:
                output_line_list.append(key)
                output_line_list += content
            else:
                output_line_list.append(key)
                output_line_list.append(str(content))
            output_line_list.append('')
        return '\n'.join(output_line_list)

# Phase 6: Read text file for the list of books in the Bible
class TxtFile:
    """Custom class for txt files"""
    def __init__(self, input_filepath):
        self.object = open(input_filepath, 'r')
        self.text = self.get_text()

    def get_text(self):
        """Gets the text from the txt file"""
        return self.object.read()

    def get_line_list(self):
        """Gets the list of lines in the txt file"""
        return self.text.split('\n')

    def get_line_list_no_empty(self):
        """Gets the list of lines in the txt file with all blank lines removed"""
        return [line for line in self.get_line_list() if line]

    def get_bible_book_re_pattern(self):
        """Gets the regex pattern to match a book of the Bible"""
        bible_book_list = self.get_line_list_no_empty()
        bible_book_whitespace_list = []
        for bible_book in bible_book_list:
            bible_book_word_whitespace_list = ['\s*'.join(word) for word in bible_book.split()]
            bible_book_whitespace_list.append('\s'.join(bible_book_word_whitespace_list))
        return '|'.join(bible_book_whitespace_list)

    def get_book_lectionary_no_whitespace_kjv_dict(self):
        """Gets a dictionary mapping the books of the Bible in the lectionary (without spaces) to that of the KJV bible"""
        bible_map_list = self.get_line_list_no_empty()
        output_dict = {}
        for bible_map in bible_map_list:
            bible_map_match = re.search('(\S+): (.+)$', bible_map)
            output_dict[bible_map_match.group(1)] = bible_map_match.group(2)
        return output_dict

    def get_easter_vigil_reading_parts_re_pattern(self):
        """Gets the regex pattern to match a reading part for the Vigil of Easter"""
        reading_part_list = [remove_char(reading_part, ' ') for reading_part in self.get_line_list_no_empty()]
        reading_part_whitespace_list = ['\s*'.join(reading_part) for reading_part in reading_part_list]
        return '|'.join(reading_part_whitespace_list)

TXT1_SOURCE_FILEPATH = os.path.join(SCRIPT_FOLDERPATH, 'books_of_the_bible.txt')
TXT1_SOURCE_FILE = TxtFile(input_filepath=TXT1_SOURCE_FILEPATH)
BIBLE_BOOK_RE_PATTERN = TXT1_SOURCE_FILE.get_bible_book_re_pattern()

TXT2_SOURCE_FILEPATH = os.path.join(SCRIPT_FOLDERPATH, 'book_lectionary_no_whitespace_kjv_map.txt')
TXT2_SOURCE_FILE = TxtFile(input_filepath=TXT2_SOURCE_FILEPATH)
BIBLE_BOOK_NWS_KJV_DICT = TXT2_SOURCE_FILE.get_book_lectionary_no_whitespace_kjv_dict()

TXT3_SOURCE_FILEPATH = os.path.join(SCRIPT_FOLDERPATH, 'easter_vigil_reading_parts.txt')
TXT3_SOURCE_FILE = TxtFile(input_filepath=TXT3_SOURCE_FILEPATH)
EV_READING_PART_RE_PATTERN = TXT3_SOURCE_FILE.get_easter_vigil_reading_parts_re_pattern()

# Phase 7: Extract JSON file for the verses in the Bible
class JsonFile:
    """Custom class for JSON file"""
    def __init__(self, input_filepath):
        self.object = open(input_filepath, 'r')

    def get_book_to_verse_list_dict(self):
        """Get the dictionary mapping the Bible books and the list of verses"""
        verse_re_pattern = '"chapter":(\d+),"verse":(\d+),"text":"([^"]+)".+"book_name":"([^"]+)"'
        verse_re_compile = re.compile(verse_re_pattern)
        output_dict = {}
        for line in self.object.readlines():
            verse_re_match = verse_re_compile.search(line)
            chapter = int(verse_re_match.group(1))
            verse_number = int(verse_re_match.group(2))
            text, book_name = verse_re_match.group(3, 4)
            if chapter * verse_number == 1:
                output_dict[book_name] = []
            if verse_number == 1:
                output_dict[book_name] += [[]]
            output_dict[book_name][chapter - 1].append(text)
            assert len(output_dict[book_name]) == chapter
            assert len(output_dict[book_name][chapter - 1]) == verse_number
        return output_dict

JSON_SOURCE_FILEPATH = os.path.join(SCRIPT_FOLDERPATH, 'kjv.json')
JSON_SOURCE_FILE = JsonFile(input_filepath=JSON_SOURCE_FILEPATH)
BIBLE_DICT = JSON_SOURCE_FILE.get_book_to_verse_list_dict()

class Readings:
    """Custom class for the lectionary item readings"""
    def __init__(self, input_str):
        self.input_str = input_str
        self.book_list, self.chapter_verse_str_list = self.get_book_chapter_verse_str_lists()
        self.content_list = self.get_content_list()

    def get_book_chapter_verse_str_lists(self):
        """Get a list of Bible books and a list of chapters and verses from the input string"""
        bible_re_compile = re.compile(BIBLE_BOOK_RE_PATTERN)
        bible_book_list = bible_re_compile.findall(self.input_str)
        bible_chapter_verse_str_list = [verses.strip() for verses in bible_re_compile.split(self.input_str)[1:]]
        return bible_book_list, bible_chapter_verse_str_list

    def get_content_list(self):
        """Get a list of contents from the list of chapters and verses"""
        output_list = []
        for index in range(len(self.book_list)):
            book = self.book_list[index]
            book_no_whitespace = book.replace(' ', '')
            input_book = BIBLE_BOOK_NWS_KJV_DICT[book_no_whitespace]
            chapter_verse_str = self.chapter_verse_str_list[index]
            chapter_verse_str_no_brackets = re.sub('[(][^)]*[)]|[{][^}]*[}]|\[[^\]]*\]', ' ', chapter_verse_str)
            chapter_verse_str_and_split = re.sub('and', ';', chapter_verse_str_no_brackets)
            chapter_verse_str_unstrip = re.sub('[A-Za-z]|(?<=[^\w\s])\s+|\s+(?=[^\w\s])', '', chapter_verse_str_and_split)
            chapter_verse_str_clean = re.sub('^\W+(?=\w)|(?<=\w)\W+$|^\W*$', '', chapter_verse_str_unstrip)
            chapter_verse_list = re.split(',|;|\s+', chapter_verse_str_clean)
            if input_book in BIBLE_DICT.keys():
                output_str_list = []
                book_chapter_list = BIBLE_DICT[input_book]
                if len(book_chapter_list) == 1:
                    chapter = 1
                else:
                    chapter = -1
                for chapter_verse in chapter_verse_list:
                    chapter_verse_range_match = re.search('([\w:]+)[^\w:]+([\w:]+)', chapter_verse)
                    chapter_verse_match = re.search('(\d+):(.+)', chapter_verse)
                    if chapter_verse_range_match:
                        chapter_list = []
                        verse_list = []
                        for chapter_verse_range_point in chapter_verse_range_match.groups():
                            chapter_verse_match = re.search('(\d+):(.+)', chapter_verse_range_point)
                            if chapter_verse_match:
                                chapter = int(chapter_verse_match.group(1))
                                verse = int(chapter_verse_match.group(2))
                                chapter_list.append(chapter)
                                verse_list.append(verse)
                            else:
                                verse = int(chapter_verse_range_point)
                                chapter_list.append(chapter)
                                verse_list.append(verse)
                        chapter_start, chapter_end = chapter_list
                        verse_start, verse_end = verse_list
                    elif chapter_verse_match:
                        chapter = int(chapter_verse_match.group(1))
                        chapter_start = chapter
                        chapter_end = chapter
                        verse_range_match = re.search('(\d+)\W+(\d+)', chapter_verse_match.group(2))
                        if verse_range_match:
                            verse_start = int(verse_range_match.group(1))
                            verse_end = int(verse_range_match.group(2))
                        else:
                            verse = int(chapter_verse_match.group(2))
                            verse_start = verse
                            verse_end = verse
                    elif re.search('^\d+$', chapter_verse):
                        if chapter == -1:
                            chapter = int(chapter_verse)
                            chapter_start = chapter
                            chapter_end = chapter
                            verse_start = 1
                            verse_end = len(book_chapter_list[chapter - 1])
                        else:
                            verse = int(chapter_verse)
                            verse_start = verse
                            verse_end = verse
                    for chapter in range(chapter_start, chapter_end + 1):
                        chapter_content_list = []
                        if chapter == chapter_start:
                            chapter_verse_start = verse_start
                        else:
                            chapter_verse_start = 1
                        if chapter == chapter_end:
                            chapter_verse_end = verse_end
                        else:
                            chapter_verse_end = len(book_chapter_list[chapter - 1])
                        for verse in range(chapter_verse_start, chapter_verse_end + 1):
                            if verse - 1 in range(len(book_chapter_list[chapter - 1])):
                                chapter_content_list.append('({}) {}'.format(verse, book_chapter_list[chapter - 1][verse - 1]))
                        output_str_list.append(' '.join(chapter_content_list))
                    if 'and' in chapter_verse_str_no_brackets:
                        chapter = -1
                output_str = '\n\n'.join(output_str_list)
                output_list.append(output_str)
            else:
                output_str = 'This reading is not supported..'
                output_list.append(output_str)
        return output_list

    def get_content_list_html(self):
        """Get a list of contents from the list of chapters and verses"""
        output_list = []
        for index in range(len(self.book_list)):
            book = self.book_list[index]
            book_no_whitespace = book.replace(' ', '')
            input_book = BIBLE_BOOK_NWS_KJV_DICT[book_no_whitespace]
            chapter_verse_str = self.chapter_verse_str_list[index]
            chapter_verse_str_no_brackets = re.sub('[(][^)]*[)]|[{][^}]*[}]|\[[^\]]*\]', ' ', chapter_verse_str)
            chapter_verse_str_and_split = re.sub('and', ';', chapter_verse_str_no_brackets)
            chapter_verse_str_unstrip = re.sub('[A-Za-z]|(?<=[^\w\s])\s+|\s+(?=[^\w\s])', '', chapter_verse_str_and_split)
            chapter_verse_str_clean = re.sub('^\W+(?=\w)|(?<=\w)\W+$|^\W*$', '', chapter_verse_str_unstrip)
            chapter_verse_list = re.split(',|;|\s+', chapter_verse_str_clean)
            if input_book in BIBLE_DICT.keys():
                output_str_list = []
                book_chapter_list = BIBLE_DICT[input_book]
                if len(book_chapter_list) == 1:
                    chapter = 1
                else:
                    chapter = -1
                for chapter_verse in chapter_verse_list:
                    chapter_verse_range_match = re.search('([\w:]+)[^\w:]+([\w:]+)', chapter_verse)
                    chapter_verse_match = re.search('(\d+):(.+)', chapter_verse)
                    if chapter_verse_range_match:
                        chapter_list = []
                        verse_list = []
                        for chapter_verse_range_point in chapter_verse_range_match.groups():
                            chapter_verse_match = re.search('(\d+):(.+)', chapter_verse_range_point)
                            if chapter_verse_match:
                                chapter = int(chapter_verse_match.group(1))
                                verse = int(chapter_verse_match.group(2))
                                chapter_list.append(chapter)
                                verse_list.append(verse)
                            else:
                                verse = int(chapter_verse_range_point)
                                chapter_list.append(chapter)
                                verse_list.append(verse)
                        chapter_start, chapter_end = chapter_list
                        verse_start, verse_end = verse_list
                    elif chapter_verse_match:
                        chapter = int(chapter_verse_match.group(1))
                        chapter_start = chapter
                        chapter_end = chapter
                        verse_range_match = re.search('(\d+)\W+(\d+)', chapter_verse_match.group(2))
                        if verse_range_match:
                            verse_start = int(verse_range_match.group(1))
                            verse_end = int(verse_range_match.group(2))
                        else:
                            verse = int(chapter_verse_match.group(2))
                            verse_start = verse
                            verse_end = verse
                    elif re.search('^\d+$', chapter_verse):
                        if chapter == -1:
                            chapter = int(chapter_verse)
                            chapter_start = chapter
                            chapter_end = chapter
                            verse_start = 1
                            verse_end = len(book_chapter_list[chapter - 1])
                        else:
                            verse = int(chapter_verse)
                            verse_start = verse
                            verse_end = verse
                    for chapter in range(chapter_start, chapter_end + 1):
                        chapter_content_list = []
                        if chapter == chapter_start:
                            chapter_verse_start = verse_start
                        else:
                            chapter_verse_start = 1
                        if chapter == chapter_end:
                            chapter_verse_end = verse_end
                        else:
                            chapter_verse_end = len(book_chapter_list[chapter - 1])
                        for verse in range(chapter_verse_start, chapter_verse_end + 1):
                            if verse - 1 in range(len(book_chapter_list[chapter - 1])):
                                chapter_content_list.append('({}) {}'.format(verse, book_chapter_list[chapter - 1][verse - 1]))
                        output_str_list.append('<p>{}</p>'.format(' '.join(chapter_content_list)))
                    if 'and' in chapter_verse_str_no_brackets:
                        chapter = -1
                output_str = '\n\n'.join(output_str_list)
                output_list.append(output_str)
            else:
                output_str = '<p>This reading is not supported..</p>'
                output_list.append(output_str)
        return output_list

    def get_html(self):
        """Gets the html to represent this reading/readings"""
        book_list, chapter_verse_str_list = self.get_book_chapter_verse_str_lists()
        content_list = self.get_content_list_html()
        output_str_list = []
        for index in range(len(book_list)):
            bible_book = book_list[index]
            chapter_verse_str = chapter_verse_str_list[index]
            content = content_list[index]
            output_str_list.append('<p><b>{} {}</b></p> {}'.format(bible_book, chapter_verse_str, content))
        return '\n\n'.join(output_str_list)

    def __str__(self):
        book_list, chapter_verse_str_list = self.get_book_chapter_verse_str_lists()
        content_list = self.get_content_list()
        output_str_list = []
        for index in range(len(book_list)):
            bible_book = book_list[index]
            chapter_verse_str = chapter_verse_str_list[index]
            content = content_list[index]
            output_str_list.append('{} {}\n\n{}'.format(bible_book, chapter_verse_str, content))
        return '\n\n'.join(output_str_list)

DATE_TO_LECTIONARY_ITEM_LIST_DICT = process_phase_2_to_4(PDF_SOURCE_FILE_TEXT_NO_NEWLINE)

import json
# Verify capturing of contents (Phase 5)
if __name__ == "__main__":
    output_dict = {'main': []}
    for date in DATE_TO_LECTIONARY_ITEM_LIST_DICT.keys():
        lectionary_item_list = DATE_TO_LECTIONARY_ITEM_LIST_DICT[date]
        lectionary_html_list = [remove_char(lectionary_item.get_html(), '\n') for lectionary_item in lectionary_item_list]
        date_to_html_list_dict = {'date': '{}/{:0>2}/{:0>2}'.format(date.year, date.month, date.day), 'html': lectionary_html_list}
        output_dict['main'].append(date_to_html_list_dict)
    with open('lectionary.json', 'w') as outfile:
        json.dump(output_dict, outfile)
