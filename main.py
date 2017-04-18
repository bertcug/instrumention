#coding=utf-8

import os
from share_operation import get_share_operations

PTHREAD_CREATE = 0x01
PTHREAD_JOIN = 0x02
PTHREAD_MUTEX_LOCK = 0x03
PTHREAD_MUTEX_UNLOCK = 0x04
PTHREAD_COND_SIGNAL = 0x05
PTHREAD_COND_WAIT = 0x06
PTHREAD_BARRIER_WAIT = 0x07

SHARE_VAR_READ = 0x08
SHARE_VAR_WRITE = 0x09

def get_cmd(op_mode, file):
    if op_mode == PTHREAD_CREATE:
        return "cat %s | grep -n pthread_create\( | awk '{print $1}'" % os.path.abspath(file)
    elif op_mode == PTHREAD_JOIN:
        return "cat %s | grep -n pthread_join\( | awk '{print $1}'" % os.path.abspath(file)
    elif op_mode == PTHREAD_MUTEX_LOCK:
        return "cat %s | grep -n pthread_mutex_lock\( | awk '{print $1}'" % os.path.abspath(file)
    elif op_mode == PTHREAD_MUTEX_UNLOCK:
        return "cat %s | grep -n pthread_mutex_unlock\( | awk '{print $1}'" % os.path.abspath(file)
    elif op_mode == PTHREAD_COND_SIGNAL:
        return "cat %s | grep -n pthread_cond_signal\( | awk '{print $1}'" % os.path.abspath(file)
    elif op_mode == PTHREAD_COND_WAIT:
        return "cat %s | grep -n pthread_cond_wait\( | awk '{print $1}'" % os.path.abspath(file)
    elif op_mode == PTHREAD_BARRIER_WAIT:
        return "cat %s | grep -n pthread_barrier_wait\( | awk '{print $1}'" % os.path.abspath(file)

def do_instrumentation(file):
    for i in range(1, 8):
        cmd = get_cmd(i)
        lines = os.popen(cmd).readlines()

        #插桩代码在本句结束后添加
        contents = open(file, "r").readlines()
        for line in lines:
            linenum = int(line[:-1])
            j = 0
            while True:
                if ");" in contents[linenum+j]:
                    contents[linenum+j] = contents[linenum].replace(");", ");instr(%d, '');" % i)
                    break
                else:
                    j += 1

    # end instr, rewrite file
    f = open(file, "w")
    f.seek(0)
    f.writelines(['#include "pf.h"',])
    f.writelines(contents)
    f.flush()
    f.close()

def do_share_operation_instrument(analyses_file):
    results = get_share_operations(analyses_file)
    current_file = ""
    contents = ""
    for file, line, op, var in results:
        if file != current_file:
            # 到新文件了，保存旧文件
            out = open(current_file, "w")
            out.seek(0)
            out.writelines(['#include "pf.h"', ])
            out.writelines(contents)
            out.flush()
            out.close()

            contents = open(file, "r").readlines()
        while True:
            if ";" in contents[line-1]:
                contents[line-1] = contents[line-1].replace(";", ";instr(%d, '%s')" % (op, var))
                break
            else:
                line += 1

    # 修改最后一个文件
    out = open(current_file, "w")
    out.seek(0)
    out.writelines(['#include "pf.h"', ])
    out.writelines(contents)
    out.flush()
    out.close()


