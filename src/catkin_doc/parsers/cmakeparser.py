# -- BEGIN LICENSE BLOCK ----------------------------------------------
# Copyright (c) 2019, FZI Forschungszentrum Informatik
#
# Redistribution and use in source and binary forms, with or without modification, are permitted
# provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions
#    and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of
#    conditions and the following disclaimer in the documentation and/or other materials provided
#    with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to
#    endorse or promote products derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# -- END LICENSE BLOCK ------------------------------------------------

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
        self.project_name = ""
        self.search_for_cpp_node()
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
        Method to parse the project name from CMakeLists.txt as it may be needed to replace Params
        later on
        """
        match = re.search(r"(project\()(\S+)(\))", self.lines[linenumber])
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
        pattern = r'add_executable\(\s*(\S+)'
        match = re.search(pattern, self.lines[linenumber])
        if match:
            self.exec_name = str(match.group(1))
            # print(self.exec_name)
            if "${PROJECT_NAME}" in self.exec_name:
                self.exec_name = self.exec_name.replace("${PROJECT_NAME}", self.project_name)
            line = self.lines[linenumber].strip()
            while not ")" in self.lines[linenumber]:
                linenumber += 1
                line += " " + self.lines[linenumber].strip()

            line = re.sub(pattern, '', line)
            line = re.sub(r'\)[^)]*$', '', line)

            cpp_files_raw = line.strip().split(' ')

            cpp_files = list()

            for cpp_file in cpp_files_raw:
                if "${PROJECT_NAME}" in cpp_file:
                    cpp_file = cpp_file.replace("${PROJECT_NAME}", self.project_name)
                if os.path.isfile(self.pkg_path + "/" + cpp_file):
                    cpp_files.append(self.pkg_path + "/" + cpp_file)

            # print("Adding " + self.exec_name)
            self.executables[self.exec_name] = cpp_files

    def remove_not_nodes(self):
        """
        Method to remove executables which are not ros nodes.
        This is done by checking if one of the corresponding files contains ros::init()
        """
        delete_exec = []
        for key in self.executables:
            # print("Checking " + key)
            node = False
            for filename in self.executables[key]:
                content = open(filename, "r")
                # print(filename)
                if "ros::init" in content.read():
                    node = True
            if not node:
                delete_exec.append(key)

        for key in delete_exec:
            # print("Deleting " + key)
            self.executables.pop(key)

    def find_more_files(self):
        """
        Method to find included files belonging to the node and which aren't in the CMakeList
        As this isn't trivial there are some assumptions made:
          - all files belonging to the node are from the same package
          - we won't look at includes from different packages if there is a Header from the same
            package included we assume that its location is
              package_name/include/package_name/name_of_class.cpp
          - the pkghandler is always used for a package not for parent- or childdirectories of one.
            So the package name is the last part of the String the pkghandler is instanciated with.
        """
        # get package name
        pkg_name = self.pkg_path.split("/")[-1]
        for key in self.executables:
            for filename in self.executables[key]:
                with open(filename) as filecontent:
                    lines = filecontent.readlines()
                for line in lines:
                    match = re.search(r'(#include\ )(\<|\")(\S+)(\>|\")', line)
                    if match:
                        included_file = str(match.group(3))
                        if pkg_name in included_file:
                            filename = included_file.split("/")[-1]
                            headerpath = self.pkg_path + "/include/" + pkg_name + "/" + filename
                            if os.path.isfile(headerpath) and \
                                    headerpath not in self.executables[key]:
                                self.executables[key].append(headerpath)
                            filecpp = filename.split(".")[0] + ".cpp"
