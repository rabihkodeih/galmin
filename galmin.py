'''
Created on May 11, 2018

@author: rabihkodeih
'''

import os
import sys
import traceback
from argparse import ArgumentParser
from multiprocessing.pool import ThreadPool
import paramiko


CONFIG_PATH = './cluster.config'


#===============================================================================
# Utility Funcions
#===============================================================================

def parse_nodes():
    '''
    This function checks if the config file "cluster.config" existst in the current working directory.
    It also checks the format of the file and parses its contents.
    The return value is one of:
    * A list of node objects if the config file is OK
    * None if the config file is incorrectly configured or is missing
    '''
    nodes = None
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as config:
            lines = [''.join(line.splitlines()) for line in config.readlines()]
            lines = [line for line in lines if line]
            sections = [lines[4*i:4*(i + 1)] for i in range(len(lines)//4)]
            legal_keys = set(['label', 'ip', 'login', 'password'])
            nodes = []
            for section in sections:
                node = {}
                for config_line in section:
                    key, value = [data.strip() for data in config_line.split(':')]
                    node[key] =  value
                if set(node.keys()) != legal_keys:
                    nodes = None
                    break
                nodes.append(node)
    return nodes


def execute(command_closure, nodes):
    '''
    This function applies the nodes argument to the command_closure if all is well otherwise
    it displays an error message.
    '''
    if nodes == None:
        sys.stdout.write('Could not execute command. The config file is either missing or is incorrectly configured.\n')
        sys.stdout.write('Use the "--init" option to create a default config file or correctly edit the existing one.\n')
    else:
        command_closure(nodes)


def execute_parrallel(function, args_list):
    '''
    Executes the input function in parrallel using a thread pool object using the fiven args_list,
    a list of results is returned
    '''
    async_results = []
    for args in args_list:
        pool = ThreadPool(processes=1)
        async_results.append(pool.apply_async(function, args))
    results = [r.get() for r in async_results]
    return results


def parse_node(node):
    '''
    Utility function to parse a node object,
    returns: label, ip, login, password
    '''
    label, ip, login, password = node['label'], node['ip'], node['login'], node['password']
    return label, ip, login, password


def ssh_run(host, login, password, commands):
    #TODO: add docstring
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, username=login, password=password)
        for command in commands:
            sys.stdout.write('\n* %s >> %s\n' % (host, command))
            stdin, stdout, stderr = client.exec_command(command)  # @UnusedVariable
            if command.startswith('sudo'):
                stdin.write('%s\n' % password)
                stdin.flush()
            result = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")
            if result:
                sys.stdout.write(result + '\n')
            if error:
                sys.stderr.write(error + '\n')
    except:
        sys.stdout.write('Failed to establish ssh connection to host "%s"\n' % host)
        sys.stdout.write('due to the following exception:\n')
        traceback.print_exc(file=sys.stdout)
    finally:
        client.close()
        

#===============================================================================
# Command Functions
#===============================================================================

def command_init():
    sys.stdout.write('\ncreating file "%s"...\n' % CONFIG_PATH)
    if os.path.exists(CONFIG_PATH):
        sys.stdout.write('Could not create file, "%s" already exists, please delete it and run this command again.' % CONFIG_PATH)
        sys.stdout.write('\n')
    else:
        with open(CONFIG_PATH, 'w') as config:
            for node_number in range(1, 4):
                config.write('label:cluster_node_%s\n' % node_number);
                config.write('ip:127.0.0.1\n');
                config.write('login:root\n');
                config.write('password:1234\n');
                config.write('\n');
        sys.stdout.write('\nDone, the file has three nodes configured to default values.\n')
        sys.stdout.write('Please make sure to edit this file and enter the correct\n')
        sys.stdout.write('ips and ssh login credentials for the cluster nodes.\n')
        sys.stdout.write('Add more nodes as desired using the following format:\n')
        sys.stdout.write('\n')
        sys.stdout.write('label: [cluster node label]\n')
        sys.stdout.write('ip: [cluster node static ip]\n')
        sys.stdout.write('login: [login account user name used in ssh connections]\n')
        sys.stdout.write('password: [password of the login account]\n')
        sys.stdout.write('[an optional trailing empty line]\n')
        sys.stdout.write('\n')


def command_ping(nodes):
    def ping_node(ip, label):
        sys.stdout.write('pinging "%s" (%s) ...\n' % (label, ip))
        response = os.system("ping -c 1 %s" % ip)
        message = '"%s" (%s) is up\n' if response==0 else '"%s" (%s) is down!\n'
        result = message % (label, ip)
        return result
    args_list = [(node['ip'], node['label']) for node in nodes]
    results = execute_parrallel(ping_node, args_list)
    sys.stdout.writelines(results)
    

def command_start(nodes):
    #TODO: implement
    sys.stdout.write('start command\n')


def command_stop(nodes):
    #TODO: implement
    sys.stdout.write('stop command\n')


def command_install(nodes):
    #TODO: implement

    # sudo -S remove selinux
    # sudo -S ln -s /etc/apparmor.d/usr /etc/apparmor.d/disable/.sbin.mysqld
    # sudo -S service apparmor restart
    
    # sudo -S apt-get -y install git
    # sudo -S apt-get -y install scons
    # sudo -S apt-get -y install libboost-dev
    # sudo -S apt-get -y install libboost-program-options-dev 
    # sudo -S apt-get -y install libasio-dev
    # sudo -S apt-get -y install check
    
    # sudo -S apt-get -y build-dep mysql-server
    # git clone https://github.com/codership/mysql-wsrep -b 5.6 --depth=1
    # cd ~/mysql-wsrep; git checkout 5.6
    # git clone https://github.com/codership/galera.git --depth=1
    # cd ~/mysql-wsrep; cmake -DWITH_WSREP=ON -DWITH_INNODB_DISALLOW_WRITES=ON ./
    # cd ~/mysql-wsrep; make
    # sudo -S ls; cd ~/mysql-wsrep; sudo make install
    # sudo -S ls; cd ~/galera; sudo scons
    
    # sudo -S groupadd mysql
    # sudo -S useradd -g mysql mysql
    # sudo -S ls; cd /usr/local/mysql; sudo ./scripts/mysql_install_db --user=mysql
    # sudo -S chown -R mysql /usr/local/mysql
    # sudo -S chgrp -R mysql /usr/local/mysql
    # sudo -S cp /usr/local/mysql/supported-files/mysql.server /etc/init.d/mysql
    # sudo -S chmod +x /etc/init.d/mysql
    # sudo -S update-rc.d mysql defaults
    
    # sudo -S aptget install mysql-client
    
    # change basedir to /usr/local/ in /etc/init.d/mysql file
    
    
    
    for node in nodes:
        label, ip, login, password = parse_node(node)
        #commands = ['sudo -S ls; cd ~/mysql-wsrep; sudo make install',]
        commands = ['pwd']
        ssh_run(ip, login, password, commands)
        return
    
    sys.stdout.write('install command\n')


def command_status(nodes):
    sys.stdout.write('\n')
    for ith, node in enumerate(nodes):
        header = 'Node %s' % (ith + 1)
        sys.stdout.write('%s\n' % header)
        sys.stdout.write('%s\n' % ('-'*len(header)))
        sys.stdout.write('  label: %s\n' % node['label'])
        sys.stdout.write('     ip: %s\n' % node['ip'])
        sys.stdout.write(' galera: %s\n' % 'installed') #TODO: implement
        sys.stdout.write(' deamon: %s\n' % 'stopped') #TODO: implement
        sys.stdout.write('\n')


def command_server(nodes):
    #TODO: implement
    sys.stdout.write('server command\n')


if __name__ == '__main__':
    
#     Write a Golang server program that
#     - installs a 3-node MySQL/Galera cluster in an environment of your choice: AWS, Docker, VMs, single host, etc.
#     - starts the cluster up
#     - waits for HTTP client connections
#     - displays a list of running nodes on the home page.
    

    epilog_message = '''
    Welcome to the Galera cluster admin command line tool. Before using this tool, use the "--init" command 
    to create a default config file named "cluster.config" then edit it to specify your cluster nodes.
    Once a cluster has been installed and started, use the command "--server" to
    start a local monitoring server on "http://localhost:8080" which can then be stopped using Ctrl-C.
    '''
    parser = ArgumentParser(description='Galera Cluster Admin Tool', epilog=epilog_message)

    parser.add_argument('--init', action='store_true', help='Creates a default config file named "cluster.config"')
    parser.add_argument('--ping', action='store_true', help='Makes sure that all nodes are reachable by pinging them')
    parser.add_argument('--install', action='store_true', help='Installs Galera cluster on the nodes specified in the config file')
    parser.add_argument('--start', action='store_true', help='Starts the cluster')
    parser.add_argument('--stop', action='store_true', help='Stops the cluster')
    parser.add_argument('--status', action='store_true', help='Shows cluster status report')
    parser.add_argument('--server', action='store_true', help='Starts a local monitoring server on "http://localhost:8080"')
    
    args = parser.parse_args()
    
    if args.init:
        nodes = parse_nodes()
        command_init()
    elif args.ping:
        nodes = parse_nodes()
        execute(command_ping, nodes)
    elif args.install:
        nodes = parse_nodes()
        execute(command_install, nodes)
    elif args.start:
        nodes = parse_nodes()
        execute(command_start, nodes)
    elif args.stop:
        nodes = parse_nodes()
        execute(command_stop, nodes)
    elif args.status:
        nodes = parse_nodes()
        execute(command_status, nodes)
    elif args.server:
        nodes = parse_nodes()
        execute(command_server, nodes)
    else:
        parser.print_help(sys.stdout)
    
    
    
    #TODO: add to documentation that :
        #  servers used for the test are ubuntu desktops 14.04
        #  git installed
        #  policycoreutils installed
    
    #TODO: replace all print statements with sys.stdout.write
    #TODO: show main help message in readme.md with some salt and pepper 
    #TODO: connect to nodes using ssh keys instead of username logins
    
    
    
    # VM Credentials:
    # ubuntu1: rabih (Abcd1234)
    # ubuntu2: rabih (Abcd1234)
    # ubuntu3: rabih (Abcd1234)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    