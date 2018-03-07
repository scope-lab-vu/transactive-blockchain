#!/bin/bash

DIR=$(pwd)
echo $DIR

rm -rf $DIR/test-10-11-withbattery/prosumer*
$DIR/test-10-11-withbattery/testrun.sh
