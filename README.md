# galmin

# Galera Cluster Command Line Tool

## Dependencies

1. [python3](https://www.python.org/downloads/release/python-364/)
2. [paramiko](http://www.paramiko.org/installing.html)

## Installation:
First, visit the websites of the dependencies and install as instructed. Then download the script **galmin.py** to any directory 
and create an alias pointing to it as follows:

    alias galmin="python3 ~/{download_directory}/galmin.py"

then use the command **galmin** from now on to manage a Galera cluster.


## Usage

When you first type **galmin** you will get the following help screen:

    usage: galmin.py [-h] [--init] [--ping] [--install] [--start] [--stop]
                     [--bootstrap] [--status] [--server]
    
    Galera Cluster Admin Tool
    
    optional arguments:
      -h, --help   show this help message and exit
      --init       Creates a default config file named "cluster.config"
      --ping       Makes sure that all nodes are reachable by pinging them
      --install    Installs Galera cluster on the nodes specified in the config
                   file
      --start      Starts the cluster
      --stop       Stops the cluster
      --bootstrap  Marks the first cluster node as safe to bootstrap from
      --status     Shows cluster status report
      --server     Starts a local monitoring server on "http://localhost:8080"
    
    Welcome to the Galera cluster admin command line tool. Before using this tool,
    use the "--init" command to create a default config file named
    "cluster.config" then edit it to specify your cluster nodes. Once a cluster
    has been installed, run the "--bootstrap" command to mark the first cluster
    node as safe to start the cluster from. After starting the cluster, use
    the command "--server" to start a local monitoring server on
    "http://localhost:8080" which can then be stopped using Ctrl-C.

To get started, first provision three `Ubuntu 16.04` servers and assign static ips to them, also make sure that `openssh-server` 
is installed on the three servers.

Now type:

    galmin --init
    
and you will get the following:

    creating file "./cluster.config"...

    Done, the file has three nodes configured to default values.
    Please make sure to edit this file and enter the correct
    ips and ssh login credentials for the cluster nodes.
    Add more nodes as desired using the following format:
    
    label: [cluster node label]
    ip: [cluster node static ip]
    login: [login account user name used in ssh connections]
    password: [password of the login account]
    [an optional trailing empty line]
    
As instructed, edit the file "cluster.config" and enter the values as necessary.

After that make sure that the cluster servers are all up by typing:

    galmin --ping
    
and if all is OK, you should see something like:

    pinging "cluster_node_1" (192.168.0.91) ...
    pinging "cluster_node_2" (192.168.0.92) ...
    pinging "cluster_node_3" (192.168.0.93) ...
    "cluster_node_1" (192.168.0.91) is up
    "cluster_node_2" (192.168.0.92) is up
    "cluster_node_3" (192.168.0.93) is up

you may want at this stage to ping each node from each other node.

Now we are ready to start the installation process.

Simply type:

    galmin --install
    
and after a while the installation should be complete on all nodes. The installation installs **mariadb** server with **galera**
at the same time. The default username for all databases on all nodes is **root** with a blank password. 

Before starting the cluster, we need to mark the primary node (the first node in "cluster.config" by convention) as safe to start
the cluster from. To do that, type:

    galmin --bootstrap
    
Now we are ready to start the cluster, use:

    galmin --start
    
to stop the cluster, use:

    galmin --stop
    
 after you start the cluster, (or just anytime) you can view the status of the cluster by issuing the command:
 
    galmin --status
    
with an outpout similar to:

    Node 1
    ------
      label: ubuntu1
         ip: 192.168.0.91
     galera: installed
     deamon: started
    
    Node 2
    ------
      label: ubuntu2
         ip: 192.168.0.92
     galera: installed
     deamon: started
    
    Node 3
    ------
      label: ubuntu3
         ip: 192.168.0.93
     galera: installed
     deamon: started
    
    Cluster Size : 3
    ------------

Finally you can open another terminal window and start a local monitoring server by:

    galmin --server
    
on the same machine open your browser and visit `http://localhost:8080` to see something like:

![server screenshot](https://github.com/rabihkodeih/galmin/blob/master/local_server.png)

----------------------------------------------------------------------------------------

    
