#!/bin/bash

BASE_DIR=`dirname $(readlink -f $0)`

phpunit $BASE_DIR/TestServiceTestCase.php