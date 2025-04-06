import os
import re
import sys
import argparse
from argparse import Action
from multiprocessing import Process
from multiprocessing import Pool
import time
from time import sleep
import random
import subprocess
import json
import datetime




class VerifyFlow():
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
             setattr (self, key, value)
             self.prj_root = None
             self.work_dir = None 
             self.verify = None
             self.compile_dict = {} 
             self.test_dict = {}
             self.compile_file = []
             self.compile_name = [] 
             self.test_name = [] 
             self.testfile_name = []
             self.test_compile_file = []
             self.test_compile_name = []
             self.final_test_dict = {}
             self.output_dir = ""
    
             
    def initial_flow(self):
        
        # self.prj_root = os.environ.get("PRJ_ROOT")
        self.prj_root = "/mnt/hgfs/my_share/python_for_ic/v3"
        self.work_dir = self.prj_root + "/" + "work"
        self.verify = self.prj_root + "/" + "verify"
        if(self.test_json == "" and self.rerun_fail == ""):
            print (" command error ")
            exit ()
        if(self.tc == "" and self.rerun_fail == ""):
            work_location = self.work_dir + "/" + "regression" 
        elif(self.rerun_fail != ""):
            work_location = self.work_dir + "/" + "rerun_fail"
        else:
            work_location = self.work_dir 
            print("work_location :"+ work_location)
            
        self.work_dir = work_location 
            
        if (os.path.exists(work_location) == False):
            os.makedirs(work_location)
        if (os.path.exists(work_location + "/report/") == False):
            os.makedirs (work_location + "/report/")
        if (os.path.exists(work_location + "/compile_location/") == False):
            os.makedirs(work_location + "/compile_location/")
            
    def create_rc_list(self, file_path):
     
        dir_name = os.path.dirname(file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        if not os.path.isfile(file_path):
            with open(file_path, " w ") as file:
                file.write ("")
                
    def is_compile_foreign(self):
        directory_name = self.verify + "/" + "compile_c"
        dir_list = []
        include_dir = ""
        source_dir = ""
        if( self.compile_c == True):
            for filename in os.listdir(directory_name):
                 if filename.endswith (".json"):
                    file_path = os.path.join (directory_name, filename)
                    compile_json = os.path.splitext (filename)[0]
                    try :
                        with open(file_path ,"r", encoding= "utf-8") as f:
                            data = json.load(f)
                            include_dir = data["inc_dir"]
                            source_dir = data["src_dir"]
                            self.output_dir = data["output_dir"]
                    except Exception as e :
                        print ("compile json error :",str(e))
                        for filename in os.listdir(source_dir):
                            if filename.endswith (".c"):
                                file_path = os.path.join(directory_name ,filename)
                                dir_list.append (file_path)
            c_file = " ".join(dir_list)
            cmd = " gcc -std=c99 -w -pipe -fPIC -02 -g -shared -Wall -I ${VCS _HOME}/include"
            cmd = cmd + " -I {} {} -o {}".format(include_dir, c_file, self.output_dir + "/svuvm.so")
            os.system(cmd)           
       
    def get_compile_information(self):
       
        directory_name = self.verify + "/"+ "compile_list" 
        for filename in os.listdir( directory_name):
            if filename.endswith(".json"):
                file_path = os.path.join(directory_name, filename)
                compile_json = os.path.splitext (filename)[0] 
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.compile_dict[compile_json] = data 
                        # print(self.compile_dict)
                except Exception as e:
                    print (" compile json error:", str(e)) 
        for module_name, value in self.compile_dict.items():
            for compile_name, sub_value in value.items():
                self.compile_dict[module_name][compile_name]["verify_file"] = self.compile_dict[module_name][compile_name]["verify_file"].replace("{PRJ_ROOT}", self.prj_root)
                self.compile_dict[module_name][compile_name]["rtl_file"] = self.compile_dict[module_name][compile_name]["rtl_file"].replace("{PRJ_ROOT}", self.prj_root)
         
        print("copile_dict_test###########",self.compile_dict)
        for module_name ,value in self.compile_dict.items():
            print ("module_name=", module_name)
            self.compile_file.append(module_name)
            print (self.compile_file)
            for compile_name ,sub_value in value.items():
                self.compile_name.append(compile_name)
                if ( self.coverage != ""):
                    self.compile_dict[module_name][compile_name]["compile_opts"]+="-cg_coverage_control -1 -cm_ibsyv -cm_dir " + \
                self.work_dir + "/coverage/"+ self.test_json + " -cm cond + line + tgl + cond + fsm + branch -cm_noconst -cm_hier "+ self.coverage              
        print(self.compile_dict)

 
    def get_simulation_information(self):
        filter_dict = {}
        directory_name = self.verify + "/" + "test_list"
      
        for filename in os.listdir( directory_name):
            if filename.endswith(".json"):
                file_path = os.path.join(directory_name, filename)
                test_json = os.path.splitext (filename)[0] 
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        print(data)
                        if(self.tc != ""):
                            for key in data:
                                if key == self.tc:
                                    filter_dict[key] = data[key]
                            data.clear()
                            data.update(filter_dict)
                        self.test_dict[test_json] = data 
                        print(self.test_dict)
                except Exception as e:
                    print (" test json error:", str(e)) 
                    
        for module_name, value in self.test_dict.items():
            select_seed_list = []
            for test_name ,sub_value in value.items():
                self.test_dict[module_name][test_name]["sim_opts"] += self.run_opts 
                self.test_dict[module_name][test_name]["seed"] = []
                if (len( select_seed_list) == 0):
                    for i in range (int(self.repeat)):
                        if (self.repeat == 1 and self.seed != ""):
                            seed = self.seed 
                        else:
                            seed = str(random.randint(1,1000000000000000))
                            self.test_dict[module_name][test_name]["seed"].append(seed)
                else:                
                    self.test_dict[module_name][test_name]["seed"]= select_seed_list 
                    
        print("test_dict###############",self.test_dict)
         

    def create_compile_directory(self):
        for module_name, value in self.compile_dict.items():
            if (os.path.exists(self.work_dir + "/compile_location/" + module_name ) == False):
                os.makedirs(self.work_dir + "/compile_location/" + module_name )
            for compile_name ,sub_value in value.items():
                if(os.path.exists(self.work_dir + "/compile_location/" + module_name + "/" + compile_name) == False):
                    os.makedirs(self.work_dir + "/compile_location/" + module_name + "/" + compile_name)
                location = self.work_dir + "/compile_location/" + module_name + "/" + compile_name 
                if (self.debug == True):
                    print ("compile location:"+location)
                print ("compile location:" + location)
                compile_f = open(location + "/compile.csh", "w+")
                verify_file = self.compile_dict[module_name][compile_name]["verify_file"]
                rtl_file = self.compile_dict[module_name][compile_name]["rtl_file"]
                compile_opts = self.compile_dict[module_name][compile_name]["compile_opts"]
                self.compile_dict[module_name][compile_name]["location"] = location
                data = "vcs -full64 -ntb_opts uvm-1.2 +v2k -sverilog -kdb -error=noMPD +libext+.v+.vlib+.sv+.svh+.vp+.sva+.svp -P ${VERDI_HOME}/share/PLI/VCS/LINUX64/novas.tab ${VERDI_HOME}/share/PLI/VCS/LINUX64/pli.a -Mupdate -lca -debug_access+f -CFLAGS -DVCS +define+UVM_PACKER_MAX_BYTES=1500000 +define+UVM_DISABLE_AUTO_ITEM_RECORDING " \
+verify_file + " "+ rtl_file + " "+ compile_opts + " -l compile.log \n"
                compile_f.write(data)
                compile_f.close ()
                os.system("cd "+location+";chmod 777 compile.csh;")
        
    def create_simulation_directory(self, timestr): 
       
        for test_module_name, value in self.test_dict.items():
            self.final_test_dict[test_module_name] = {}
        
            if(os.path.exists(self.work_dir + "/report/" + test_module_name + "_"+ timestr) == False):
                os.makedirs( self.work_dir + "/report/"+ test_module_name + "_" + timestr)
            test_result_report_f = open(self.work_dir + "/report/" + test_module_name + "_" + timestr + "/test_run.log","w+")

            result_report_f = open(self.work_dir +"/report/"+test_module_name + "_" + timestr + "/result.log", "w+")
            result_report_f.write("TEST_FILE:"+ test_module_name + "\n")
            result_report_f.write("TEST_NAME"+ 21*' ' + "STATUS" +24*" "+"SEED"+26*" "+"FAIL REASON" + 20*" " +"\n")

            if(os.path.exists(self.work_dir + "/" + test_module_name) == False):
                os.makedirs(self.work_dir +"/" + test_module_name)

            for test_name, sub_value in value.items():
                location = ""
                for seed in sub_value["seed"]:
                    if(self.repeat == 1 and self.seed == "" and self.rerun_fail == ""):
                        if(os.path.exists(self.work_dir + "/" +test_module_name + "/" + test_name) == False):
                            os.makedirs( self.work_dir + "/" + test_module_name + "/" + test_name)
                        location = self.work_dir +"/" + test_module_name + "/" + test_name 
                       
                    else:
                        if(os.path.exists(self.work_dir +"/" +test_module_name + "/" + test_name+"_"+seed) == False):
                            os.makedirs( self.work_dir +"/" + test_module_name  + "/" + test_name + "_" + seed)
                        location = self.work_dir + "/" + test_module_name  + "/" + test_name + "_" +seed
                    
                    if(self.debug == True):
                        print("location: "+ location)
                  
                    if(self.repeat == 1 and self.seed == "" and self.rerun_fail == ""):
                        final_test_name =  test_name
                        self.final_test_dict[test_module_name][final_test_name] = {}
                        self.final_test_dict[test_module_name][final_test_name]["location"] = location
                        self.final_test_dict[test_module_name][final_test_name]["compile_file"] =  self.test_dict[test_module_name][test_name]["compile_file"]
                        self.final_test_dict[test_module_name][final_test_name]["compile_name"] =  self.test_dict[test_module_name][test_name]["compile_name"]
                        self.final_test_dict[test_module_name][final_test_name]["seed"] = seed
                        self.final_test_dict[test_module_name][final_test_name]["sim_opts"] =  self.test_dict[test_module_name][test_name]["sim_opts"]
                    
                    else:
                        final_test_name = test_name + "_" + seed
                        self.final_test_dict[test_module_name][final_test_name] = {}
                        self.final_test_dict[test_module_name][final_test_name]["location"] = location
                        self.final_test_dict[test_module_name][final_test_name]["compile_file"] =  self.test_dict[test_module_name][test_name]["compile_file"]
                        self.final_test_dict[test_module_name][final_test_name]["compile_name"] =  self.test_dict[test_module_name][test_name]["compile_name"]
                        self.final_test_dict[test_module_name][final_test_name]["seed"] = seed
                        self.final_test_dict[test_module_name][final_test_name]["sim_opts"] =  self.test_dict[test_module_name][test_name]["sim_opts"]
                    

                    compile_file = self.final_test_dict[test_module_name][final_test_name]["compile_file"]
                    compile_name = self.final_test_dict[test_module_name][final_test_name]["compile_name"]
                    sim_opts   =  self.final_test_dict[test_module_name][final_test_name]["sim_opts"]
                    test_result_report_f.write(test_module_name + "." + final_test_name+"\n")

                    sim_file = open(location + "/run_sim.csh","w+")
                    run_verdi_file = open(location + "/run_verdi.csh","w+")

                    compile_location =  self.work_dir +"/compile_location/" + compile_file + "/" + compile_name
                    if(self.coverage != ""):
                       sim_opts += " -cm cond+line+tgl+fsm+branch +cov -cm_name " + final_test_name
                    if(self.is_compile_foreign == True):
                        sim_opts += " -sv_lib {}".format(self.output_dir +"/svuvm")
                    run_verdi_file.write("verdi -autoalias -ssf tb.fsdb -nologo &")   
                    sim_file.write(compile_location + "/simv +vcs+lic+wait +no_notifier +dontStopOnSimulError=1   \
                         +UVM_NO_RELNOTES +  ntb_random_seed =" +seed +  \
                         " " +sim_opts + " -l simulation.log\n")
                    # verdi_cmmand = "verdi -autoalias -top tb -sv -uvm  -ssf tb.fsdb - nologo &"
                    sim_file.close()
                    run_verdi_file.close()
                    os.system("cd "+location+";chmod 777 run_sim.csh;")
                    os.system("cd "+location+";chmod 777 run_verdi.csh;")


            test_result_report_f.close()
 
    def run_compile(self, run_compile_location):
        print("compile###############################")
        compile_result = subprocess.call("compile.csh;",cwd=run_compile_location,shell=True,stdout=subprocess.DEVNULL)
        print("compile_returncode",compile_result)
    
    def run_test(self, run_test_location, work_location, seed, test_module, test_name):
        print("run###############################")
        script_dir = self.verify + "/flow_script/parse_log.py"
        print("test_debug",script_dir)
        run_log_dir = " python3 " + script_dir 
        file_name = run_test_location + "/simulation.log"
        dir = run_log_dir + " -parser_log {} -result_dir {} -tc {} -test_json {} -seed {}".format (file_name, work_location, test_name, test_module,seed) 
        sim_result = subprocess.call("run_sim.csh;", cwd=run_test_location, shell=True) # , stdout = subprocess.DEVNULL
        print(dir)
        os.system(dir)

    def process_test(self, timestr):
        # compile 
        print("my_test")
        pool = Pool(self.process_number)
        if (self.only_sim == False):
            print("my_test1")
            for compile_module, value in self.compile_dict.items():
                for compile_name, sub_value in value.items():
                    compile_dir = self.compile_dict[compile_module][compile_name]["location"]
                    print("###############debug_dir",compile_dir)
                    pool.apply_async(self.run_compile,args =(compile_dir ,))
            pool.close()
            pool.join()
        # simulation 
        pool_sim = Pool(self.process_number)
        if (self.only_build == False):
            print ("TEST RUNING:")
            for test_module_name, value in self.final_test_dict.items():
                result_dir = self.work_dir + "/report/"+ test_module_name + "_" + timestr 
                for test_name, sub_value in value.items():
                    run_dir = self.final_test_dict[test_module_name][test_name]["location"]
                    run_seed = self.final_test_dict[test_module_name][test_name]["seed"]
                    pool_sim.apply_async(self.run_test, args=(run_dir, result_dir, run_seed, test_module_name, test_name))
            pool_sim.close()
            pool_sim.join()
            
            
    def get_coverage(self):
        
        dir_list = []
        if(self.coverage != ""):
            if (os.path.exists(self.work_dir + "/report/") == False ):
                os.makedirs(self.work_dir + "/report/")
            for root, dirs, files in os.walk(self.work_dir + "/coverage/"):
                print("dirs= ",dirs)
            for dir in dirs:
                if dir.endswith (".vdb"):
                    print(os.path.join(root, dir))
                    dir_list.append(os.path.join(root, dir))
                    vdb_dir = " ".join(dir_list)
                    print(dir_list)
                    cov_name = self.work_dir + "merge.vdb"
                    cmd = " urg -ful164 -dir {} -dbname {} -parallel".format(vdb_dir, cov_name)
                    os.system(cmd)
                    cmd = " verdi -cov -covdir {}".format(vdb_dir)
                    os.system (cmd)

    def print_report_message(self, timestr):
        fail_case_number = 0
        total_case_number = 0
        line_message = ""
        report_dir = self.work_dir + "/report/" + self.test_json + "_" + timestr + "/result.log"
        with open (report_dir, "r") as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                if(re.search (" fail_status ", line) != None ):
                    fail_case_number += 1
                    line_message = line 
                total_case_number += 1
        print(fail_case_number) 
        print(total_case_number)
        print ("simulation result:")
        if(fail_case_number !=0):
            print("TEST FAIL")
        else:
            print("TEST PASS")
        if(total_case_number >3):
            print("PASS RATE: "+ str((1- fail_case_number/(total_case_number -2))*100)+"%")
        else:
            if(line_message != ""):
                print("fail_meassge:"+line_message)
                
                
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-test_json", default="", help="test_file, only one test file") 
    parser.add_argument ("-tc", default="", help="test_name,only one test name") 
    parser.add_argument ("-run_opts", default="", help="add run option from command") 
    parser.add_argument ("-build_opts ", default= "", help="add build option from command")
    parser.add_argument("-repeat", default=1, help="repeat times")
    parser.add_argument("-process_number", default=5, help="process number")
    parser.add_argument("-seed", default = "", help="random seed select")
    parser.add_argument("-tag", default = "", help="select case with special tag")
    parser.add_argument("-rerun_fail", default = "", help="rerun the fail case in the result file")
    parser.add_argument("-coverage", default = "", help="coverage option")
    parser.add_argument("-only_sim", action = "store_true", help="only simulation")
    parser.add_argument("-only_build", action = "store_true", help="only build")
    parser.add_argument("-debug", action = "store_true", help="only for debug")
    parser.add_argument("-compile_foreign", action = "store_true", help="compile c c++")
    parser.add_argument("-timestr", default = "", help="time point")
    cmd_args = parser.parse_args()
    if(cmd_args.timestr ==""):
        now = datetime.datetime.now ()
        timestr = now.strftime("%Y%m%d-%H%M%S%f")[:-3]
    else:
        timestr = cmd_args.timestr
    args_dict= vars(cmd_args) 
    verify_flow_ins = VerifyFlow(**args_dict)
    verify_flow_ins.initial_flow()
    verify_flow_ins.get_compile_information() 
    verify_flow_ins.get_simulation_information() 
    verify_flow_ins.create_compile_directory()
    verify_flow_ins.create_simulation_directory(timestr) 
    verify_flow_ins.process_test(timestr)




if __name__== "__main__":
    main()
