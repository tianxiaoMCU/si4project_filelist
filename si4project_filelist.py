'''
This tool will generate source insight 4 project file list
from build output file (*.dep)，then we can import the
file list in the source insight 4 project.
'''
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
import re

# 1、Find .dep file
projectfilename = ''
sourcefile = ''
outputfile = ''

for entry in os.scandir():
    if entry.is_file():
        if entry.name.endswith('.eww'):
            projectfilename = entry.name

            # find current target
            wsdtfile = os.path.join(os.getcwd(), 'settings')
            wsdtfile = os.path.join(wsdtfile, entry.name.replace('.eww', '.wsdt'))

            if os.path.exists(wsdtfile):
                tree = ET.ElementTree(file=wsdtfile)
                ConfigDictionary = tree.find('ConfigDictionary')
                CurrentConfigs = ConfigDictionary.find('CurrentConfigs')
                TargetName = CurrentConfigs.find('Project').text.split('/')[1]

                depfilename = CurrentConfigs.find('Project').text.split('/')[0] + '.dep'
                if os.path.exists(depfilename):
                    sourcefile = depfilename
                    outputfile = os.path.splitext(projectfilename)[0]
                    break

            print('Please build the project once')
            input()
            sys.exit(0)

        elif entry.name.endswith('.uvproj') or entry.name.endswith('.uvprojx'):
            projectfilename = entry.name

            if entry.name.endswith('.uvproj'):
                uvoptfile = entry.name.replace('.uvproj', '.uvopt')
            elif entry.name.endswith('.uvprojx'):
                uvoptfile = entry.name.replace('.uvprojx', '.uvoptx')

            tree = ET.ElementTree(file=uvoptfile)

            # find current target
            for tag in tree.findall('Target'):
                TargetOption = tag.find('TargetOption')
                OPTFL = TargetOption.find('OPTFL')
                IsCurrentTarget = int(OPTFL.find('IsCurrentTarget').text)
                if IsCurrentTarget:
                    TargetName = tag.find('TargetName').text
                    break

            # find dep file of current target
            Extensions = tree.find('Extensions')
            if None == Extensions.findtext('nMigrate'):
                # ide is keil4
                depfilename = os.path.splitext(projectfilename)[0] + '_' + TargetName + '.dep'
                if os.path.exists(depfilename):
                    sourcefile = depfilename
                    outputfile = os.path.splitext(projectfilename)[0]

            else:
                # ide is keil5
                tree = ET.ElementTree(file=entry.name)
                for tag in tree.find('Targets').findall('Target'):
                    if tag.find('TargetName').text == TargetName:
                        TargetOption = tag.find('TargetOption')
                        TargetCommonOption = TargetOption.find('TargetCommonOption')
                        OutputDirectory = TargetCommonOption.find('OutputDirectory').text
                        OutputDirectory = os.path.normpath(os.path.join(os.getcwd(), OutputDirectory))

                        depfilename = os.path.splitext(projectfilename)[0] + '_' + TargetName + '.dep'
                        depfilename = os.path.join(OutputDirectory, depfilename)

                        if os.path.exists(depfilename):
                            sourcefile = depfilename
                            outputfile = os.path.splitext(projectfilename)[0]
                            break

            if '' == sourcefile:
                print('Please build the project once')
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
if projectfilename.endswith('.eww'):
    tree = ET.ElementTree(file=parsefile)
    for tag in tree.findall('configuration'):
        if TargetName == tag.find('name').text:
            output_tag = tag.find('outputs')

            for elem in output_tag.findall('file'):
                if elem.text.startswith('$PROJ_DIR$'):
                    if elem.text.endswith('.c') or elem.text.endswith('.s') or elem.text.endswith('.h'):
                        si4filelist.append(os.path.abspath(elem.text.replace('$PROJ_DIR$', os.getcwd()))+'\n')
            break

elif projectfilename.endswith('.uvproj') or projectfilename.endswith('.uvprojx'):
    for line in parsefile.readlines():
        m = re.search(r"^F \(.*?\)|^I \(.*?\)", line)
        if None != m:
            relpath = m.group(0)[3:-1]
            si4filelist.append(os.path.abspath(relpath)+'\n')
    si4filelist = set(si4filelist)

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

