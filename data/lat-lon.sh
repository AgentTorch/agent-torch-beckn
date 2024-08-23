#!/bin/bash

awk -F, '{ print $4 " " $5 " " $7 " MA" }' < downloads/house-details.csv |
	xargs -n 1 -P 16 -I {} sh -c '
   query=$(printf "%s " {});
   curl -s "https://nominatim.openstreetmap.org/search?q=${query// /%20}&format=json&polygon=1&addressdetails=1" | jq -r "[.[0].lat, .[0].lon] | @tsv"
  '
