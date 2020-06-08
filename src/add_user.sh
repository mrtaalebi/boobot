#!/bin/bash
ocpasswd -c $1 $2 <<< "$3\n$3\n"
