# KeckLFC
Copyright (c) Caltech, Maodong Gao, 2021-2023

This is control package for Laser Frequency Comb in Keck Observatory

# Installation

The texts **bolded like this** are **_Actions_ you need to execute**. Please read them carefully.

Other texts are explanations of the purpose of these actions. You can skip them ***only if*** you are familiar with the respective part.

This installation guide is written for Windows 11 platform. It should be similar ***(but untested)*** for other operating systems.


## Step 1: Install Anaconda and prepare the environment

This part typically takes 5-20 minutes. Please be patient.

Anacoda is a free and open-source Python (and R) package manager that aims to simplify package management and deployment. And typically is also recommended for installation of many other python packages (Not only for KeckLFC). For KeckLFC, it is ***highly recommended*** to use Anaconda to manage python packages, to save you from dependency hell.

Without Anaconda, the package installation can be complicated because of the dependencies of different packages, ***especially when you have other python packages already installed for other purposes***.


### 1.1: Download and install Anaconda

**IF you already have Anaconda installed, you may skip this step.**

- **Download Anaconda installation package from [https://www.anaconda.com/download/] (https://www.anaconda.com/download/).**

- **Run the installation package and follow the DEFAULT instructions.**

> Note: DEFAULT instructions means ***you don't need to change any settings during the installation. Just click "Next" or "Continue" until the installation is finished.*** This procedure has been tested and works fine. You may modify the settings if you know what you are doing.


### 1.2: Open Anaconda Prompt (will be referred as terminal) and verify Anaconda installation

Anacoda Prompt (also called terminal in this guide) is a terminal-like interface for Anaconda. Anaconda also has a graphic user interface (GUI), but we will not use it now.

Anacoda Prompt can be used to execute commands for package management. And **all following commands described later that states ***... in terminal*** should be executed in Anaconda Prompt.**

- **Open Anaconda Prompt by searching "Anaconda Prompt" in Windows search bar.**

You should see a terminal-like window pops up. The window title should be something like "Anaconda Prompt (base)". And the command prompt should be something like "(base) C:\Users\your_user_name>".

 The ***"(base)"*** means you are in the base environment of Anaconda. All packages installed in this environment will be available for all other environments. So ***if you do any package installation in (base), it will be available for all other environments and WILL POTENTIALLY CAUSE PACKAGE CONFLICTS***. So it is ***important keep (base) clean*** and only install packages in other environments.

 > Note: 
 >- You may check if your (base) environment is clean by running `conda list` in terminal. 
 >- You may also find Anaconda GUI useful for package management. You can open it by searching "Anaconda Navigator" in Windows search bar. The list of packages in (base) environment can be found in "Environments" tab.
>- If you see a list of packages, you may want to clean them by running `conda clean --all` in terminal, make sure you see (base) in the command prompt. This will remove all packages in (base) environment. ***This is not necessary if you have just installed Anaconda.***


- **Verify the installation by running `conda --version` in terminal.**

You should see something like "conda 4.10.3" in the terminal. If you see something like "conda is not recognized as an internal or external command, operable program or batch file.", please refer to the Common issues and solution suggestions for Anaconda installation section below.

### 1.3: Create a new environment

- **Create a new environment for KeckLFC by running `conda create -n lfc-env` in terminal.**

> Note: lfc-env is the name of the environment. You can change it to any name you like. But please remember the name you choose. You will need it later. I recommend you attach "-env" to the name to indicate it is an environment, otherwise it may be confused with package names.

- **Type 'Y' and press Enter to confirm if you see a prompt like "Proceed ([y]/n)?".**

If the environment is created successfully, you should see something like "Preparing transaction: done", "Verifying transaction: done", "Executing transaction: done" in the terminal.

- **Activate the environment by running `conda activate lfc-env` in terminal.**

You should see the command prompt changes to something like "(lfc-env) C:\Users\your_user_name>". This means you are now in the environment you just created. All packages you install now will be installed in this environment. ***Please make sure you see (lfc-env) in the command prompt before you install any packages.***

> Note: If you selected a different name for the environment, please replace "lfc-env" with the name you choose.


### 1.end: Common issues and solution suggestions for Anaconda installation

If you have trouble installing Anaconda ***(which rarely happens for Windows user)***, generally you may try use miniconda instead. Miniconda is a minimal version of Anaconda. It is smaller and easier to install. But it does not include graphical user interface (GUI) and some other packages. You can download miniconda from [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html). The installation procedure is similar to Anaconda.

> Other useful links: 
> - If you have trouble installing Anaconda, please refer to https://docs.anaconda.com/anaconda/install/ for more information.
> - If you have trouble running Anaconda Prompt (or running `conda --version` in terminal), please refer to https://docs.anaconda.com/anaconda/user-guide/getting-started/ for more information.
> - If you have trouble creating a new environment, please refer to https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html for more information.


## Step 2: Install dependent packages for `KeckLFC`

**BEFORE PROCEDING THIS STEP, make sure you see (lfc-env) in the command prompt shown in terminal. If not, please run `conda activate lfc-env` in terminal.**

> Note: If you selected a different name for the environment, please replace "lfc-env" with the name you choose.

We will use both conda and pip to install packages because some packages are not available in conda. To use `pip` we need to install it first.

- **Run `conda install pip` in terminal.**

You should see a list of packages to be installed.

- **Type "y" and press enter to confirm the installation if you see a prompt like "Proceed ([y]/n)?". You may also need to do this for the following package installation.** Text **bolding** for this _Action_ will be omitted for the following package installation.

You should see something like "Successfully installed ..." in the terminal if the installation is successful.

### 2.1 Install pyvisa

pyvisa is a python package for instrument control. You can find more information about pyvisa in https://pyvisa.readthedocs.io/en/latest/.

- **Run `conda install -c conda-forge pyvisa` in terminal.**

You should see a list of packages to be installed. 

- Type "y" and press enter to confirm the installation if you see a prompt like "Proceed ([y]/n)?".

You should see something like "Successfully installed ..." in the terminal if the installation is successful.

### 2.2 Install numpy, scipy, matplotlib

numpy, scipy, matplotlib are python packages for scientific computing. You can find more information about them in https://numpy.org/, https://www.scipy.org/, https://matplotlib.org/.

- **Run `conda install numpy scipy matplotlib` in terminal.**

You should see a list of packages to be installed.

- Type "y" and press enter to confirm the installation if you see a prompt like "Proceed ([y]/n)?".

You should see something like "Successfully installed ..." in the terminal if the installation is successful.

### 2.3 Install mcculw (for USB-2408 DAQ)

***USB-2408 DAQ is used to monitor the temperature of the instruments. It is not necessary for the operation of KeckLFC.***

`mcculw` is a python package for USB-2408 DAQ. You can find more information about mcculw in https://www.mccdaq.com/PDFs/Manuals/USB-2408-2-4.pdf.

- **Run `pip install mcculw` in terminal.**

You should see a list of packages to be installed.

- Type "y" and press enter to confirm the installation if you see a prompt like "Proceed ([y]/n)?".

You should see something like "Successfully installed ..." in the terminal if the installation is successful.

### 2.4 Install wsapi (for Finisar WaveShaper)

- **Install waveshaper driver from https://ii-vi.com/product-category/products/optical-communications/optical-instrumentation/. Go to tag "Software & Drivers", download and install** 
-- **WaveAnalyzer GUI Software 1.9.0**
-- **WaveManager Set-up 2.7.5**
-- **WaveShaper App Setup 2.2.0**

> Note: The above **three** Apps are all necessary for the installation of wsapi. A common mistake is to only install one of the above. This will cause the folllowing installation of wsapi to fail. 

- **Check you can find folder C:\Program Files (x86)\Finisar\WaveManager\waveshaper**

> Note added by Greg: If you can't find it, please check again you indeed installed **all the three** Apps above.

- **Follow DEFAULT download procedure. Especially oo not change the default installation path.**

[TODO: Add more information on wsapi install. Download those necessary files and put them in the repo. Copy the online instructions here.]

- **Follow the instructions in [https://ii-vi.com/use-64-bit-python-3-7-to-control-the-waveshaper-through-the-usb-port/](https://ii-vi.com/use-64-bit-python-3-7-to-control-the-waveshaper-through-the-usb-port/) to install wsapi.**



> Note: The following instructions are copied from the above link. Please refer to the above link for more information.
> In order to control the WaveShaper through USB using 64-bit Python 3.7 please follow these instructions:

> Load up the Command Prompt as administrator and change to the Python directory using the following command:
> `cd C:\Program Files (x86)\Finisar\WaveManager\waveshaper\api\python3`

> Run the setup.py script via this command:

> `python setup.py install`

**If you get access denied errors, you may need to run these commands as administrator. To do this, right click on the Command Prompt icon and select ‘Run as administrator’. Then repeat this step over again. Also don't forget to check you are in the right environment. You should see (lfc-env) in the command prompt. (If not please run `conda activate lfc-env` in terminal.)**

> You must copy over the correct DLL files into the appropriate Windows folder. 64-bit Python requires the 64 bit DLLs to be copied into the System32

> Copy this file: C:\Program Files (x86)\Finisar\WaveManager\waveshaper\bin\amd64\wsapi.dll into this folder C:\Windows\System32

> Copy this file: C:\Program Files (x86)\Finisar\WaveManager\waveshaper\bin\amd64\ftd2xx64.dll into this folder C:\Windows\System32

> Rename the copied file above from ftd2xx64.dll to ftd2xx.dll.

> Copy this file: C:\Program Files (x86)\Finisar\WaveManager\waveshaper\bin\amd64\ws_cheetah64.dll into this folder C:\Windows\System32

> Rename the copied file above from ws_cheetah64.dll to ws_cheetah.dll.

> We can now test to see if the installation was successful. Load up Python 3.7. Import the wsapi library using the following command:

> `from wsapi import *`

> Return the API version number

> `ws_get_version()`

> This command should return a version number e.g. ‘2.7.3’. If it returns -1, then the DLL was not loaded correctly. You may wish to double-check step 3, restart Python and try again. If you still have trouble, please contact waveshaper@finisar.com.



### 2.5 Install loguru (for local logging)

loguru is a python package for logging. Locally logging is used to record the commands sent to the instruments and the responses from the instruments. (This function is updated during test in July 2023)

- **Run `pip install loguru` in terminal.**

You should see a list of packages to be installed. 

- Type "y" and press enter to confirm the installation if you see a prompt like "Proceed ([y]/n)?".

You should see something like "Successfully installed ..." in the terminal if the installation is successful.



### 2.end: Common issues and solution suggestions for package installation

If you have trouble installing any of the above packages, first make sure you are starting with a clean environment. The environment may not be clean for several reasons:

- You already have other packges installed in the environment. This is simple to check by running `conda list` in terminal. If you see a list of packages, you may want to clean them by running `conda clean --all` in terminal, make sure you see (lfc-env) in the command prompt. This will remove all packages in (lfc-env) environment. ***This is not necessary if you have just created the environment.***
- You specified a python version when creating the environment. (This means you ran `conda create -n lfc-env python=3.7` in terminal when creating the environment.) This is also simple to check by running `conda info` in terminal. If you see something like "python version : 3.7.10.final.0", you may want to remove the environment by running `conda deactivate` to deactivate the environment first. Then run `conda remove --name lfc-env --all` in terminal, make sure you see (base) in the command prompt. This will remove the environment. Then you can re-create a new environment without specifying python version by running `conda create -n lfc-env` in terminal, make sure you see (base) in the command prompt. Then you can activate the environment by running `conda activate lfc-env` in terminal, make sure you see (lfc-env) in the command prompt. Then you can install packages by following the instructions in 2.1-2.4.
- (base) is not clean. Please refer to the note in 1.2 for more information.

> Other useful links:
> - If you have trouble installing package `pyvisa`, please refer to https://pyvisa.readthedocs.io/en/latest/getting.html for more information.
> - If you have trouble installing package `numpy`, please refer to https://numpy.org/install/ for more information.


## Step 3: [OPTIONAL] Install Arduino Integrated Development Environment (IDE)

***This step is optional if you don't wish to modify the logic that is already implemented in Arduino board.***

Arduino is an open-source electronics platform based on easy-to-use hardware and software. You can find more information about Arduino in https://www.arduino.cc/. 

> Note: In Keck Laser Frequency Comb, we use Arduino to serve as a latched relay circuit to protect Pritel Amplifier. If the input power of Pritel amplifier is too low, it can cause a Q-switch failure and damage the amplifier/ pulse compressor/ ocatve waveguide. The Q-switch failure happens in a time scale of mili-seconds, which means we need a fast protection circuit to protect the amplifier. 

> Here, we use an analog relay circuit and an Arduino controlled relay circuit connected in series as input to Pritel amplifier interlock, to serve as a latched relay circuit. The analog relay circuit will turn off the power of Pritel amplifier immediately (in miliseconds) if the input power is too low. The Arduino controlled relay circuit will prevent turn on the power of Pritel amplifier if the input power is back to threshold, which realize the latching of the series circuit. The Arduino controlled relay circuit will also send a signal to the computer to indicate the status of the latched relay circuit. The computer will use this signal to trigger alarm to user.

> If user wish to turn on the power of Pritel amplifier after the latched relay circuit is triggered, user need to manually reset the latched relay circuit by sending command "RESET" to Arduino. The Arduino controlled relay circuit will then turn on the power of Pritel amplifier if the input power is back to threshold (Arduino will not respond if input power is still too low). 

> Furthermore [TODO]. Arduino will also serve as a controller for "blue screen death" for the computer. Arduino will regularly send try to communicate with the computer and if the computer is not responding, Arduino will turn off the power of Pritel amplifier to put the system in "SAFE" mode.

[TODO: add more information about IDE download and installation]
- **Follow the instructions in [https://www.arduino.cc/en/software](https://www.arduino.cc/en/software) to install Arduino IDE.**


## Step 4: Download this repository

This step will help you fork this repository to your local computer. You can also download the repository directly from Github website. Direct download should be easier but you will not be able to push your changes to the repository.

**Choose one of the following options to fork or download the repository to your local computer.**

### (Option 1, do this only if you are familiar with github) 4.1: Install Github Desktop and clone the repository

This can be complicated if you are not familiar with Github. But this will allow you to push your changes to the repository and pull the latest version of the repository to your local computer.

- **Follow the instructions in [https://docs.github.com/en/desktop/installing-and-configuring-github-desktop/installing-and-authenticating-to-github-desktop/installing-github-desktop](https://docs.github.com/en/desktop/installing-and-configuring-github-desktop/installing-and-authenticating-to-github-desktop/installing-github-desktop) to install Github Desktop.**

### (Option 2, easiest way) 4.2: Download the repository directly from Github website

This is most straightforward way to download the repository. But you will not be able to push your changes to the repository and pull the latest version of the repository to your local computer. You will need to download the repository again if you want to get the latest version of the repository.

- **click the green button "Code" on the top right corner of this page, then click "Download ZIP".**

- **Unzip the downloaded file to your local computer.**

- **Save the unzipped files to your project folder.**

### (UNAVAILABLE YET) 4.3: Download repo from pypi using pip

[TODO: upload the repo to pypi]


## Step 5 : [OPTIONAL] Install python Integrated Development Environment (IDE): Visual Studio Code (VScode)

***This step is optional if you don't like VScode as your programming tool. You can use any other IDE you like.***

### 5.1 Download VScode

- **Follow the instructions in [https://code.visualstudio.com/download](https://code.visualstudio.com/download) to download VScode.**

>Note added by Greg: Needed to click on the windows button install, NOT the “installer” or “.zip” or “CLI” buttons.

### 5.2: Open your project folder in VScode and select the python environment

- 1. Open your project folder in VScode

    **Open your project folder in VScode by clicking "File" -> "Open Folder" in VScode.**

- 2. Select the python environment
    
    **Use the Python: Select Interpreter command from the Command Palette (Ctrl+Shift+P) to select the python environment.**

    > For more information,  Follow the instructions in [https://code.visualstudio.com/docs/python/environments](https://code.visualstudio.com/docs/python/environments) to select the python environment. 

### 5.3: Install extensions in VScode

***This step is OPTIONAL at the beginning.***

> Note: VScode has already provided user friendly interface to install extensions. And those extensions typically can be installed ***when you actually need them***. So you don't necessarily need to follow the following instructions and install all the extensions at the beginning.

- 1. Install python extension in VScode

 Follow the instructions in [https://code.visualstudio.com/docs/python/python-tutorial](https://code.visualstudio.com/docs/python/python-tutorial) to install python extension in VScode.

- 2. Install jupyter extension in VScode

 Follow the instructions in [https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) to install jupyter extension in VScode.

- 3. Install git extension in VScode (optional)

  Follow the instructions in [https://code.visualstudio.com/docs/editor/github](https://code.visualstudio.com/docs/editor/github) to install git extension in VScode. 


## Step 6: Install Keysight IO Libraries Suite

Keysight IO Libraries Suite is a collection of libraries and tools that help you to quickly and easily connect your test instruments to your PC. You can find more information about Keysight IO Libraries Suite in https://www.keysight.com/us/en/software/application-sw/keysight-io-libraries-suite.html.

> Note: In Keck Laser Frequency Comb, we use Keysight IO Libraries Suite to communicate with not only KeySight equipments. [TODO: Identify what specifically are using it]

**Follow the instructions in [https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html](https://www.keysight.com/us/en/lib/software-detail/computer-software/io-libraries-suite-downloads-2175637.html) to install Keysight IO Libraries Suite.**

> Note added by Greg: If the above link is broken, you may search 'Keysight IO Libraries Suite' in Google or in Keysight.com. The link should be easy to find.

## Step 7: Install Ni-Max

Ni-Max is a software that helps you to manage your National Instruments (NI) devices. It is also the software that you can use to communicate with NI devices, ***debug your NI devices, and identify the address of your NI devices.***

You can find more information about Ni-Max in https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGQwCAO&l=en-US.

**Follow the instructions in [https://www.ni.com/en-us/support/downloads/drivers/download.ni-max.html](https://www.ni.com/en-us/support/downloads/drivers/download.ni-max.html) to install Ni-Max.**

> Note added by Greg: If the above link is broken, you may search 'Ni Max download' in Google or in NI.com. The link should be easy to find.


## Step 8: Install NI-488.2 package

NI-488.2 is a package that helps you to communicate with NI devices through GPIB interface.
You can find more information about NI-488.2 in https://www.ni.com/en-us/support/downloads/drivers/download.ni-488-2.html.

**Follow the instructions in [https://www.ni.com/en-us/support/downloads/drivers/download.ni-488-2.html](https://www.ni.com/en-us/support/downloads/drivers/download.ni-488-2.html) to install NI-488.2.**


## Step 9: Install Instek GPP driver

Instek GPP driver is a driver that helps you to communicate with Instek GPP devices. In our case especially Instek GPD-4303S and GPP-1326. They are power supply for RF oscillator and RF amplifier, respectively. 

GPD-4303S is a four channel DC power supply, which is used to provide power for RF oscillator, and provide DC bias for RF attenuator on optical intensity modulator.

GPP-1326 is a one channel high power (operating at ~120W) DC power supply, which is used to provide power for RF amplifier.

You can find more information about Instek GPP driver in https://www.gwinstek.com/en-IN/products/detail/GPP-Series.

**Download the driver from [https://www.gwinstek.com/en-IN/products/downloadSeriesDownNew/14684/1747](https://www.gwinstek.com/en-IN/products/downloadSeriesDownNew/14684/1747).** (In case the above link fails, you may go to [https://www.gwinstek.com/en-IN/products/detail/GPP-Series](https://www.gwinstek.com/en-IN/products/detail/GPP-Series) and click "Download" on the right side of the page. Find 'USB driver' there and click "Download".)

**Install the downloaded GPP package following default instructions.**



## Step End-1: Verify installations

[TODO: add more information about how to verify the installations]


