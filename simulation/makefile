# Configuration Section
TEST          := rkv_i2c_master_directed_interrupt_test
module_name   := i2c
PRJ_HOME      := $(shell echo $(CURDIR) | sed -r 's|/$(module_name)/.*|/$(module_name)|')
FILELIST_HOME := /mnt/hgfs/my_share/ic_prj/examples/uvm_template/$(module_name)
SEED          := $(shell head -4 /dev/urandom | od -N 4 -D -A n | awk '{gsub(/ /,"")}1')

# Coverage Options
cm            := -cm line+cond+tgl+fsm+branch+assert
cm_name       := -cm_name $(TEST)_$(SEED)
cm_dir        := -cm_dir $(PRJ_HOME)/vdb/$(TEST)/simv.vdb
merge_cov_file:= $(shell find $(PRJ_HOME)/vdb -name "*.vdb")

# Export Variables
export PRJ_HOME FILELIST_HOME

# Directory Paths
COMPILE_DIR   := $(PRJ_HOME)/compile/$(TEST)
SIMULATION_DIR:= $(PRJ_HOME)/simulation/$(TEST)_$(SEED)
SIGNAL_DIR    := $(PRJ_HOME)/signal_list/$(module_name)
VDB_DIR       := $(PRJ_HOME)/vdb

# Compile Options
compile_option := vcs \
    -kdb -lca \
    -full64 \
    -sverilog +v2k \
    -noIncrComp \
    -timescale=1ns/1ps \
    +lint=TFIPC-L \
    +vcs+lic+wait \
    $(cm_dir) \
    $(cm) \
    $(cm_name) \
    -f ../../filelist.f \
    -debug_access+all \
    +define+$(TEST) \
    -ntb_opts uvm-1.1 \
    -l compile.log

# Run Options
run_option := ./simv \
    +fsdb+force \
    -reportstats \
    $(cm_dir) \
    $(cm) \
    $(cm_name) \
    -cm_nocasedef \
    +UVM_TESTNAME=$(TEST) \
    +ntb_random_seed=$(SEED) \
    -l simulation.log

# Phony Targets
.PHONY: test comp compile_clean run run_clean verdi cov_open cov_merge

# Test Target
test:
	@echo "Project Home: $(PRJ_HOME)"

# Clean Targets
compile_clean:
	@rm -rf $(COMPILE_DIR) $(PRJ_HOME)/vdCovLog/ $(PRJ_HOME)/urgReport \
        $(PRJ_HOME)/novas.* $(PRJ_HOME)/vdb/$(TEST)

run_clean:
	@rm -rf $(SIMULATION_DIR)/csrc $(SIMULATION_DIR)/simv.daidir \
        $(SIMULATION_DIR)/simv $(SIMULATION_DIR)/*.log \
        $(SIMULATION_DIR)/makefile $(SIMULATION_DIR)/*.fsdb* \
        $(SIMULATION_DIR)/ucli.key

# Compilation Target
comp: compile_clean
	@mkdir -p $(COMPILE_DIR) $(SIGNAL_DIR)
	@touch $(SIGNAL_DIR)/$(TEST).rc
	@cp $(PRJ_HOME)/makefile $(COMPILE_DIR)
	@cd $(COMPILE_DIR) && $(compile_option)

# Simulation Target
run: run_clean
	@mkdir -p $(SIMULATION_DIR)
	@cp $(PRJ_HOME)/makefile $(SIMULATION_DIR)
	@cd $(SIMULATION_DIR) && \
    ln -sf $(COMPILE_DIR)/simv.daidir simv.daidir && \
    ln -sf $(COMPILE_DIR)/csrc csrc && \
    ln -sf $(COMPILE_DIR)/simv simv && \
    $(run_option)

# Debug Targets
verdi:
	verdi -sv -uvm -f filelist.f \
    -ssf $(SIMULATION_DIR)/tb.fsdb \
    -sswr $(SIGNAL_DIR)/$(TEST).rc \
    -preTitle $(TEST)_$(SEED) -nologo &

cov_open:
	verdi -cov -covdir $(VDB_DIR)/simv_merge.vdb &

cov_merge:
	urg -full64 -dir $(merge_cov_file) \
    -dbname $(VDB_DIR)/simv_merge.vdb