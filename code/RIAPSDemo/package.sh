set +e
mkdir -p pkg
cp -r python/* pkg
cp -r json-gen/* pkg						
export outputdir=`mktemp -d`
mkdir $outputdir/TransactiveEnergy
cp -r pkg/* $outputdir/TransactiveEnergy
export currentdir=`pwd`
cd  $outputdir
tar czvf TransactiveEnergy.tar.gz TransactiveEnergy/*
cd $currentdir
mv $outputdir/TransactiveEnergy.tar.gz .   

