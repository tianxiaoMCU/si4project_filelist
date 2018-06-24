'''
This tool will generate source insight 4 project file list
from IAR build output file (*.dep)，then we can import the
file list in the source insight 4 project.
'''
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

# 1、Find .dep file
projectfilename = ''
sourcefile = ''
outputfile = ''

for entry in os.scandir():
    if entry.is_file():
        if entry.name.endswith('.eww'):
            projectfilename = entry.name
            for entry in os.scandir():
                if entry.is_file() and entry.name.endswith('.dep'):
                    sourcefile = entry.name
                    outputfile = os.path.splitext(entry.name)[0]
                    break
            if '' == sourcefile:
                print('Please build the project once')
                input()
                sys.exit(0)

        elif entry.name.endswith('.uvproj') or entry.name.endswith('.uvprojx'):
            projectfilename = entry.name
            tree = ET.ElementTree(file=entry.name)
            tag_cfg_list = tree.find('Targets').findall('Target')
            listsize = len(tag_cfg_list)
            if listsize > 1:
                print("There are multiple configuration:")
                for index in range(0, listsize):
                    print("%d %s" % (index+1, tag_cfg_list[index].find('TargetName').text))

                print("Enter the index num to selete:")
                strin = input()
                if strin.isdigit():
                    selnum = int(strin)
                    if (selnum < (listsize + 1)):
                        TargetName = tag_cfg_list[selnum - 1].find('TargetName').text
                        TargetOption = tag_cfg_list[selnum - 1].find('TargetOption')
                        TargetCommonOption = TargetOption.find('TargetCommonOption')
                        OutputDirectory = TargetCommonOption.find('OutputDirectory').text
                        OutputDirectory = os.path.normpath(os.path.join(os.getcwd(), OutputDirectory))

                        depfilename = os.path.splitext(projectfilename)[0] + '_' + TargetName + '.dep'

                        for entry in os.scandir(OutputDirectory):
                            if entry.is_file() and entry.name == depfilename:
                                sourcefile = os.path.join(OutputDirectory, entry.name)
                                outputfile = os.path.splitext(entry.name)[0]
                                break
                        if '' == sourcefile:
                            print('Please build the project once')
                            input()
                            sys.exit(0)
                else:
                    print("Please restart the tool, the input shounld be a number")
                    input()
                    sys.exit(0)

            elif listsize == 1:
                TargetName = tag_cfg_list[selnum - 1].find('TargetName').text
                TargetOption = tag_cfg_list[selnum - 1].find('TargetOption')
                TargetCommonOption = TargetOption.find('TargetCommonOption')
                OutputDirectory = TargetCommonOption.find('OutputDirectory').text
                OutputDirectory = os.path.normpath(os.path.join(os.getcwd(), OutputDirectory))

                depfilename = projectfilename + '_' + TargetName + '.dep'

                for entry in os.scandir(OutputDirectory):
                    if entry.is_file() and entry.name == depfilename:
                        sourcefile = os.path.join(OutputDirectory, entry.name)
                        outputfile = os.path.splitext(entry.name)[0]
                        break
                if '' == sourcefile:
                    print('Please build the project once')
                    input()
                    sys.exit(0)
            else:
                print("Please check the project configuration")
                input()
                sys.exit(0)
            break

if '' == projectfilename:
    print('Can not find project file, enter any key to exit')
    input()
    sys.exit(0)

#2、parse the seleted dep file
parsefile = open(sourcefile, 'r')
si4filelist = []
print(projectfilename)
if projectfilename.endswith('.eww'):
    tree = ET.ElementTree(file=parsefile)
    tag_cfg_list = tree.findall('configuration')
    output_tag = ''

    listsize = len(tag_cfg_list)
    if listsize > 1:
        print("There are multiple configuration:")
        for index in range(0, listsize):
            print("%d %s" % (index+1, tag_cfg_list[index].find('name').text))

        print("Enter the index num to selete one:")
        strin = input()
        if strin.isdigit():
            selnum = int(strin)
            if (selnum < (listsize + 1)):
                output_tag = tag_cfg_list[selnum - 1].find('outputs')
        else:
            print("Please restart the tool, the input shounld be a number")
            input()
            sys.exit(0)

    elif listsize == 1:
        output_tag = tag_cfg_list[0].find('outputs')
    else:
        print("Please check the project configuration")
        input()
        sys.exit(0)

    for elem in output_tag.iterfind('file'):
        if elem.text.startswith('$PROJ_DIR$'):
            if elem.text.endswith('.c'):
                si4filelist.append(os.path.abspath(elem.text.replace('$PROJ_DIR$', os.getcwd()))+'\n')
            elif elem.text.endswith('.h'):
                si4filelist.append(os.path.abspath(elem.text.replace('$PROJ_DIR$', os.getcwd()))+'\n')

elif projectfilename.endswith('.uvproj') or projectfilename.endswith('.uvprojx'):
    print('Parse MDK dep file')

#3、save the lists
outputfile = open(outputfile + '.si4project_filelist.txt', 'w')
outputfile.write('; Source Insight Project File List\n')
outputfile.write('; Project Name: '+os.path.splitext(sourcefile)[0]+'\n')
outputfile.write('; Generated by si4project_filelist.py at '+datetime.now().strftime('%Y/%m/%d %H:%M:%S')+'\n')
outputfile.write('; Version=4.00.xxxx\n')
outputfile.write(';\n')
outputfile.write('; Each line should contain either a file name, a wildcard, or a sub-directory name.\n')
outputfile.write('; File paths are relative to the project source root directory.\n')
outputfile.write(';\n')
outputfile.writelines(si4filelist)
outputfile.close()

