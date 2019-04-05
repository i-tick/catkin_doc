# The catkin\_doc project

Generally this package generates some documentation for ros nodes. For
each ros node declared in the package python nodes as well as cpp nodes
the project generates a documentation file.
## How to use:

Please consider that the generated files are currently put in the
directory from which you envoke the script.

How to create new or update documentation for a package:
```
catkin_doc "/path/to/your/package"
```

This functionality will only work correctly if the old documentation is
generated by this package.

Be aware that anything additional you wrote in the documentation except
explanations for the parameter, subscriber,... will most likely be
deleted.

The update funcionality will automatically find the documentation for
the nodes if the documentation is within the given package and you did
not change the filename. If no matching documentation is found you will
be asked to enter the path to and including the documentation file. If
no documentation exists you can press enter to generate a documentation.

The functionality will not delete any of explanations you made
concerning the entries by default. Instead if it finds a new comment in
the code it will ask you if you want to keep the old comment or replace
it. The same applies if an entry, e.g. a service which was in the old
docu could not be found in the current code. If the default value for
parameter or the msg type has changed it will simply replace the old one
but notify you on the terminal. The funcionality does not overwrite the
old documentation by default, instead it ouputs the resulting
documentation in a file "nodename./md" in the directory from which
you envoke the script.

## How it works:


This package consists of muliple python modules:

### node

The representation of the Ros Nodes.

### pkghandler

Provides funcionality to search a package for documentation files md,
python files and to check wheter a python file is a ros node.
Creates also python parser for each found node

### cmakeparser

Parses the CMakeList.txt for executables. Finds all files belonging to
one executable and checks wheter the executable is a rosnode. Creates
also Cpp parser for each found node.

### python

Contains the PythonParser. Parses the file given in constructor and
creates a Node representation for the file.

### cpp

Contains the CppParser. Parses a list of cpp files given in the
constructor and creates a node representation for the files.

### nodeconverter

Creates a md file for a given node.

### mdparser

Parses an md file and creates node representation for the file.

### nodecomparator

Compares two nodes and creates thrid node which contains the merged
information from both nodes
