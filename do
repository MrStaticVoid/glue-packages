#!/bin/bash

export HOME=$(readlink -f $(dirname $0))
exec "$@"
