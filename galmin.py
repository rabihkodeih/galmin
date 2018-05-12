'''
Created on May 11, 2018

@author: rabihkodeih
'''

import sys
from argparse import ArgumentParser


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
    #TODO: in each mode except the config mode, check if cluster.config exists in the same directory
    # and make sure it has the appropriate format, in case of error, show the exact error and display the same help as in the config mode
    nodes = [{}, {}, {}]
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


#===============================================================================
# Command Functions
#===============================================================================

def command_init(nodes):
    #TODO: implement
    sys.stdout.write('init command\n')

def command_install(nodes):
    #TODO: implement
    sys.stdout.write('install command\n')

def command_ping(nodes):
    #TODO: implement
    sys.stdout.write('ping command\n')

def command_start(nodes):
    #TODO: implement
    sys.stdout.write('start command\n')

def command_stop(nodes):
    #TODO: implement
    sys.stdout.write('stop command\n')

def command_status(nodes):
    #TODO: implement
    sys.stdout.write('status command\n')

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
        execute(command_init, nodes)
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
    
    #TODO: replace all print statements with sys.stdout.write
    #TODO: show main help message in readme.md with some salt and pepper 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    