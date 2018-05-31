#!/bin/bash


#
# script to get trades and quotes data
# tip for formatting symbol - @ symbol year month
# so for corn futures DEC 2018, it would be @CZ8Z
#

if [[ $# != 5 ]]; then
   echo "USAGE: $0 symbol database start-date end-date out-file"
   exit
fi

symbol=$1
database=$2

case "$2" in
'64')
    query_id="3/27/otq/49fb7507-e40d-48ba-bec7-fd0f1a514b18.otq"
    ;;
'75')
    query_id="3/27/otq/05c60b59-a915-4650-9dc1-e0291ca264a8.otq"
    ;;
'77')
    query_id="3/27/otq/5d1d92c3-22df-4b02-86fa-c3854d4b7d38.otq"
    ;;
'67')
    query_id="3/27/otq/b9a9762d-9994-4fcf-b99b-182f90ba87b0.otq"
    ;;
'66')
    query_id="3/27/otq/9941a0ac-1f49-42e4-90dd-7badd4e44fe4.otq"
    ;;
*)
    echo "database $database is not supported"
    exit
    ;;
esac

T="180000"

start_time=$3$T
end_time=$4$T

out_file=$5

curl --tr-encoding -o $out_file -u ddon@limebrokerage.com:DDsvidCloud42 --data "{\"context\":\"DEFAULT\",\"query_type\":\"otq\",\"otq\":\"$query_id\",\"s\":\"$start_time\",\"e\":\"$end_time\",\"timezone\":\"America/New_York\",\"response\":\"csv\",\"format\":[\"order=TIMESTAMP|PRICE|SEQ_NUM|SIZE|ASK_SIZE_IMPLIED|ASK_SIZE_OUTRIGHT|ASK_PRICE|ASK_SIZE|BID_SIZE_IMPLIED|BID_SIZE_OUTRIGHT|BID_PRICE|BID_SIZE\",\"TIMESTAMP=%|America/New_York|%Y-%m-%d %H:%M:%S.%q\",\"ASK_PRICE=%.10f\",\"BID_PRICE=%.10f\",\"PRICE=%.10f\"] ,\"otq_params\":\"SYMBOL=$symbol.$database\" }" https://cloud.onetick.com:443/omdwebapi/rest --header "Content-Type:application/x-gzip"
