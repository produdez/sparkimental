# Detail setup

![Untitled](images/spark-cluster-setup/Untitled.png)

# Foreword

If you ever come across `Spark` in your journey into data science, then there might be some of the basics questions that lingers when you first encounter it, such as:

- How to setup `Spark` (local machine or virtual machine?) (cluster or just local processes?)
- How to run code on it? Directly? Through python script? `jupyter`?
- Which version works with which? `Java` `Python` `Spark` `Scala`
- Why aren’t there a super detailed tutorial for this whole thing? Most tutorial either
    1. Just sure you get Spark to run (local or distributed does not matter)
    2. Installing a Spark cluster but does not show how to run code on it
    3. Does not include how you interact with Spark UI (history, master UI, slave UI, job monitor UI, …)
    4. Does not have a python virtual environment setup to manage python package for Spark
    5. Does not mention how to make the best of Virtual Machines (like `VirtualBox` VMs) to help with our development process 

So in this blog post, while researching for my distributed data processing assignment, I’ve ***********************(with my best capacity)*********************** documented exactly how I

1. Setup my Spark cluster on VMs managed by Virtual Box
2. Setup a python environment (virtual environment) using Anaconda to manage python packages on those VM
3. Run/Submit python code to my running spark cluster *(we want none of that local process Spark)*
4. Resolve all of the niches/pitfalls that I’ve encounter along the way

> This guide is meant to be a compilation of all my researched references on the topic and also meant to be ************************COMPLETELY FOOL PROOF************************ 🐪 for people like me 🙈
> 

*************So please do excuse my rather lengthy post************* 📣 Let’s go 👟🪜

# Virtual Box

> Virtual Machine Manager
> 
- 6.1.38 (most stable version) (⁉️ DONT install ≥ 7.0 since it has many bug and unstable)

