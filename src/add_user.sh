#!/bin/bash
echo $2 > boo.temp
echo $2 >> boo.temp
ocpasswd -c /etc/ocserv/pass.wd $1 < boo.temp
rm boo.temp
