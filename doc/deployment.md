## Python Deployment

###### Installed Python 3.6


```
$ sudo nano /etc/apt/sources.list
```

*Included following snippet after* `deb http://ftp.de.debian.org/debian testing main`

```
$ echo 'APT::Default-Release "stable";' | sudo tee -a /etc/apt/apt.conf.d/00local
$ sudo apt-get update
$ sudo apt-get -t testing install python3.6
$ python3.6 -V
	
```

###### Set Alias & Paths


```
$ sudo nano /home/student/.bashrc
```

*Included following snippet at the end of file*

```
alias python=python3.6
alias pip=pip3.6
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3.6

```

*Reload .bashrc without logging out*

```
$ source /home/student/.bashrc
```

## Git configuration 

###### Setup Git 


```
$ sudo nano /home/student/.ssh/config
```

*Placed following snippet in the file*

```
Host gitmrcc.iti.cs.ovgu.de
    StrictHostKeyChecking no	
    UserKnownHostsFile /dev/null	
    HostName gitmrcc.iti.cs.ovgu.de	
    Port 2222	
    User muashraf
    
```

*Placed public(id_rsa.pub) and private(id_rsa) ssh keys in the same .ssh folder.*


###### Cloned repo


```
$ cd /home/student/
$ git clone git@gitmrcc.iti.cs.ovgu.de:matpohl/businessDataMatching.git

```
###### Latest pull


*Start ssh agent and add private key for authenticatoin as follow:*

```
$ eval `ssh-agent -s`
$ ssh-add /home/student/.ssh/id_rsa

```

*Now take pull*

```
$ cd /home/student/businessDataMatching
$ git pull git@gitmrcc.iti.cs.ovgu.de:matpohl/businessDataMatching.git

```

## Virtual environment configuration


###### Installed virtualenv package

```
$ pip install virtualenv
```

*Moved back to project directory and created virtualenv*

```
$ cd /home/student/businessDataMatching
$ virtualenv bdm_venv

```

*activated virtualenv using* `$ source bdm_venv/bin/activate`

*Following configurations are required for datefinder package upfront on debian:*

*Added the specs to `no-pie-compile.specs` file using* `$ nano /usr/share/dpkg/no-pie-compile.specs` and then added:

```
*self_spec:
+ %{!r:%{!fpie:%{!fPIE:%{!fpic:%{!fPIC:%{!fno-pic:-fno-PIE}}}}}}

```

*Added the specs to `no-pie-link.specs` file using* `$ nano /usr/share/dpkg/no-pie-link.specs` and then added:

```
*self_spec:
+ %{!shared:%{!r:%{!fPIE:%{!pie:-fno-PIE -no-pie}}}}

```

###### Installed following common packages:

*Installed python and python3.6 dev headers using* `apt-get install -y python3.6-dev python-dev`

*Installed for cryptography (required by twisted[tls]) using* `apt-get install -y libssl-dev libffi-dev zlib1g-dev`

*Installed lxml using* `apt-get install -y libxml2-dev libxslt1-dev`

*Installed python build essentials using* `apt-get install -y build-essential`

###### Freeze the current state of the environment packages

*At the root of project directory run `pip freeze > requirements.txt`

###### Installed Django web-server

```
$ pip install django
```