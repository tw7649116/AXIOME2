from __future__ import print_function
from os import getcwd
from os.path import dirname, abspath, isfile
from shutil import copyfile
from collections import OrderedDict
import sys

def copySampleAxData():
    '''Copies the sample AXIOME data, updating the filepaths in the process'''
    #Finds the install directory, from which the res folder can be found
    cwd = getcwd()
    source_dir = dirname(abspath(__file__))
    sample_file = source_dir + "/res/sample/sample.ax"
    with open(sample_file, "r") as sample_in:
        with open("sample.ax", "w") as sample_out:
            for line in sample_in:
                sample_out.write(line.replace("@SOURCE_DIR@",source_dir).replace("@PWD@",getcwd()))
    mapping_file = source_dir + "/res/sample/sample_file_mapping.tsv"
    with open(mapping_file, "r") as mapping_in:
        with open("sample_file_mapping.tsv", "w") as mapping_out:
            for line in mapping_in:
                mapping_out.write(line.replace("@SOURCE_DIR@",source_dir))

def generateMappingTemplate(AxAnalysis):
    '''Generates a file mapping template based on loaded source submodules'''
    source_module = AxAnalysis.getModuleByName("source")
    source_inputs = OrderedDict()
    for submodule in source_module._submodules:
        AxIn = submodule._input
        for requirement in AxIn._values:
            if requirement["name"] not in source_inputs:
                source_inputs[requirement["name"]] = [(submodule.name, requirement["label"], requirement["required"])]
            else:
                source_inputs[requirement["name"]].append((submodule.name, requirement["label"], requirement["required"]))
    #Now we output this information into a tab separated value file
    with open("axiome_file_mapping_template.tsv", "w") as template:
        template.write("#File mapping template generated by AXIOME2\n")
        template.write("#Instructions:\n")
        template.write("# - sample_alias column contains UNIQUE sample names and must match sample metadata sheet\n")
        template.write("# - axiome_module column contains the name of the AXIOME module that will process the input file\n")
        template.write("# - all other columns are variables requested by AXIOME source modules, and only those columns required by the chosen module need to be filled out\n")
        source_module_string = "#Source module (module that requires this variable)\t"
        description_string = "#Description of variable\t"
        required_string = "#Required?\t"
        column_headers = "sample_alias\taxiome_submodule"
        for variable_name, submodules in source_inputs.iteritems():
			#We want sample_alias to be added in manually. It is mandatory.
			if variable_name != "sample_alias":
				source_add = []
				description_add = []
				required_add = []
				column_headers_add = []
				for info in submodules:
					source_add.append(info[0])
					description_add.append("%s: %s" % (info[0], info[1]))
					required_add.append("%s: %s" % (info[0], info[2]))
				source_module_string += "\t%s" % ", ".join(source_add)
				description_string += "\t%s" % "; ".join(description_add)
				required_string += "\t%s" % "; ".join(required_add)
				column_headers += "\t%s" % variable_name
        template.write("%s\n" % source_module_string)
        template.write("%s\n" % description_string)
        template.write("%s\n" % required_string)
        template.write("%s\n" % column_headers)
        print("Successfully written file 'axiome_file_mapping_template.tsv'", file=sys.stdout)
        print("This file can be opened and edited in a spreadsheet application (eg. Excel)", file=sys.stdout)

def metadataMappingCheck(metadata_mapping):

    print("Checking the metadata mapping file...", file=sys.stdout)
    
    if not isfile(metadata_mapping):
        print("ERROR: The provided metadata mapping '" + metadata_mapping + "' is not a file", file=sys.stderr)
        sys.exit(1)

    with open(metadata_mapping) as metaMap:
        
        header = metaMap.readline()
        categories = header.split("\t")
        numColumns = len(categories)
        if numColumns <= 1:
            print("ERROR: The mapping file '" + metadata_mapping + "' is not tab delimited", file=sys.stderr)
            sys.exit(1)

        if categories[0] != "#SampleID":
            print("ERROR: The first column must be #SampleID, was given: " + str(categories[0]), file=sys.stderr)
            sys.exit(1)

        lineNum = 1
        for line in metaMap:
            lineNum += 1
            newNumColumns = len(line.split("\t"))
            if newNumColumns != numColumns:
                print("ERROR: Line " + str(lineNum) + " has the incorrect number of columns", file=sys.stderr)
                print("Expected " + str(numColumns) + " columns, but found " + str(newNumColumns), file=sys.stderr)
                print(line, file=sys.stderr)
                sys.exit(1)

    print("Metadata mapping file is okay!", file=sys.stdout)