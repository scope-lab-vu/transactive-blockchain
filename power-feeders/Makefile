
# model's name
MODEL = R1_1247_3_t6


# Script to customize the
create_custom = config_model.py

DIR=$(shell pwd)

# model's folders
TAXONOMY_DIR = Taxonomy_feeders
TAXONOMY_NEW_DIR = modified_taxonomy

MODEL_DIR = $(DIR)/$(TAXONOMY_NEW_DIR)/$(MODEL)

# files
ORIGINAL_GLM = $(DIR)/$(TAXONOMY_DIR)/$(MODEL).glm
NEW_GLM = $(MODEL_DIR)/$(MODEL)_custom.glm

# simulation's folder
SIM_DIR = simulations

SIM_NORMAL_DIR = $(DIR)/$(SIM_DIR)/$(MODEL)/normal
PLOT_DIR = $(DIR)/$(SIM_DIR)/$(MODEL)/plot


LABEL=$(shell grep 'name.*_reg_1' $(ORIGINAL_GLM) |  grep -o '[a-zA-Z0-9-]*_reg_1' | sed 's/_reg_1//g')


port=$(shell port=6267; \
	while [ "$$port" -lt "65535" ]; do \
		gld_clk=$$(wget http://localhost:$$port/raw/clock -q -O - ); \
		if [ -z "$$gld_clk" ]; then \
			echo "$$port"; \
			break ; \
		else \
			port=$$( echo "($$port + 1)" | bc -l ) ; \
		fi ; \
	done  \
)

options=$(port)


# customize the GLM file
custom: $(ORIGINAL_GLM) $(create_custom)
	if [ ! -d $(MODEL_DIR) ]; then mkdir -p $(MODEL_DIR); fi
	grep -v '^[/]*#' $(ORIGINAL_GLM) > $(NEW_GLM)
	sed -i 's/$(LABEL)[_]//g' $(NEW_GLM)
	sed -i 's/my_avg/current_price_mean_1h/g' $(NEW_GLM)
	sed -i 's/my_std/current_price_stdev_1h/g' $(NEW_GLM)
	python $(create_custom) -i  $(NEW_GLM)



simulate:
	${MAKE} -s custom
	${MAKE} -s list_objects
	cp events_normal events
	if [ ! -d $(SIM_NORMAL_DIR) ]; then mkdir -p $(SIM_NORMAL_DIR); fi
	python event_manager.py --port $(port) &
	sh run_gridlab.sh $(NEW_GLM) $(SIM_NORMAL_DIR) $(options)




list_objects: $(NEW_GLM)
	grep '^\s*name' $(NEW_GLM) | sed 's/[ ]*name//' | sed 's/;//' > list_gl_objects


extract_data: 
	python extract_data.py


plot:
	if [ ! -d $(PLOT_DIR) ]; then mkdir -p $(PLOT_DIR); fi
	ruby ./graph-feeders/glm2dot/glm2dot.rb $(NEW_GLM) $(PLOT_DIR)/plot.dot
	dot -Tpdf $(PLOT_DIR)/plot.dot -o $(PLOT_DIR)/plot.pdf
	neato $(PLOT_DIR)/plot.dot -Tpdf -o $(PLOT_DIR)/plot_b.pdf
	ruby ./graph-feeders/glm2dot/glm2dot.rb $(ORIGINAL_GLM) $(PLOT_DIR)/plot_original.dot
	dot -Tpdf $(PLOT_DIR)/plot_original.dot -o $(PLOT_DIR)/plot_original.pdf



.SILENT: all clean check_log simulate scenario_1 scenario_2 $(NEW_GLM) custom list_objects


clean:
	rm -fR $(DIR)/$(TAXONOMY_NEW_DIR)
	rm -fR $(DIR)/$(SIM_DIR)
	rm -fR $(PLOT_DIR)
	rm -fR ./records/
	rm -f /tmp/simulation.log
	rm -f *.xml warnings* error* *.csv *.log list_gl_objects *.pyc *~
	rm -f *.csv
	rm -f ./lib_parser_GLM/*.pyc
	rm -rf $(DIR)/$(TAXONOMY_NEW_DIR)/*
	rm -rf *.png *.pgf *.eps
	rm -rf events
	rm -rf *conflicted*
