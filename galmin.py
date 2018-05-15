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


def ssh_run(host, login, password, commands, verbose=True):
    '''
    Runs a list of commands through an ssh connection to the given host using the supplied login and password
    '''
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    result = None
    try:
        client.connect(hostname=host, username=login, password=password)
        for command in commands:
            if verbose: sys.stdout.write('\n* %s >> %s\n' % (host, command))
            stdin, stdout, stderr = client.exec_command(command)  # @UnusedVariable
            if command.startswith('sudo'):
                stdin.write('%s\n' % password)
                stdin.flush()
            #for some weird reason trying to read the output buffer hangs on "ufw enable" command
            if command == 'sudo -S ufw enable': continue 
            result = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")
            if result:
                if verbose: sys.stdout.write(result + '\n')
            if error:
                if verbose: sys.stderr.write(error + '\n')
    except:
        sys.stdout.write('Failed to establish ssh connection to host "%s"\n' % host)
        sys.stdout.write('due to the following exception:\n')
        traceback.print_exc(file=sys.stdout)
    finally:
        client.close()
    return result
   
   
def get_galera_cnf_content(node_ip, node_name, cluster_ips):
    template = '''
    [mysqld]
    binlog_format=ROW
    default-storage-engine=innodb
    innodb_autoinc_lock_mode=2
    bind-address=0.0.0.0
    
    # Galera Provider Configuration
    wsrep_on=ON
    wsrep_provider=/usr/lib/galera/libgalera_smm.so
    
    # Galera Cluster Configuration
    wsrep_cluster_name="galera_cluster"
    wsrep_cluster_address="gcomm://%CLUSTER_IPS%"
    
    # Galera Synchronization Configuration
    wsrep_sst_method=rsync
    
    # Galera Node Configuration
    wsrep_node_address="%NODE_IP%"
    wsrep_node_name="%NODE_NAME%"
    '''
    template = template.replace('%CLUSTER_IPS%', ','.join(cluster_ips))
    template = template.replace('%NODE_IP%', node_ip)
    template = template.replace('%NODE_NAME%', node_name)
    content = '\n'.join(line.strip() for line in template.splitlines())
    return content     


def check_installation(node):
    '''
    This function checks whether galera cluster is installed on the node pointed to by the supplied node object
    '''
    _, ip, login, password = parse_node(node)
    output = ssh_run(ip, login, password, ['sudo -S which mysqld'], verbose=False)
    output = ''.join(output.splitlines()).strip()
    return ip, 'mysqld' in output


def check_deamon(node):
    '''
    This function checks whether mysql is started on the node pointed to by the supplied node object
    '''
    _, ip, login, password = parse_node(node)
    output = ssh_run(ip, login, password, ['sudo -S service --status-all | grep mysql'], verbose=False)
    output = ''.join(output.splitlines()).strip()
    return ip, output=='[ + ]  mysql'


def get_cluster_size(node):
    '''
    this function returns the cluster size from the node pointed to by the supplied node object
    '''
    _, ip, login, password = parse_node(node)
    commands = ['''sudo -S mysql -u root -e "SHOW STATUS LIKE 'wsrep_cluster_size'" | grep wsrep_cluster_size''']
    output = ssh_run(ip, login, password, commands, verbose=False)
    tmp = output.split()
    if len(tmp) > 1:
        cluster_size = tmp[1]
    else:
        cluster_size = '0'
    return cluster_size


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
    primary_node = nodes[0]
    _, ip, login, pwd = parse_node(primary_node)
    ssh_run(ip, login, pwd, ['sudo -S galera_new_cluster'])
    secondary_nodes = nodes[1:]
    def join_cluster(node):
        _, ip, login, pwd = parse_node(node)
        commands = ['sudo -S systemctl start mysql']
        ssh_run(ip, login, pwd, commands)
    args_list = [(node,) for node in secondary_nodes]
    execute_parrallel(join_cluster, args_list)


def command_stop(nodes):
    def stop_deamon(node):
        _, ip, login, password = parse_node(node)
        commands = ['sudo -S systemctl stop mysql']
        ssh_run(ip, login, password, commands)
    args_list = [(node,) for node in nodes]
    execute_parrallel(stop_deamon, args_list)
    

def command_install(nodes):
    cluster_ips = [node['ip'] for node in nodes]
    def install_cluster_node(node):
        sys.stdout.write('trying to ssh to %s\n' % str(node['ip']))
        label, ip, login, password = parse_node(node)
        config_file_content = get_galera_cnf_content(ip, label, cluster_ips)
        commands = [
            'sudo -S apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8',
            "sudo -S add-apt-repository 'deb [arch=amd64,i386,ppc64el] http://ftp.utexas.edu/mariadb/repo/10.1/ubuntu xenial main'",
            'sudo -S apt update -y',
            "sudo -S sh -c 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y mariadb-server rsync'",
            'sudo -S echo \'%s\' > ~/galera.tmp' % config_file_content,
            'sudo -S mv galera.tmp /etc/mysql/conf.d/galera.cnf',
            'sudo -S ufw enable',
            'sudo -S ufw allow ssh',
            'sudo -S ufw allow 3306/tcp',
            'sudo -S ufw allow 4444/tcp',
            'sudo -S ufw allow 4567/tcp',
            'sudo -S ufw allow 4568/tcp',
            'sudo -S ufw allow 4567/udp',
            'sudo -S systemctl stop mysql'
        ]
        ssh_run(ip, login, password, commands)
        return 0
    args_list = [(node,) for node in nodes]
    installations = dict(execute_parrallel(check_installation, args_list))
    installed_nodes = [node for node in nodes if installations[node['ip']]]
    uninstalled_nodes = [(node,) for node in nodes if not installations[node['ip']]]
    for node in installed_nodes:
        label, ip, _, _ = parse_node(node)
        sys.stdout.write('Galera allready installed on node "%s" (%s), skipping installation\n' % (label, ip))
    execute_parrallel(install_cluster_node, uninstalled_nodes)


def command_status(nodes):
    args_list = [(node, ) for node in nodes]
    installations = dict(execute_parrallel(check_installation, args_list))
    deamons = dict(execute_parrallel(check_deamon, args_list))
    sys.stdout.write('\n')
    for ith, node in enumerate(nodes):
        header = 'Node %s' % (ith + 1)
        sys.stdout.write('%s\n' % header)
        sys.stdout.write('%s\n' % ('-'*len(header)))
        sys.stdout.write('  label: %s\n' % node['label'])
        sys.stdout.write('     ip: %s\n' % node['ip'])
        sys.stdout.write(' galera: %s\n' % ('installed' if installations[node['ip']] else 'not installed')) 
        sys.stdout.write(' deamon: %s\n' % ('started' if deamons[node['ip']] else 'stopped'))
        sys.stdout.write('\n')
    sys.stdout.write('Cluster Size : %s\n' % get_cluster_size(nodes[0]))
    sys.stdout.write('------------\n\n')


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
    
    
    #TODO: add db user name and password in each node (currently set to root/"" by default isntallation process)
    
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
    
    
    
    
    # manual installation MariaDB/Galera cluster on Ubuntu 14.04
    
    # pre-conditions:
    #    ubuntu server 16.04 with openssh-server installed and a static ip address assigned
    # >> sudo apt-get update -y
    # >> sudo apt-get upgrade -y
    # >> reboot
    
    # >> 
    
    #...
    # sudo sh -c 'apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y mariadb-server'
    #...
    
    
    
    
    
    
    