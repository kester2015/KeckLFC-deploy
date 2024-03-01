# KeckLFC
This is control package for Laser Frequency Comb in Keck Observatory

# Installation

The texts <mark> highlighted like this </mark> are **Action Points**. Please read them carefully.

This installation guide is written for Windows 11 platform. It should be similar (but untested) for other operating systems.


## Step 1: Install Anaconda and prepare the environment

Anaconda is a free and open-source distribution of the Python (and R) programming languages for scientific computing, that aims to simplify package management and deployment. Package versions are managed by the package management system conda. **Without Anaconda, the package installation can be complicated because of the dependencies of different packages, especially for Windows users when you have other python packages already installed for whatever other reasons.** It is **highly recommended** to use Anaconda to manage python packages.


### 1.1 Download and install Anaconda

<mark> 
Download and install Anaconda from https://www.anaconda.com/download/ 
</mark>


Verify the installation by running `conda --version` in terminal.

### 1.2 Create a new environment



Create a new environment for KeckLFC by running `conda create -n lfc` in terminal.

Activate the environment by running `conda activate lfc` in terminal.

- Step 2: Install required packages

-- 2.1 Install pyvisa

Run `conda install -c conda-forge pyvisa` in terminal.

-- 2.2 Install numpy, scipy, matplotlib

Run `conda install numpy scipy matplotlib` in terminal.

-- 2.3 Install mcculw (for USB-2408 DAQ)

Run `pip install mcculw` in terminal.

-- 2.4 Install wsapi (for Finisar WaveShaper)

Follow the instructions in https://ii-vi.com/use-64-bit-python-3-7-to-control-the-waveshaper-through-the-usb-port/ for connection guide






