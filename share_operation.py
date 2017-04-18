#coding=utf-8
import re

class Pos:
    def __init__(self, str):
        items = str.strip().split(':')
        self.fileName = items[0]
        self.lineNum = items[1]

    def __hash__(self):
        return hash((self.fileName, self.lineNum))

    def __eq__(self, other):
        return self.fileName == other.fileName and self.lineNum == other.lineNum

    def __str__(self):
        return '%s %s' % (self.fileName, self.lineNum)


class Rho:
    def __init__(self, str):
        if str.strip() == '<empty>' or str.strip() == 'unknown':
            self.valName = 'NULL'
            self.fileName = 'NULL'
            self.lineNum = 'NULL'
        else:
            items = str.strip().split(':')
            self.valName = items[0]
            self.fileName = items[1]
            self.lineNum = items[2]

    def __eq__(self, other):
        return self.valName == other.valName and self.fileName == other.fileName and self.lineNum == other.lineNum

    def __hash__(self):
        return hash((self.valName, self.fileName, self.lineNum))

    def __str__(self):
        return '%s %s %s' % (self.valName, self.fileName, self.lineNum)


def processFork(lines, option):
    result = []
    if option == 'r':
        result.append(Rho(lines[0].strip().split('filtered read:')[1]))
    elif option == 'w':
        result.append(Rho(lines[0].strip().split('filtered write:')[1]))
    elif option == 's':
        result.append(Rho(lines[0][lines[0].find(': ') + 1:]))
    i = 1
    while True:
        if not lines[i].startswith('  '):
            break
        else:
            result.append(Rho(lines[i]))
        i += 1
    return result


def preprocess(fileName):
    lines = []
    with open(fileName, 'r') as pfile:
        lines = pfile.readlines()
    read_access = {}
    write_access = {}
    forks = {}
    shared = []
    i = 0
    for eachline in lines:
        if 'read access to' in eachline:
            item = eachline.split('read access to')
            t_pos = Pos(item[0])
            t_rho = Rho(item[1])
            if t_rho not in read_access:
                read_access[t_rho] = [t_pos]
            elif t_pos not in read_access[t_rho]:
                read_access[t_rho].append(t_pos)
        elif 'write access to' in eachline:
            item = eachline.split('write access to')
            t_pos = Pos(item[0])
            t_rho = Rho(item[1])
            if t_rho not in write_access:
                write_access[t_rho] = [t_pos]
            elif t_pos not in write_access[t_rho]:
                write_access[t_rho].append(t_pos)
        elif 'FORK' in eachline and 'filtered read' in eachline:
            posStr = re.findall('FORK\s\((.*?)\)', eachline)
            # if len(posStr)!= 1:
            #	print 'Multi pos found!'
            #	return
            # if len(posStr) <= 1:
            #	print eachline
            posStr = posStr[0]
            t_pos = Pos(posStr)
            forks[t_pos] = {}  # read always comes first
            forks[t_pos]['read'] = processFork(lines[i:], 'r')
        elif 'FORK' in eachline and 'filtered write' in eachline:
            posStr = re.findall('FORK\s\((.*?)\)', eachline)
            # if len(posStr)!= 1:
            #	print 'Multi pos found!'
            #	return
            # if len(posStr) <= 1:
            #	print eachline
            posStr = posStr[0]
            forks[Pos(posStr)]['write'] = processFork(lines[i:], 'w')
        elif eachline.startswith('shared: '):
            shared = processFork(lines[i:], 's')
        i += 1
    return read_access, write_access, forks, shared


def get_share_operations(file):
    read_access, write_access, forks, shareds = preprocess(file)
    result = []
    for fork in forks:
        # print 'For',fork,':'
        for shared in shareds:
            for rho in forks[fork]['read']:
                if rho.fileName == shared.fileName and rho.lineNum == shared.lineNum:
                    if rho not in read_access:
                        # print rho,'cannot find read accessing pos'
                        pass
                    else:
                        for single_access in read_access[rho]:
                            result.append((single_access.fileName, single_access.lineNum, 0x08, rho.valName))
            for rho in forks[fork]['write']:
                if rho.fileName == shared.fileName and rho.lineNum == shared.lineNum:
                    if rho not in write_access:
                        #print rho,'cannot find write accessing pos'
                        pass
                    else:
                        for single_access in write_access[rho]:
                            result.append((single_access.fileName, single_access.lineNum, 0x09, rho.valName))
    result = set(result)
    result = list(result)
    result = sorted(result)
    return  result