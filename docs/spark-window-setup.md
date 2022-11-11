# Project doc

⚠️ This doc is in-complete and will not be updated. Use at your own risk
# Setting up Spark in Windows

```text
Careful of many errors that might happen in this process :(
```

### **********Steps**********

1. Install `Anaconda` (aka `Conda`) to manage python virtual environment for easy development environment managing/setting up
2. Create virtual development environment in `Conda` using my predefined config file `conda.env.yml`
3. Make sure `JupyterNotebook` works with `Conda`
4. Download an appropriate version of `winutils` for hadoop [Link](https://github.com/steveloughran/winutils)
5. Use the notebook `/scripts/window-setup/test-spark` for testing spark configuration
6. (Optional) If fail step 3, Install `Java JDK 8` and repeat step 3

### More details

************Step 1************

Follow: [https://docs.anaconda.com/anaconda/install/windows/](https://docs.anaconda.com/anaconda/install/windows/)

************Step 2************

> NOTE: make sure to have pyspark on your python environment

Follow `Create Anaconda environment` Section in this file

**Step 3**

> Note that the `conda` environment created from `conda.env.yml` already have `jupyter` installed, you just need to make sure that `jupyter` notebook works properly

If you’re using plain `JupyterNotebook`

- Run `jupyter notebook` to start notebook in browser
- Open any notebook and make sure you can select our `sparkimental` virtual environment as a kernel
- Reference [this link](https://towardsdatascience.com/get-your-conda-environment-to-show-in-jupyter-notebooks-the-easy-way-17010b76e874) for possible fixes

If you’re using the notebook in `VSCode`

- Reference [this link](https://towardsdatascience.com/installing-jupyter-notebook-support-in-visual-studio-code-91887d644c5d)

************Step 4************

Just download from [link](https://github.com/steveloughran/winutils) and take note the hadoop path `...winutils/hadoop-3.0.0`

************Step 5************

Just run the `test-spark.ipynb` and make sure all passes

**NOTE:**

1. Make sure `HADOOP_HOME` is set

    ```[python]
    hadoop_home_path = f'{cwd}/windows/winutils/hadoop-3.0.0'
    os.environ['HADOOP_HOME'] = hadoop_home_path
    sys.path.append(f'{hadoop_home_path}/bin')
    ```

******Step 6******

Code not running? Fail Error: `Port something not ready something bla bla`? - could be because of Java

Install `Java JDK` by following [this link](https://www.guru99.com/install-java.html)

<aside>
💡 I’m not sure if it’s needed or not to set the environment variables (PATH, CLASSPATH). Test it out as you will.

</aside>

************Step 6************

Just run `test-pipeline.ipynb`

### Some references

<aside>
💡 In case you fail in the middle and needs some resource to fix it yourself

</aside>

1. [https://www.guru99.com/pyspark-tutorial.html#4](https://www.guru99.com/pyspark-tutorial.html#4)
2. [https://sparkbyexamples.com/pyspark/install-pyspark-in-anaconda-jupyter-notebook/](https://sparkbyexamples.com/pyspark/install-pyspark-in-anaconda-jupyter-notebook/)
3. [https://stackoverflow.com/questions/32215782/set-up-hadoop-home-variable-in-windows](https://stackoverflow.com/questions/32215782/set-up-hadoop-home-variable-in-windows)

# How to❔

## Create Anaconda environment

- Create environment from config file
    
    `conda env create -f conda.env.yml`
    
    ❗Careful about the `yml` file ([ref](https://stackoverflow.com/questions/57381678/how-to-create-conda-environment-with-yml-file-without-this-error))
    
- Please activate environment before any other steps, always make sure you’re executing code in the correct `conda` environment
    
    `conda activate sparkimental`
    
- **If** want to remove environment
    
    `conda activate base`
    
    `conda env remove -n sparkimental -y`
