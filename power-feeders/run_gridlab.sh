DIR="$(pwd)"

# model's folders
TAXONOMY_DIR="Taxonomy_feeders"
TAXONOMY_NEW_DIR="modified_taxonomy"

export LIB_TAXONOMY="$DIR/$TAXONOMY_DIR"
export GLPATH="$LIB_TAXONOMY/InputGLMs/:$LIB_TAXONOMY/Weather/:$LIB_TAXONOMY/InputPlayers/:$GLPATH"
export PATH="$PATH:$GLPATH"


# record the current time
echo $(date) > time.log
start_t=$(date +"%s")

#gridlabd -v --debug -W $2 --bothstdout $1 -o model.xml --server -P $3 > /tmp/simulation.log
gridlabd -W $2 --bothstdout $1 -o model.xml --server -P $3 > /tmp/simulation.log

#gdb -ex=r --args  gridlabd -v --debug -W $2 --bothstdout $1 -o model.xml --server -P $3 

#valgrind --leak-check=full --show-leak-kinds=all gridlabd -v --debug -W $2 --bothstdout $1 -o model.xml --server -P $3 

#> /tmp/simulation.log 
# record the finish time

end_t=$(date +"%s")
echo $(date) >> time.log

# print the time spent in the simulation
runtime=$( echo "($end_t - $start_t)/60" | bc -l )
echo "\n== Runtime: " $runtime "minutes ==\n"
