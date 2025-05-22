# Conda Environment Setup Guide

Documented by: Mehdi Saraeian (<mehdi@iastate.edu>)

Follow the instructions below to set up your Conda environment using the provided `environment.yml` file.

> **Note for Windows users:**  
> You must use Windows Subsystem for Linux (WSL) to create and use this Conda environment on Windows.
> This is because the environment contains Linux-specific packages that are not available on native Windows.
> You cannot use this `environment.yml` file directly in Windows Command Prompt or PowerShell.

---

## Prerequisites

- **Conda Installed:**  
  You need Conda installed on your computer.  
  - **Linux/macOS:** Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution).
  - **Windows:** Install Conda inside your WSL environment.
- **GitHub Repository:**  
  Make sure you have cloned or downloaded this repository to your local machine.

---

## Step-by-Step Instructions

### **1. Open a Terminal**

- **Linux/macOS:** Open your Terminal.
- **Windows:**  
  - Install [WSL and a Linux distribution (e.g., Ubuntu)](https://learn.microsoft.com/en-us/windows/wsl/install) if you have not already done so.
  - Open your WSL terminal.

### **2. Navigate to the Project Directory**

Use the `cd` command to move into the folder where the `environment.yml` file is located:

```bash
cd path/to/your/repository
```

### **3. Create the Conda Environment**

Run the following command to create a new Conda environment using the `environment.yml` file:

```bash
conda env create -f environment.yml
```

This will automatically create an environment with the name specified in `environment.yml` and install all required dependencies.

### **4. Activate the Environment**

Once the environment is created, activate it using:

```bash
conda activate ParaValve
```

Replace with the actual name of the environment you created (the default as defined in the `environment.yml` file is `ParaValve`).

You can list all environments with:

```bash
conda env list
```

### **5. Verify the Environment**

Check that the environment is active and contains the correct packages by running:

```bash
conda list
```

---

## Additional Notes

- You must install Conda inside WSL, not on Windows itself, for this environment to work properly.
- For a smoother experience, consider using Visual Studio Code with the [WSL extension](https://code.visualstudio.com/docs/remote/wsl) to develop directly from your WSL environment.
