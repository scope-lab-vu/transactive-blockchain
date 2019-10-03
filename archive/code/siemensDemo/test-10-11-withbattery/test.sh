
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $DIR

for i in `ls $DIR/all_data/ | cut -d '_' -f2 |tr -d "*.csv"`;
do
echo "launching prosumer $i"
done
