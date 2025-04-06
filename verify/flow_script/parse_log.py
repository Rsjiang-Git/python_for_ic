
import re 
import sys 
import argparse 
from multiprocessing import Process 
from multiprocessing import Pool, Lock 

import time 
import os
import random 
import subprocess 
import json 

class Parse_Log():
    def __init__(self, **kwargs):
        for key ,value in kwargs.items():
            setattr (self,key,value)
            self.prj_root = None 
            self.errors_pattern = {}
            self.errors_info = {}
            self.lock = Lock()
        
    def initial_parse(self):
        self.prj_root = os.environ.get("PRJ_ROOT")
        self.file_path = self.prj_root +"/" + "verify" + "/" + "pattern" + "/" + "error_pattern.json"
        try:
            with open(self.file_path, "r", encoding ="utf-8") as f : 
                 self.errors_pattern = json.load (f)
        except Exception as e :
              print ("error_pattern.json:", str(e))
    
    def parse_simulation_log(self):
        self.lock.acquire()
        test_name = self.tc
        try:
            with open (self.parser_log ,"r", encoding ="utf-8") as f :
                data = f.readlines()
                for content in data :
                    for pattern_name, pattern in self.errors_pattern.items():
                        matches = re.search (pattern, content, re.I)
                        content = content.strip()
                        if(re.search("UVM_ERROR :.*(\d+)|(UVM_FATAL :.*(\d+))",content) == None):
                            if matches:
                                if test_name not in self.errors_info:
                                    self.errors_info[test_name] = {}
                                    self.errors_info[test_name][pattern_name] = content 

                        json_string = json.dumps(self.errors_info, indent = 4)
                        report_file = self.result_dir + "/" + "test_result.log" 

                        with open(report_file ,"a") as file:
                            file.write(json_string + "\n")
                        result_file = self.result_dir +"/"+"result.log"
                        if not self.errors_info[self.tc]:
                            with open(result_file, "a") as file :
                                file.write( self.tc +" pass_status "+ self.seed)
                        else:
                            with open (result_file, "a") as file:
                                if ("error" not in self.errors_info [self.tc]):
                                    file.write(self.tc + "fail_status" + self.seed +" "+ self.errors_info[self.tc]["fatal"]+"\n")

                                elif ("fatal" not in self.errors_info[self.tc]): 
                                     file.write(self.tc + "fail_status" + self.seed +" "+ self.errors_info[self.tc]["error"]+"\n")
                                else:
                                    file.write(self.tc + "fail_status" + self.seed +" "+ self.errors_info[self.tc]["error"]+"\n")
        except Exception as e:
            print ("parse_log error :", str(e))
      
    # def parse_log (self):
    #     self.lock.acquire()
    #     test_name = self.test_json +"."+ self.tc + "_"+ self.seed
    #     try:
    #         with open(self.parse_log ,"r", encoding= "utf-8") as f: 
    #             data = f . readlines ()
    #             for content in data :
    #                 for pattern_name , pattern in self.errors_pattern.items():
    #                     matchs = re.findall( pattern ,content)
    #                     if matchs:
    #                         if test_name not in self.errors_info:
    #                             self.errors_info[test_name]= {}
    #             self.errors_info[test_name][pattern_name]= matchs 
                
    #         #json string 
    #         json_string = json.dumps(self.errors_info,indent = 4)
    #         with open(self.result_dir, "a") as file:
    #             file.write (json_string + "\n")
    #     except Exception as e:
    #         print ("parse_log error :", str(e))
    #     self.lock.release ()
        
        
def main():
    parser= argparse.ArgumentParser()
    parser.add_argument("-seed", default="", help ="random seed select")
    parser.add_argument("-tc", default="", help="test name , only one test name")
    parser.add_argument("-test_json", default="", help=" test_file only one test file")
    parser.add_argument("-parser_log", default="", help="parser_log")
    parser.add_argument("-result_dir", default="", help="result_directory")
    cmd_args = parser.parse_args()
    args_dict = vars(cmd_args)
    parse_log_ins = Parse_Log(**args_dict)
    parse_log_ins.initial_parse()
    parse_log_ins.parse_simulation_log()
            
            


if __name__== "__main__" :
    main()