[Ref](https://download.virtualbox.org/virtualbox/6.1.38/VirtualBox-6.1.38-153438-Win.exe), [Download](https://download.virtualbox.org/virtualbox/6.1.38/VirtualBox-6.1.38-153438-Win.exe)

# Create base Linux

> This will be our `building block` VM that we’ll clone and later further tweak into our master node and worker nodes
> 

## Linux Settings

### Specs

- Ubuntu 18.04 LTS ([Ref](https://releases.ubuntu.com/18.04/), [Download 64-bit](https://releases.ubuntu.com/18.04/ubuntu-18.04.6-desktop-amd64.iso))
- Recommended VM storage size: 20GB (❗You’ll already use ~10GB for all the basic packages installs)
- RAM/CPU → Your choice, my choice:
    
    > This can be easily change later so no biggie !
    > 
    - 2 CPU, 4GB RAM for master node
    - Default for slaves (workers)

### Steps

> I name my ubuntu machine name same as my Virtual Box VM name for convenient
> 
1. Run setup on virtual box to create a new empty virtual machine with the specs above
    
    > **NOTE 🗒️:** I name this machine `base-clean`
    > 
    
    [Detail Tutorial](https://medium.com/dfclub/create-a-virtual-machine-on-virtualbox-47e7ce10b21) (this is too simple for me to cover)
    
    > *Do note that you should use dynamic allocation*
    > 
2. Setup VM’s network to local host
    1. Right-click on machine > Settings > Network
    2. Make sure `Adapter 2` has these configs (Why? [Ref](https://serverfault.com/questions/225155/virtualbox-how-to-set-up-networking-so-both-host-and-guest-can-access-internet))
        
        ![Untitled](images/spark-cluster-setup/Untitled%201.png)
        
3. Run the new VM, select our `Ubuntu` ISO and start the installation (This step takes the longest 😷)
    - Simple username and password please 🙏
    - No need to care about machine name, we can always change it
    
    > **NOTE 🗒️:** My setup’s user name is `prod`
    > 
4. (⏰ Optional) Update the kernel/system (their might be an on screen UI prompt for this)
5. (⏰ Optional) Install `Guest Addition CD Image` 
    - So that we can use bidirectional clipboard between host (*********your pc)********* and the VMs
        
        *************Details below************* 🔽
        
        1. Mount cd
            
            ![Untitled](images/spark-cluster-setup/Untitled%202.png)
            
        2. Wait for CD to be mounted + popup for installation
            
            ![Untitled](images/spark-cluster-setup/Untitled%203.png)
            
        3. Click run and wait till finish, eject the CD if you’re a gentlemen 🎩
        4. **Restart** VM and make sure the shared clipboard works
            
            > Don’t 4get to select shared clipboard option before testing 😉
            > 
            
            ![Untitled](images/spark-cluster-setup/Untitled%204.png)
            
6. (⏰ Optional) Update package manager `apt-get`
    
    ```bash
    sudo apt-get upgrade
    ```
    
7. Get the VM’s `ip address`
    
    ```bash
    ip addr
    ```
    
    > The first two IPs are for internet connection, there should be a third one that indicate our VM’s IP within our host’s local network *(recheck adapter 2 network settings if missing one entry)*
    > 
    
    ![VM’s IP on local network](images/spark-cluster-setup/Untitled%205.png)
    
    VM’s IP on local network
    
    Take note of the VM’s IP on the local network for later configure
    
    > **NOTE 🗒️:** my `base-clean` VM’s IP is `192.168.56.105`
    > 
8. Install `SSH`
    1. Download
        
        ```bash
        sudo apt-get install openssh-server openssh-client
        ```
        
    2. Generate key with `ssh-keygen`
        
        > Or create `.ssh` folder with `mkdir ~/.ssh` if you don’t want your VMs to have duplicated SSH keys when they’re cloned.
        > 
    3. (⏰ Optional) Copy your host’s SSH key to the VM for later quick SSH access without needing to re-type password every time
        
        ```bash
        # assuming you already have you ssh key generated on your host machine
        cat C:\Users\USER\.ssh\id_rsa.pub | ssh prod@192.168.56.105 "cat >> .ssh/authorized_keys"
        ```
        
    4. Test with `ssh <username>@<ip-addr>` (should not ask for password)
9. Install `curl` (for downloading files later)
    
    ```bash
    sudo apt-get install curl
    ```
    
10. Power off the machine 🥂
11. Make a clone of the current machine (`base-clean`) for backup, name it `base-installed` (for next step)

> ⚡ Always clone with MAC-address-policy set to `Generate new MAC address for all network adapters` (avoid IP repetition)
> 

### Where are we at

We’ve now got a `base-clean` Linux VM that

- Has basic network setup
- Ubuntu installed and updated
- Complete clean state with no extra packages
- SSH setup for easy access from local machine’s shell

---

### Why?

- This clean state help with to rollback in case our later `Spark/Python/Java/Scala/…` packages installs fails 💀
- The SSH setup allow us to later run these machine in `headless` mode (no UI) and access them easily from local machine’s shell with `ssh`

# Installing Spark

> Next step we’ll continue to install needed packages on the `base-installed` VM
> 

### Steps

**⚠️ These steps take from decent to … N amount of time** 👿

> ⚡ Should run you newly cloned VM in normal start (GUI) mode once to get its IP before going headless with SSH shell for easier management
> 
1. Connect to machine `ssh <username>:<base-installed-VM-IP>`
    
    > **NOTE 🗒️:** My `base-installed` VM’s IP is `192.168.56.106`
    > 
2. Java, Scala 
    
    ```bash
    sudo apt install default-jdk scala
    
    # Verify
    java -version; javac -version; scala -version;
    ```
    
    Installed versions should be
    
    ```bash
    openjdk version "11.0.16" 2022-07-19
    OpenJDK Runtime Environment (build 11.0.16+8-post-Ubuntu-0ubuntu118.04)
    OpenJDK 64-Bit Server VM (build 11.0.16+8-post-Ubuntu-0ubuntu118.04, mixed mode, sharing)
    javac 11.0.16
    Scala code runner version 2.11.12 -- Copyright 2002-2017, LAMP/EPFL
    ```
    
3. (⏰ Optional) Git
    
    ```bash
    sudo apt-get install git
    
    git --version
    ```
    
    ⚡ Git installed should be 2.17.1, which is older than 2.23. So use `checkout` instead of `switch` ([Ref](https://stackoverflow.com/questions/60754571/why-does-git-switch-checkout-not-switch-branch))
    
4. Anaconda ([Ref](https://phoenixnap.com/kb/how-to-install-anaconda-ubuntu-18-04-or-20-04))
    
    ```bash
    # download
    curl -O https://repo.anaconda.com/archive/Anaconda3-2022.10-Linux-x86_64.sh
    # validate download
    sha256sum Anaconda3-2022.10-Linux-x86_64.sh
    # install (follow the instructions)
    bash Anaconda3-2022.10-Linux-x86_64.sh
    ```
    
    If shown with option below ⇒ accept it
    
    ```bash
    Do you wish the installer to initialize Anaconda3
    by running conda init?
    
    # Answer yes :v
    ```
    
    When done, reload bash with `source ~/.bashrc` and make sure you can run `conda` and `python`
    
    ```bash
    which python
    
    #should return
    /home/prod/anaconda3/bin/python
    ```
    
5. Spark ([Home Page](https://www.apache.org/dyn/closer.lua/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz), [Download Site](https://www.apache.org/dyn/closer.lua/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz), [Download Link](https://dlcdn.apache.org/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz))
    
    ```bash
    curl -O https://dlcdn.apache.org/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz
    
    sha256sum spark-3.3.1-bin-hadoop3.tgz
    
    sudo tar xvf spark-3.3.1-bin-hadoop3.tgz
    ```
    
    > **NOTE 🗒️:** remember SPARK installation folder, currently `~/spark-3.3.1-bin-hadoop3/`
    > 
6. Create Anaconda environment (to manage our python packages)
    
    > Reference “Create `conda` environment” part in section **********Extra**********
    > 
    
    > **NOTE 🗒️:** My `conda` environment is named `sparkimental`
    and its python path is `/home/prod/anaconda3/envs/sparkimental/bin/python`
    > 
7. **Config environment for Spark** ☣️
    1. Open `bashrc` 
        
        ```bash
        sudo nano ~/.bashrc
        ```
        
    2. Append these to the end of the file
        
        ```bash
        # 1
        export SPARK_HOME=~/spark-3.3.1-bin-hadoop3
        
        # 2
        export PATH=$PATH:$SPARK_HOME/bin
        export PATH=$PATH:$SPARK_HOME/sbin
        
        # 3
        export PATH=$PATH:~/anaconda3/bin
        
        # 4
        export PATH=$PATH:$JAVA_HOME/jre/bin
        
        # 5
        export PYTHONPATH=<path-to-python-binary-in-your-conda-env> #ex: /home/prod/anaconda3/envs/sparkimental/bin/python
        export PYSPARK_PYTHON=$PYTHONPATH
        export PYSPARK_DRIVER_PYTHON=$PYTHONPATH
        
        # 6 optional
        conda activate <your-conda-env-name> #ex: sparkimental
        ```
        
        🤔 Why these configs? `Explanation` 
        
        Here’re my simple explanation for each of the above lines
        
        1. Here’s just where we installed Spark
        2. Adding Spark’s binary for easy access
        3. Anaconda binaries
        4. JRE binaries
        5. Setting python for `PySpark` driver (master) and worker (slaves)
            
            > ❗Very important that the driver’s python version is the same as the worker’s ([Ref](https://stackoverflow.com/questions/30518362/how-do-i-set-the-drivers-python-version-in-spark))
            > 
        6. This is optional to make sure your wanted `conda` virtual environment is always activated in the shell
    3. Reload bash `source ~/.bashrc`
8. Test Spark
Run some of the below commands and make sure no errors are encounter
   - *************************Some warning might be there though~*************************
    1. `pyspark` → makes sure `pyspark` uses the matching version of python in `sparkimental` (aka our preferred `conda` environment)
        - Should use `python=3.10` (as we configured when we create our python environment - `sparkimental`)
        
        ```yaml
        Using Python version 3.10.6 (main, Oct 24 2022 16:07:47)
        ```
        
        ⚠️ Ubuntu 18.04 default pre-installed python version is 3.6
        Anaconda base python version is 3.9
        
        - So if any of these two versions shows up, your `.bashrc` is likely ill-configured
        - *Refer to Pitfalls section at the end*
        
        ---
        
    2. `spark-shell` → should be no errors
    3. Run cluster test
        - `start-all.sh` (⚠️ If has permission error just change permission of folder)
        - Run `jps` and make sure worker + master is available
            
            ```python
            # Expected output
            3907 Jps
            3723 Master
            3851 Worker
            ```
            
    4. Run an example python code ([Ref](https://stackoverflow.com/questions/25585194/standalone-apache-spark-what-to-put-as-slave-ip-and-port)) 
        
        ```python
        # run from anywhere
        spark-submit --master spark://base-clean:7077 /home/prod/spark-3.3.1-bin-hadoop3/examples/src/main/python/pi.py 10
        ```
        
        The output is expected to:
        
        - Run 10 tasks (we required 10 jobs)
            
            ```python
            ............
            22/11/01 23:13:57 INFO TaskSchedulerImpl: Adding task set 0.0 with 10 tasks resource profile 0
            22/11/01 23:14:00 INFO CoarseGrainedSchedulerBackend$DriverEndpoint: Registered executor NettyRpcEndpointRef(spark-client://Executor) (10.0.2.15:35918) with ID 0,  ResourceProfileId 0
            22/11/01 23:14:00 INFO BlockManagerMasterEndpoint: Registering block manager 10.0.2.15:36705 with 413.9 MiB RAM, BlockManagerId(0, 10.0.2.15, 36705, None)
            22/11/01 23:14:01 INFO TaskSetManager: Starting task 0.0 in stage 0.0 (TID 0) (10.0.2.15, executor 0, partition 0, PROCESS_LOCAL, 4437 bytes) taskResourceAssignments Map()
            22/11/01 23:14:01 INFO BlockManagerInfo: Added broadcast_0_piece0 in memory on 10.0.2.15:36705 (size: 8.6 KiB, free: 413.9 MiB)
            22/11/01 23:14:03 INFO TaskSetManager: Starting task 1.0 in stage 0.0 (TID 1) (10.0.2.15, executor 0, partition 1, PROCESS_LOCAL, 4437 bytes) taskResourceAssignments Map()
            ............
            ```
            
        - Have no Java exception
        - Get result for Pi
            
            ```python
            ............
            22/11/01 23:14:04 INFO DAGScheduler: Job 0 finished: reduce at /home/prod/spark-3.3.1-bin-hadoop3/examples/src/main/python/pi.py:42, took 8.446990 s
            Pi is roughly 3.143960
            ............
            ```
            
        
        > **NOTE 🗒️:** `base-clean` here is the name of the current machine (could check using `hostname` command)
        > 
9. (⏰ Optional) `gparted` (Just in case need to resize disk later) [Ref](https://askubuntu.com/questions/101715/resizing-virtual-drive)
    
    ```bash
    sudo apt-get install gparted
    ```
    
10. Power off 🎊

### Where’re we at

- At this point, we should have a spark capable VM (`spark-installed`) that can:
    - Run `pyspark`
    - Run `spark-submit` examples
    - Has compatible `python/ java/ scala/ spark` versions
    - And with configured `conda` environment easy package management if any thing arises
- All we need to do now is adding master/slave nodes to the spark network and round out our master/slave setup

# New Node

> For every new node added, slave or master, must configure these steps
> 
1. Clone new VM from `base-installed`
2. (⏰ Optional) Rename machine
3. Network setup

***Details below*** ⬇️

## Cloning

> ❗Every time you need to add a new machine to our cluster (IE. a new slave) just clone our fully functional `base-install` VM and continue
> 
1. Decide whether you want to clone in `full` mode or `linked` mode
    
    > ⚡ Personally I would recommend linked clone, just make sure the original virtual storage disk that you’re linking to have enough space
    > 
2. Clone it (prepare to wait for ages if `full clone` is selected)
3. Start up the machine in GUI mode and take note of machine’s IP/name (`ip addr`)
    
    > **NOTE 🗒️:** You can `ssh` to machine using IP from this point onward
    > 
4. (⏰ Optional) Resize storage if needed
*(Refer to Pitfalls section at the end)*

## Renaming Machine

Rename machine for easy distinction from `cli` (since we’ll be accessing them through `ssh` from `shell/bash`)

[Ref1](https://www.cyberciti.biz/faq/ubuntu-change-hostname-command/) [Ref2](https://phoenixnap.com/kb/ubuntu-20-04-change-hostname)

> The name that shows on the bash and network communications (not the name on Virtua Box’s UI
> 

> **NOTE 🗒️:** I’ll use `spark-master` for my master node and `spark-slave-1 (2,3, ..)` for my slaves
> 
1. `sudo nano /etc/hostname` → Delete `<old-name>` and change to your `<new-name>`
2. `sudo nano /etc/hosts` → Change `127.0.1.1 <old-name>` to `127.0.1.1 <new-name>`
3. `sudo hostname <new-name>` 
4. Verify with `hostnamectl` command and `hostname` command
5. Reload machine
6. You should be able to `ssh` to the machine using its name now
    
    ```bash
    # Ex (from local machine)
    ssh prod@spark-master
    
    # Instead of
    ssh prod@<a-long-ip-addr>
    ```
    
    `ip addr` should also output the matching address with machine name
    

## Networking

1. Configure network/IP list 📵
    1. `sudo nano /etc/hosts`
        
        File should contain
        
        ```bash
        127.0.0.1       localhost
        
        # Remove this entry below
        127.0.1.1       <this-current-machine-name> # ex: spark-master
        ```
        
    2. Remove the entry with IP `127.0.1.1` since this is a loop back and will interfere with out access to Spark UI from the browser later 
    *(Refer the Pitfall Section at the end)*
    3. Add all the IPs and names of all machines in the network to this file **(including the current machine’s IP itself)**
    
    ```bash
    # example
    192.168.56.107 spark-master
    192.168.56.108 spark-slave-1
    ```
    
    > ‼️ REMEMBER TO UPDATE THIS LIST WHEVER NEW NODES ARE ADDED
    > 
2. (⏰ Optional) You can `ssh` from current machine to others using their name to make sure they recognize each other on the network
    
    ```yaml
    # from the spark-master's shell
    ssh prod@spark-slave-1
    
    # should prompt for access and password
    ```
    
3. Move on to next step to configure master/slave specifics

# Slave setup

> At this point, slave is already done configured 👷‍♂️
- spark install
- IP configure
> 

Just go to master node ***(next step)*** and update spark’s network config there (`spark-master`)

# Master setup

> Here we round out our spark setup on our master 👑
> 
1. Make sure all the slaves are available in master’s `/etc/hosts`
2. Setup spark master environment 
    
    ```bash
    cd $SPARK_HOME/conf
    cp spark-env.sh.template spark-env.sh
    sudo nano spark-env.sh
    
    # Add
    export  SPARK_MASTER_HOST= <master-ip-addr> # Ex: 192.168.56.107   
    export JAVA_HOME='/usr'
    ```
    
    ❓ How to find Java path❓ ⇒ `which java` ⇒ copy the path before `/bin`
    
3. Add slaves to spark config
    
    ```bash
    cd $SPARK_HOME/conf
    sudo nano slaves #notice the 's'
    
    # add slave name from our network settings here
    spark-master
    spark-slave-1
    ```
    
    > ⚡ I’m starting a worker process on my master node also! (don’t be confused)
    > 
4. Generate `ssh` key if haven’t
    
    ```bash
    ssh-keygen
    ```
    
5. Copy `ssh` key to all other workers
    
    ```bash
    ssh-copy-id prod@spark-master
    ssh-copy-id prod@spark-slave-1
    ```
    
    > ‼️ Remember to update  `$SPARK_HOME/conf/slaves` when you add a new slave. and copy master’s `ssh` key over
    > 
    
    *************************Similarly, can test `ssh` from master to slave to make sure no password prompt is given*
    
6. (⏰ Optional) Setup `history-server` to manage logs of all finished applications
    1. Make a folder to contain the logs
        
        ```bash
        mkdir ~/spark-logs
        ```
        
    2. Config
        
        ```bash
        cd $SPARK_HOME/conf
        cp spark-defaults.conf.template spark-defaults.conf
        sudo nano spark-defaults.conf
        
        # add these lines
        spark.eventLog.enabled           true
        spark.eventLog.dir file://~/spark-logs
        spark.history.fs.logDirectory file://~/spark-logs
        ```
        
    3. Run `start-history-server.sh`
    4. `jps` should show `HistoryServer` as an entry
    5. Verify by going to `spark-master:18080` or `<master-ip>:18080` 
        
        ![Untitled](images/spark-cluster-setup/Untitled%206.png)
        
7. Test Spark’s cluster setup 
    1. Run the cluster (master + all slaves)
        
        ```bash
        start-all.sh
        ```
        
    2. `jps` output should have `Worker` and `Master` process
        
        ```bash
        3645 Worker
        3533 Master
        ```
        
    3. Verify on the browser at link `spark-master:8080`
        
        ![Notice our workers on their respective IP address](images/spark-cluster-setup/Untitled%207.png)
        
        Notice our workers on their respective IP address
        
        No applications as for now since haven’t test anything
        
8. Run example and see results
    
    > We’ll be running the simple Pi calculation example available with our spark installation to verify that our cluster operate properly
    > 
    1. Make sure that the master/slaves are running (also history server if you configured it)
        
        ```bash
        jps
        
        # expected output
        4658 Jps
        4396 HistoryServer
        3886 Master
        3999 Worker
        ```
        
    2. Run `spark-submit` to our running cluster
        
        ```bash
        cd $SPARK_HOME	
        spark-submit --master spark://spark-master:7077 ./examples/src/main/python/pi.py 10
        ```
        
    3. (If you have history server) Go to history server (`spark-master:18080`)
        - This log should be present
        
        ![Untitled](images/spark-cluster-setup/Untitled%208.png)
        
        - Go into the job for more detail
        
        ![Untitled](images/spark-cluster-setup/Untitled%209.png)
        
        ![Untitled](images/spark-cluster-setup/Untitled%2010.png)
        
        - Go all the way to details and you will see our Job with 10 tasks distributed over our two configured workers
        
        ![Untitled](images/spark-cluster-setup/Untitled%2011.png)
        
        ![Untitled](images/spark-cluster-setup/Untitled%2012.png)
        
        - You can go to other tabs for more details
            
            Executor tab shows 1 driver and 2 workers executor
            
        
        ![Untitled](images/spark-cluster-setup/Untitled%2013.png)
        

🎉 **And that’s our spark cluster ready for use** 🎉

> 🍖 **Extra:** If you don’t wanna have to specify master node option `--master spark://...` every time your run `spark-submit`,  just set master by appending:   
`spark.master spark://spark-master:7077` in `$SPARK_HOME/conf/spark-defaults.conf`
> 

# How to write code for the cluster

## Using spark-submit

Simple, just 

```python
import pyspark

# do your code
```

And submit with `spark-submit <path-to-py-file>`

## Using python

> `python` binary does not know about our local installation of `pyspark` so we need a supporting package called `findspark`
> 

```python
# this first
import findspark
findspark.init()
findspark.find()

# then import pyspark
import pyspark

# your codes
```

Run with `python <path-to-py-file>`

❗**Note:** Remember to set the master as the current running master node in our cluster, either by 

- setting it `spark.master` as default in `$SPARK_HOME/config/spark-defaults.conf`
- setting it in your script (`.py`) using **`SparkConf`** ([Ref](https://spark.apache.org/docs/3.1.1/api/python/reference/api/pyspark.SparkConf.html#pyspark.SparkConf))
    
    ```python
    conf = SparkConf()
    conf.setMaster("spark://spark-master:7077")
    sc = SparkContext.getOrCreate(conf)
    ```
    

⚠️ If you don’t config this, you code would be ran on a newly created (and temporary) process on the master node instead of being summited to your currently running cluster

## Using Notebook

> `Jupyter` should only meant for development/debugging purposes, real production code should be summited to cluster through `spark-submit`
> 
1. Make sure `jupyter` is installed
2. Start `jupyter` notebook process with `jupyter notebook` from your master node (`spark-master`)
3. Open an `ssh` tunnel from local machine to `spark-master`
    
    ```python
    ssh -N -L 8888:localhost:8888 prod@spark-master
    # this makes anyone accessing localhost:8888 be tunneled to prod@spark-master:8888
    ```
    
4. In your local machine, go to `localhost:8888` and input the access token/password to start working
5. (🗒️ Note) make sure you select your wanted python environment as kernel in the notebook ([Ref](https://towardsdatascience.com/get-your-conda-environment-to-show-in-jupyter-notebooks-the-easy-way-17010b76e874))
    
    ```python
    conda activate spakimental # if not already
    ipython kernel install --user --name=sparkimental 
    
    # then select "sparkimental" in notebook
    ```
    
6. Similar to running directly using `python` bin, our code need these steps
    1. Find spark
        
        ```python
        import findspark
        findspark.init()
        findspark.find()
        ```
        
    2. Configure
        
        ```python
        from pyspark import SparkConf
        conf = SparkConf()
        # if not already configured in spark-defaults.conf
        conf.setMaster('spark://spark-master:7077')
        # if you dont set app name, our jupyter job will be named `spark-shell`
        conf.setAppName('jupyter job'); 
        ```
        
    3. Create Spark context and go crazy
        
        ```python
        sc = SparkContext.getOrCreate(conf)
        ```
        
        The `spark-master` web UI at `spark-master:8080` should show a new running application as soon as the above line in executed
        
        ![Untitled](images/spark-cluster-setup/Untitled%2014.png)
        

# Extras

> From a `config.yml` file
> 

```yaml
# example conda.env.yml config file content
name: sparkimental # this is environment name
dependencies: # and the packages we need
	# must have these 2
	- python=3.10
	- conda-forge::findspark
	# NOTE! don't install pyspark and java here since we already installed them
	# ones below are optional
	- jupyter
	- ipython
	- nltk
	- ipykernel
	- numpy
```

- Create environment from config file
    
    `conda env create -f conda.env.yml`
    
    ❗Careful about the `yml` file ([ref](https://stackoverflow.com/questions/57381678/how-to-create-conda-environment-with-yml-file-without-this-error))
    
- Please activate environment before any other steps, always make sure you’re executing code in the correct `conda` environment
    
    `conda activate sparkimental`
    
- **If** want to remove environment
    
    `conda activate base`
    
    `conda env remove -n sparkimental -y`
    

# Pitfalls

- Run out of storage → [(How to resize)](https://askubuntu.com/questions/101715/resizing-virtual-drive)
- Not allowed to create log while running spark → Just change permission of the folder being access denied `chmod -R 777 dirname`
- What is the default service port that spark master listens on? `7077` ([Ref 1](https://spark.apache.org/docs/latest/spark-standalone.html), [Ref 2](https://stackoverflow.com/questions/25585194/standalone-apache-spark-what-to-put-as-slave-ip-and-port))
- Python mismatch between worker and driver → Just make sure both are set to the same python (use absolute path recommended)
    - [Mismatching Ref](https://stackoverflow.com/questions/54115290/mismatch-between-python-version-in-spark-worker-and-spark-driver)
    - [How to check all python versions on Linux](https://stackoverflow.com/questions/30464980/how-to-check-all-versions-of-python-installed-on-osx-and-centos)
- Loopback IP problem with Spark ([Problem description](https://support.datastax.com/s/article/Spark-hostname-resolving-to-loopback-address-warning-in-spark-worker-logs))
    
    ```python
    Your hostname, ... resolves to a loopback address: 127.0.0.1; using 10.1.2.1 instead
    ```
    
    ⇒ Solve by removing the `127.0.1.1` entry from `/etc/hosts`
    

# References

> This post is mainly based on ideas/guidance from these below 🙇, my thanks to all the other authors ❣️
> 
- Basic `PySpark` tutorial: [https://www.guru99.com/pyspark-tutorial.html#4](https://www.guru99.com/pyspark-tutorial.html#4)
- How to setup `Spark` cluster: [https://medium.com/@jootorres_11979/how-to-install-and-set-up-an-apache-spark-cluster-on-hadoop-18-04-b4d70650ed42](https://medium.com/@jootorres_11979/how-to-install-and-set-up-an-apache-spark-cluster-on-hadoop-18-04-b4d70650ed42)
- Running `PySpark` with `Jupyter` notebook: [https://blog.devgenius.io/a-convenient-way-to-run-pyspark-4e84a32f00b7](https://blog.devgenius.io/a-convenient-way-to-run-pyspark-4e84a32f00b7)
- Spark History Server setup: [https://sparkbyexamples.com/spark/spark-history-server-to-monitor-applications/](https://sparkbyexamples.com/spark/spark-history-server-to-monitor-applications/)

# Conclusion

And there we have it 🥳 a fully functional VM cluster that runs spark that you can manage from your local machine and run code in what ever way you want.

********************Please do comment your thought on my topic and clap if it helped in any ways. Would love to hear from you******************** 😸

Thanks for reading 🖤, keep Sparkling 😉💫
