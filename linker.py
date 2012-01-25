#-*- coding: utf-8 -*-
from optparse import OptionParser
import re
import sys

__author__ = 'Vladimir Ignatyev'

re_import = re.compile('\$import\s*\(\s*[\'\"]([^\)]+)[\'\"]\s*\)')

def classnames_from_import(line):
    return re.findall(re_import, line)

def filepath_from_classname(classname):
    chunks ='/'.join(classname.split('.'))
    filepath = chunks.replace('/*', '.js')
    return filepath

def get_filtered_file_and_imports_list(filename):
    imports_list = []
    file_lines = []

    # Python 3 requires the file encoding to be specified
    if (sys.version_info[0] < 3):
        file_handle = open(filename, 'r')
    else:
        file_handle = open(filename, 'r', encoding='utf8')

    for line in file_handle:
        imports = classnames_from_import(line)
        if len(imports):
            imports_list += imports
        else:
            if line.strip():
                file_lines += line

    return imports_list, file_lines


def build(input_file, output_file, class_path):
    imports_list, result_lines = get_filtered_file_and_imports_list(input_file)
    result_lines = [("\n\n//content of component file: %s\n" % input_file)] + result_lines
    included = []
    while len(imports_list) > 0:
        classname = imports_list[len(imports_list)-1]
        imports_list.pop()
        try:
            included.index(classname)
        except ValueError:
            included.append(classname)

            filename = class_path + filepath_from_classname(classname)
            new_imports, new_lines = get_filtered_file_and_imports_list(filename)
            imports_list += new_imports
            result_lines = ([("\n\n//content of file: %s\n" % filename)] + new_lines) + result_lines

    output = open(output_file, 'w')
    output.writelines(result_lines)


def main():
    parser = OptionParser()
    parser.add_option("-i", "--input_file", dest="input_file", help="input .js file to link", metavar="FILE")
    parser.add_option("-o", "--output_file", dest="output_file", help="output .js file", metavar="FILE")
    parser.add_option("-c", "--class_path", dest="class_path", help="root directory for searching paths with delimeter at the end")
    
    (options, args) = parser.parse_args()

    build(options.input_file, options.output_file, options.class_path)

main()