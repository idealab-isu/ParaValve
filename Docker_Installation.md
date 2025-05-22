# Docker Installation Guide

Documented by: Mehdi Saraeian (<mehdi@iastate.edu>)

This documentation is mainly aimed at Windows users with an attempt to cover MacOS users.

---

## Prerequisites

- **Git**: Ensure you have Git installed on your host system. While Git is often pre-installed in Linux/MacOS environments and FEniCS Docker images, having it on your host allows you to manage the code outside the container if needed. You can download Git from [https://git-scm.com/downloads](https://git-scm.com/downloads).
- **Host Directory for Sharing**: Before running step 4, it's recommended to create the directory `C:\shared_FEniCS_ParaValve` on your Windows computer. For MacOS/Linux users, you would create a similar directory, for example, `/Users/yourusername/shared_FEniCS_ParaValve` (adjust `yourusername` accordingly), and you'll need to use this path in the `docker run` command in step 4. This directory will be used to share files between your computer and the Docker container.

---

## Installation steps

1) Download & install docker on your local computer: <https://www.docker.com/products/docker-desktop>
**Note:** The installation process is going to ask you to restart your computer.

2) Once Docker is installed and the docker application is running, open Windows PowerShell(Windows)/Terminal(MacOS) in the directory where you have the provided Dockerfile.
**Note:** This is important because the `docker build` command in the next step looks for the `Dockerfile` in your current directory.

3) Run the following command: `docker build -t ParaValve .`
**Note:** This command builds a Docker image from the `Dockerfile`. The `-t ParaValve` part tags (or names) your image as `ParaValve` for easier reference later. This step may take several minutes to complete.

4) Run the following command: `docker run --shm-size=256m --name FEniCS_ParaValve -p 127.0.0.1:8000:8000 -v "C:\shared_FEniCS_ParaValve:/home/fenics/shared" -ti ParaValve`
**Note:** This command starts and runs a Docker container from the `ParaValve` image you built in the previous step.
Here's a breakdown of what each part of the command does:
   - `--shm-size=256m`: Allocates 256 megabytes of shared memory to the container.
   - `--name FEniCS_ParaValve`: Assigns a specific name (`FEniCS_ParaValve`) to your running container.
   - `-p 127.0.0.1:8000:8000`: This maps a port from your host computer to a port inside the container.
   - `-v "C:\shared_FEniCS_ParaValve:/home/fenics/shared"`: This creates a "volume" that links a directory on your host computer to a directory inside the container.
   - `"C:\shared_FEniCS_ParaValve"` is the path on your Windows host machine.
   - `"/home/fenics/shared"` is the path inside the Docker container.
   - This allows files created or modified in `/home/fenics/shared` inside the container to be accessible at `C:\shared_FEniCS_ParaValve` on your host, and vice-versa. It's very useful for getting simulation results out of the container or providing input files to it.
   - **Important**: Ensure the host directory (e.g., `C:\shared_FEniCS_ParaValve`) exists on your computer *before* running this command (see Prerequisites section).
   - **MacOS/Linux users**: You'll need to change the host path. For example: `-v "/Users/yourusername/shared_FEniCS_ParaValve:/home/fenics/shared"`.
   - `-ti ParaValve`:
     - `-t`: Allocates a pseudo-TTY (a virtual terminal).
     - `-i`: Keeps STDIN (standard input) open, making the session interactive.
     - Together, `-ti` allows you to interact with the container's command-line shell.
     - `ParaValve`: Specifies the name of the Docker image to run.
      After this command executes successfully, your terminal prompt will likely change, indicating you are now "inside" the container's environment.

5) Inside your container, change your directory to `cd ~/fenics` and clone the ParaValve repository by running the following command: `git clone https://github.com/idealab-isu/ParaValve.git`.
**Note:** The `git clone` command downloads a copy of the ParaValve project's source code and files from its GitHub repository. The files will be placed into a new directory named `ParaValve` inside your current directory within the container (which should be `/home/fenics`).

6) To run the simulation on `x` cores, you can use the following command: `mpirun -n 'x' python3 ParaValve.py`

7) To exit the container you can simply type `exit`

8) To start the container again use the following command: `docker start -i FEniCS_ParaValve`

---

You can find more information here:
Docker: <https://docs.docker.com/get-started/>
Docker & FEniCS: <https://fenics.readthedocs.io/projects/containers/en/latest/index.html>
Questions: <mehdi@iastate.edu>
