# KeckLFC
Copyright (c) Caltech, Maodong Gao, 2021-2023

This is control package for Laser Frequency Comb in Keck Observatory

# Installation

The texts <mark> highlighted like this</mark> are <mark>**Actions** you need to execute</mark>. Please read them carefully.

Other texts are explanations of the purpose of these actions. You can skip them **only if** you are familiar with the respective part.

This installation guide is written for Windows 11 platform. It should be similar **(but untested)** for other operating systems.


## Step 1: Install Anaconda and prepare the environment

This part typically takes 5-20 minutes. Please be patient.

Anacoda is a free and open-source Python (and R) package manager that aims to simplify package management and deployment. And typically is also recommended for installation of many other python packages (Not only for KeckLFC). For KeckLFC, it is **highly recommended** to use Anaconda to manage python packages, to save you from dependency hell.

Without Anaconda, the package installation can be complicated because of the dependencies of different packages, **especially when you have other python packages already installed for other purposes**.


### 1.1: Download and install Anaconda

<mark>IF you already have Anaconda installed, you may skip this step.</mark>

- <mark> Download Anaconda installation package from [https://www.anaconda.com/download/] (https://www.anaconda.com/download/). 
</mark>

- <mark> Run the installation package and follow the DEFAULT instructions.
</mark>

> Note: DEFAULT instructions means **you don't need to change any settings during the installation. Just click "Next" or "Continue" until the installation is finished.** This procedure has been tested and works fine. You may modify the settings if you know what you are doing.


### 1.2: Open Anaconda Prompt (will be referred as terminal) and verify Anaconda installation

Anacoda Prompt (also called terminal in this guide) is a terminal-like interface for Anaconda. Anaconda also has a graphic user interface (GUI), but we will not use it now.

Anacoda Prompt can be used to execute commands for package management. And <mark>all following commands described later that states **... in terminal** should be executed in Anaconda Prompt.</mark>

- <mark> Open Anaconda Prompt by searching "Anaconda Prompt" in Windows search bar. </mark>

You should see a terminal-like window pops up. The window title should be something like "Anaconda Prompt (base)". And the command prompt should be something like "(base) C:\Users\your_user_name>".

 The **"(base)"** means you are in the base environment of Anaconda. All packages installed in this environment will be available for all other environments. So **if you do any package installation in (base), it will be available for all other environments and WILL POTENTIALLY CAUSE PACKAGE CONFLICTS**. So it is **important keep (base) clean** and only install packages in other environments.

 > Note: 
 >- You may check if your (base) environment is clean by running `conda list` in terminal. 
 >- You may also find Anaconda GUI useful for package management. You can open it by searching "Anaconda Navigator" in Windows search bar. The list of packages in (base) environment can be found in "Environments" tab.
>- If you see a list of packages, you may want to clean them by running `conda clean --all` in terminal, make sure you see (base) in the command prompt. This will remove all packages in (base) environment. **This is not necessary if you have just installed Anaconda.**


- <mark> Verify the installation by running `conda --version` in terminal.</mark>

You should see something like "conda 4.10.3" in the terminal. If you see something like "conda is not recognized as an internal or external command, operable program or batch file.", please refer to the Common issues and solution suggestions for Anaconda installation section below.

### 1.3: Create a new environment

- <mark>Create a new environment for KeckLFC by running `conda create -n lfc-env` in terminal.</mark>

> Note: lfc-env is the name of the environment. You can change it to any name you like. But please remember the name you choose. You will need it later. I recommend you attach "-env" to the name to indicate it is an environment, otherwise it may be confused with package names.

- <mark> Type 'Y' and press Enter to confirm if you see a prompt like "Proceed ([y]/n)?".</mark>

If the environment is created successfully, you should see something like "Preparing transaction: done", "Verifying transaction: done", "Executing transaction: done" in the terminal.

- <mark> Activate the environment by running `conda activate lfc-env` in terminal.</mark>

You should see the command prompt changes to something like "(lfc-env) C:\Users\your_user_name>". This means you are now in the environment you just created. All packages you install now will be installed in this environment. **Please make sure you see (lfc-env) in the command prompt before you install any packages.**

> Note: If you selected a different name for the environment, please replace "lfc-env" with the name you choose.


### 1.end: Common issues and solution suggestions for Anaconda installation

If you have trouble installing Anaconda **(which rarely happens for Windows user)**, generally you may try use miniconda instead. Miniconda is a minimal version of Anaconda. It is smaller and easier to install. But it does not include graphical user interface (GUI) and some other packages. You can download miniconda from [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html). The installation procedure is similar to Anaconda.

> Other useful links: 
> - If you have trouble installing Anaconda, please refer to https://docs.anaconda.com/anaconda/install/ for more information.
> - If you have trouble running Anaconda Prompt (or running `conda --version` in terminal), please refer to https://docs.anaconda.com/anaconda/user-guide/getting-started/ for more information.
> - If you have trouble creating a new environment, please refer to https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html for more information.


## Step 2: Install dependent packages for `KeckLFC`

<mark> BEFORE PROCEDING THIS STEP, make sure you see (lfc-env) in the command prompt shown in terminal. If not, please run `conda activate lfc-env` in terminal.</mark>

> Note: If you selected a different name for the environment, please replace "lfc-env" with the name you choose.

### 2.1 Install pyvisa

pyvisa is a python package for instrument control. You can find more information about pyvisa in https://pyvisa.readthedocs.io/en/latest/.

- <mark>Run `conda install -c conda-forge pyvisa` in terminal.</mark>

You should see a list of packages to be installed. 

- <mark> Type "y" and press enter to confirm the installation if you see a prompt like "Proceed ([y]/n)?".</mark>

You should see something like "Successfully installed ..." 

### 2.2 Install numpy, scipy, matplotlib

numpy, scipy, matplotlib are python packages for scientific computing. You can find more information about them in https://numpy.org/, https://www.scipy.org/, https://matplotlib.org/.

- <mark> Run `conda install numpy scipy matplotlib` in terminal. </mark>

You should see a list of packages to be installed.

- <mark> Type "y" and press enter to confirm the installation if you see a prompt like "Proceed ([y]/n)?".</mark>

-- 2.3 Install mcculw (for USB-2408 DAQ)

Run `pip install mcculw` in terminal.

-- 2.4 Install wsapi (for Finisar WaveShaper)

Follow the instructions in https://ii-vi.com/use-64-bit-python-3-7-to-control-the-waveshaper-through-the-usb-port/ for connection guide


### 2.end: Common issues and solution suggestions for package installation

If you have trouble installing any of the above packages, first make sure you are starting with a clean environment. The environment may not be clean for several reasons:

- You already have other packges installed in the environment. This is simple to check by running `conda list` in terminal. If you see a list of packages, you may want to clean them by running `conda clean --all` in terminal, make sure you see (lfc-env) in the command prompt. This will remove all packages in (lfc-env) environment. **This is not necessary if you have just created the environment.**
- You specified a python version when creating the environment. (This means you ran `conda create -n lfc-env python=3.7` in terminal when creating the environment.) This is also simple to check by running `conda info` in terminal. If you see something like "python version : 3.7.10.final.0", you may want to remove the environment by running `conda deactivate` to deactivate the environment first. Then run `conda remove --name lfc-env --all` in terminal, make sure you see (base) in the command prompt. This will remove the environment. Then you can re-create a new environment without specifying python version by running `conda create -n lfc-env` in terminal, make sure you see (base) in the command prompt. Then you can activate the environment by running `conda activate lfc-env` in terminal, make sure you see (lfc-env) in the command prompt. Then you can install packages by following the instructions in 2.1-2.4.
- (base) is not clean. Please refer to the note in 1.2 for more information.

> Other useful links:
> - If you have trouble installing package `pyvisa`, please refer to https://pyvisa.readthedocs.io/en/latest/getting.html for more information.
> - If you have trouble installing package `numpy`, please refer to https://numpy.org/install/ for more information.


## Step 2: Install python Integrated Development Environment (IDE): Visual Studio Code





