"""
Parses a cmake file for defined ROS nodes
"""
from __future__ import print_function

import re
import os


class CMakeParser(object):
    """
    Parses a cmake file for defined ROS nodes
    """

    def __init__(self, pkg_path):
        self.exec_name = None
        self.pkg_path = pkg_path
        self.executables = dict()
        self.search_for_cpp_node()
        self.parser = list()
        self.project_name = ""
        for node in self.executables:
            print("Found node " + node)

    def search_for_cpp_node(self):
        """
        Method which searches the CMakeLists.txt for passible node entries
        """
        if os.path.isfile(self.pkg_path + "/CMakeLists.txt"):
            with open(self.pkg_path + "/CMakeLists.txt") as filecontent:
                self.lines = filecontent.readlines()
            linenumber = 0
            while linenumber < len(self.lines):
                self.parse_project_name(linenumber)
                self.parse_executables(linenumber)
                linenumber += 1
            self.remove_not_nodes()
            self.find_more_files()

    def parse_project_name(self, linenumber):
        """
        Method to parse the project name from CMAkeLists.txt as it may be needed to replace Params
        later on
        """
        match = re.search("(project\()(\S+)(\))", self.lines[linenumber])
        if match:
            self.project_name = str(match.group(2))

    def parse_executables(self, linenumber):
        """
        Method to parse add_executable entries.
        Skipping entries containing "#" as they are hopefully a comment

        TODO: What about one line definitions like add_executable(name file file)
        Maybe first check if regex: (add_executable\()(\S+)(((\s)(\S+))+)\) is match an if so
        Reading group3 (files) as string an cutting at whitespaces + check if directories
        """
        if "#" in self.lines[linenumber]:
            return
        match = re.search("(add_executable\()(\S+)+( ([^)]+))+\)", self.lines[linenumber])
        if match:
            self.exec_name = str(match.group(2))
            if "${PROJECT_NAME}" in self.exec_name:
                self.exec_name = self.exec_name.replace("${PROJECT_NAME}", self.project_name)
            cpp_files = list()
            cpp_file = str(match.group(4))
            if "${PROJECT_NAME}" in cpp_file:
                cpp_file = cpp_file.replace("${PROJECT_NAME}", self.project_name)
            if os.path.isfile(self.pkg_path + "/" + cpp_file):
                cpp_files.append(self.pkg_path + "/" + cpp_file)
            elif os.path.isdir(self.pkg_path + "/" + cpp_file):
                for filename in os.listdir(self.pkg_path):
                    cpp_files.append(self.pkg_path + "/" + filename)

            linenumber += 1
            while not ")" in self.lines[linenumber]:
                match_files = re.search("(\S+)", self.lines[linenumber])
                if match_files:
                    cpp_file = str(match_files.group(1))
                    if "${PROJECT_NAME}" in cpp_file:
                        cpp_file = cpp_file.replace("${PROJECT_NAME}", self.project_name)
                    if os.path.isfile(self.pkg_path + "/" + cpp_file):
                        cpp_files.append(self.pkg_path + "/" + cpp_file)
                    elif os.path.isdir(self.pkg_path + "/" + cpp_file):
                        for filename in os.listdir(self.pkg_path):
                            cpp_files.append(self.pkg_path + "/" + filename)

                linenumber += 1
            self.executables[self.exec_name] = cpp_files
            return

        match = re.search("(add_executable\()(\S+)", self.lines[linenumber])
        if match:
            self.exec_name = str(match.group(2))
            if "${PROJECT_NAME}" in self.exec_name:
                self.exec_name = self.exec_name.replace("${PROJECT_NAME}", self.project_name)
            cpp_files = list()
            linenumber += 1
            while not ")" in self.lines[linenumber]:
                match_files = re.search("(\S+)", self.lines[linenumber])
                if match_files:
                    cpp_file = str(match_files.group(1))
                    if "${PROJECT_NAME}" in cpp_file:
                        cpp_file = cpp_file.replace("${PROJECT_NAME}", self.project_name)
                    if os.path.isfile(self.pkg_path + "/" + cpp_file):
                        cpp_files.append(self.pkg_path + "/" + cpp_file)
                    elif os.path.isdir(self.pkg_path + "/" + cpp_file):
                        for filename in os.listdir(self.pkg_path):
                            cpp_files.append(self.pkg_path + "/" + filename)

                linenumber += 1
            self.executables[self.exec_name] = cpp_files

    def remove_not_nodes(self):
        """
        Method to remove executables which are not ros nodes.
        This is done by checking if one of the corresponding files contains ros::init()
        """
        delete_exec = []
        for key in self.executables:
            node = False
            for filename in self.executables[key]:
                content = open(filename, "r")
                if "ros::init" in content.read():
                    node = True
            if not node:
                delete_exec.append(key)

        for key in delete_exec:
            self.executables.pop(key)

    def find_more_files(self):
        """
        Method to find included files belonging to the node and which aren't in the CMakeList As
        this isn't trivial there are some assumptions made: all files belonging to the node are from
        the same package we won't look at includes from different packages if there is a Header from
        the same package included we assume that its location is
        package_name/include/package_name/name_of_class.cpp the pkghandler is always used for a
        package not for parent- or childdirectories of one. So the package name is the last part of
        the String the pkghandler is instanciated with.
        """
        # get package name
        pkg_name = self.pkg_path.split("/")[-1]
        for key in self.executables:
            add_list = list()
            for filename in self.executables[key]:
                with open(filename) as filecontent:
                    lines = filecontent.readlines()
                for line in lines:
                    match = re.search('(#include\ )(\<|\")(\S+)(\>|\")', line)
                    if match:
                        included_file = str(match.group(3))
                        if pkg_name in included_file:
                            filename = included_file.split("/")[-1]
                            headerpath = self.pkg_path + "/include/" + pkg_name + "/" + filename
                            if os.path.isfile(headerpath) and \
                                    headerpath not in self.executables[key]:
                                add_list.append(headerpath)
                            filecpp = filename.split(".")[0] + ".cpp"
                            cpppath = self.pkg_path + "/src/" + filecpp
                            if os.path.isfile(cpppath) and cpppath not in self.executables[key]:
                                add_list.append(cpppath)
            self.executables[key] += add_list