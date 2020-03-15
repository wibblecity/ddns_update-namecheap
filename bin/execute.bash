#!/bin/bash

CFG_DIR=/etc/ddns/namecheap/conf.d

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

if [ -d "${CFG_DIR}" ] ; then
  CFG_FILE_LIST=`ls -1 "${CFG_DIR}" | grep "\.conf$" | sort`
  for CFG_FILE in `echo ${CFG_FILE_LIST}` ; do
    if [ -f "${CFG_DIR}/${CFG_FILE}" ] ; then
      echo "${CFG_DIR}/${CFG_FILE}"
      cat "${CFG_DIR}/${CFG_FILE}"
      ${SCRIPT_DIR}/update.py --config="${CFG_DIR}/${CFG_FILE}"
    fi
  done
fi

### log_event "Updating Git workspace"
if [ -f /etc/git_control/auto_updates/ddnd_update-namecheap.enabled ] ; then
  cd "${SCRIPT_DIR}"
  git pull -f --all >/dev/null
  if [ "$?" -ne "0" ] ; then
    usage "git pull -f --all command exited with errors"
  fi
fi
