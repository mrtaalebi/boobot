#!/bin/bash
ocpasswd -c /etc/ocserv/pass.wd $1 <<< "$2\n$2\n"
