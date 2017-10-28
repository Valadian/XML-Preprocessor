import os
import platform
import re


class Preprocessor():
    def __init__(self):
        self.original_file = {}
        self.processed_file = {}
        self.sys_vars = self.init_sys_vars()

    def load(self, file_path):
        self.original_file["file"] = file_path
        try:
            with open(file_path, "r") as original_file:
                self.original_file["content"] = original_file.read().split("\n")
            return 0
        except:
            return -1

    def init_sys_vars(self):
        sys_vars = {}
        sys_vars["ARCH"] = platform.architecture()[0]
        sys_vars["SOURCE"] = os.path.abspath(__file__)
        sys_vars["CURRENT"] = os.getcwd()
        return sys_vars

    def parse_include(self, xml_str):
        include_regex = r"(<\?include([\w\s\\/.:]+)\s*\?>)"
        matches = re.findall(include_regex, xml_str)
        for group_inc, group_xml in matches:
            inc_file_path = group_xml.strip()
            with open(inc_file_path, "r") as inc_file:
                inc_file_content = inc_file.read()
                inc_file_content = self.parse_include(inc_file_content)
                xml_str = xml_str.replace(group_inc, inc_file_content)
        return xml_str

    def parse_env_var(self, xml_str):
        envvar_regex = r"(\$\(env\.(\w+)\))"
        matches = re.findall(envvar_regex, xml_str)
        for group_env, group_var in matches:
            xml_str = xml_str.replace(group_env, os.environ[group_var])
        return xml_str

    def parse_sys_var(self, xml_str):
        sysvar_regex = r"(\$\(sys\.(\w+)\))"
        matches = re.findall(sysvar_regex, xml_str)
        for group_sys, group_var in matches:
            if group_var not in self.sys_vars:
                raise Exception("Wrong System Variable: " + group_var)
            xml_str = xml_str.replace(group_sys, self.sys_vars[group_var])
        return xml_str

    def preprocess(self):
        self.processed_file["content"] = []
        for index, xml_str in enumerate(self.original_file["content"]):
            xml_str = self.parse_include(xml_str)
            xml_str = self.parse_env_var(xml_str)
            xml_str = self.parse_sys_var(xml_str)
            #TODO: Custom Variables $(var.CusVar)
            #TODO: Conditional Statements <?if ?>, <?ifdef ?>, <?ifndef ?>, <?else?>, <?elseif ?>, <?endif?>
            #TODO: Errors and Warnings <?error?>, <?warning?>
            #TODO: Iteration Statements <?foreach?>
            self.processed_file["content"].extend(xml_str.split("\n"))

    def save(self, file_path):
        self.processed_file["file"] = file_path
        try:
            with open(file_path, "w") as processed_file:
                processed_file.write("\n".join(self.processed_file["content"]))
            return 0
        except:
            return -1
