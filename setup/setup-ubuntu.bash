#!/bin/bash

### variables ###
CFG_DIR_BASE=/etc/ddns/namecheap
CFG_DIR=${CFG_DIR_BASE}/conf.d
PATH=${PATH}:/usr/local/bin
######

### functions
function log_event {
  EVENT_DATA="$1"
  THIS_PID="$$"
  if [ -z "${THIS_PID}" ] ; then
    usage "THIS_PID: variable is empty"
  fi
  LOG_TIMESTAMP=`date "+%F %H:%M:%S %z"`
  echo "${LOG_TIMESTAMP} - ${THIS_PID} - ${SCRIPT_NAME} - ${EVENT_DATA}"
}

function usage {
  ERROR_LOG_EVENT="$1"
  USAGE_INFO="$2"
  THIS_PID="$$"
  EXIT_STATUS="1"
  log_error_line
  log_error "##### ***** ERROR ***** ######"
  log_error
  log_error "CMD: ${SCRIPT_NAME} ${THIS_ARGS}"
  log_error "Message: ${ERROR_LOG_EVENT}"
  if [ ! -z "${USAGE_INFO}" ] ; then
    log_error
    log_error "Usage: ${SCRIPT_NAME} ${USAGE_INFO}"
    log_error
  fi
  log_error "##### ***** ERROR ***** ######"
  log_error "##### Sleeping for 5 seconds then exiting with status: ${EXIT_STATUS}"
  log_error_line
  sleep 5
  exit "${EXIT_STATUS}"
}

function log_error {
  EVENT_DATA="$1"
  THIS_PID="$$"
  LOG_TIMESTAMP=`date "+%F %H:%M:%S %z"`
  echo "${LOG_TIMESTAMP} - ${THIS_PID} - ${SCRIPT_NAME} - ERROR: ${EVENT_DATA}" >&2
}

function log_error_line {
  EVENT_DATA="$1"
  echo "${EVENT_DATA}" >&2
}
#####

SCRIPT_PATH="$(realpath "$0")"
if [ "$?" -ne "0" ] ; then
  usage "SCRIPT_PATH: realpath $0 command exited with errors"
fi

SCRIPT_NAME="$(basename "${SCRIPT_PATH}")"
if [ "$?" -ne "0" ] ; then
  usage "SCRIPT_NAME: basename ${SCRIPT_PATH} command exited with errors"
fi

SCRIPT_DIR="$(dirname "${SCRIPT_PATH}")"
if [ "$?" -ne "0" ] ; then
  usage "SCRIPT_DIR: dirname ${SCRIPT_PATH} command exited with errors"
fi
if [ ! -d "${SCRIPT_DIR}" ] ; then
  usage "SCRIPT_DIR: ${SCRIPT_DIR} does not exist or is not a directory"
fi

mkdir -p ${CFG_DIR}
useradd -r -M -s /bin/bash -d ${CFG_DIR_BASE} ddns-namecheap
chown -R ddns-namecheap ${CFG_DIR_BASE}
chmod 700 ${CFG_DIR_BASE}
cp -v ${SCRIPT_DIR}/001-default.conf ${CFG_DIR}
cp -v ${SCRIPT_DIR}/utils-update_ddns /etc/cron.d/
