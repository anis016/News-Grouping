# MongoDB installation

This setup is for the Ubuntu 16.04 OS. Please check the [Official website](https://docs.mongodb.com/v3.2/administration/install-community/) for other OS installations.
`Project Specific Version: 3.2.16`

### Pre-configurations and Installations

1. Import the public key used by the package management system.
    ```sh
    $ sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
    ```
2. Create a list file for MongoDB [Ubuntu 16.04]
    ```sh
    $ echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
    ```
3. Reload local package database
    ```sh
    $ sudo apt-get update
    ```
4. Install the MongoDB packages
    ```sh
    $ sudo apt-get install -y mongodb-org=3.2.16 mongodb-org-server=3.2.16 mongodb-org-shell=3.2.16 mongodb-org-mongos=3.2.16 mongodb-org-tools=3.2.16
    ```

### Configurations

1. (Ubuntu 16.04-only) Create systemd service file if not present
    ```sh
    $ touch /lib/systemd/system/mongod.service
    $ vi mongod.service
    ```
    ```
    [Unit]
    Description=High-performance, schema-free document-oriented database
    After=network.target
    Documentation=https://docs.mongodb.org/manual
    
    [Service]
    User=mongodb
    Group=mongodb
    ExecStart=/usr/bin/mongod --quiet --config /etc/mongod.conf
    
    [Install]
    WantedBy=multi-user.target
    ```
### Commands

1. `Start MongoDB`
    ```sh
    $ sudo service mongod start
    ```
2. `Stop MongoDB`
    ```sh
    $ sudo service mongod stop
    ```
3. `Verify if MongoDB has started successfully`
    ```sh
    $ tail -f /var/log/mongodb/mongod.log
    Check "[initandlisten] waiting for connections on port <port>"
    ```
4. `Start Mongo CL Shell`
    ```sh
    $ mongo
    ```
