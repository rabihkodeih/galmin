# galmin

# Galera Cluster Command Line Tool

    usage: galmin.py [-h] [--init] [--ping] [--install] [--start] [--stop]
                     [--status] [--server]

    Galera Cluster Admin Tool

    optional arguments:
      -h, --help  show this help message and exit
      --init      Creates a default config file named "cluster.config"
      --ping      Makes sure that all nodes are reachable by pinging them
      --install   Installs Galera cluster on the nodes specified in the config file
      --start     Starts the cluster
      --stop      Stops the cluster
      --status    Shows cluster status report
      --server    Starts a local monitoring server on "http://localhost:8080"

    Welcome to the Galera cluster admin command line tool. Before using this tool,
    use the "--init" command to create a default config file named
    "cluster.config" then edit it to specify your cluster nodes. Once a cluster
    has been installed and started, use the command "--server" to start a local
    monitoring server on "http://localhost:8080" which can then be stopped using
    Ctrl-C.
