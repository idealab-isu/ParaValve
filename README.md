# ParaValve

## A framework for simulating bioprosthetic heart valves in patient-specific geometries

Simulate blood flow, arterial wall deformation, and valve deformation of immersed bio-prosthetic heart valves using FEniCS and custom libraries for fluid-structure interaction (FSI) simulations

This repository presents an **open-source framework** for the simulation of bioprosthetic heart valves (BHV) in patient-specific aortic geometries using fluid-structure interaction (FSI) analysis. The framework leverages the [FEniCS](https://fenicsproject.org/) project and is built upon [immersogeometric analysis (IMGA)](https://doi.org/10.1007/s00366-022-01754-y), which combines isogeometric analysis (IGA) with immersed boundary methods. This approach is particularly suited for problems with complex geometries. The framework integrates parametric geometry modeling, meshing, FSI simulation, and post-processing. It is designed to be modular and expandable, supporting iterative optimization of valve designs.

---

## Overview of the Pipeline

The ParaValve framework provides a pipeline for simulating heart valve function within the aorta, starting from geometric modeling and concluding with visualization of simulation results. The key steps include:

1. **Geometric Modeling:** Creating parametric designs of the bioprosthetic heart valve and template-based aortic geometries with Non-uniform rational B-splines (NURBS). The framework can adapt template geometries to patient-specific data. (TODO: Adding the NURBSDiff script to match the template geometry of the aorta to the patient-specific data.)
2. **Meshing:** The aorta geometry is meshed for finite element analysis using external tools like [**Gmsh**](https://gmsh.info/). The resulting mesh files are then converted to formats compatible with FEniCS (e.g., XDMF) using utilities like **ChaMeleon** (part of the VarMINT library) or [meshio](https://github.com/nschloe/meshio).
3. **Simulation:** Performing the coupled fluid-structure interaction simulation using FEniCS and a suite of custom libraries. The framework can simulate blood flow (fluid domain), aortic wall deformation (solid domain), and valve leaflet deformation (shell domain), including contact between leaflets. It uses techniques like Immersogeometric Analysis (IMGA) for coupling the valve with the surrounding blood flow and handles deforming domains for the artery wall. The script supports parallel execution using MPI, which is recommended for realistic 3D simulations.

4. **Post-processing and Visualization:** This is typically done using the open-source visualization tool [ParaView](https://www.paraview.org/).

---

## How to install (user)

1. **Using Docker (Recommended for most users):** This method provides a containerized environment with all dependencies pre-installed. See the [Docker Installation Guide](Docker_Installation.md) for detailed instructions.
2. **Using Conda (For users familiar with Conda environments):** This method involves setting up a Conda environment from the provided `environment.yml` file. See the [Conda Environment Setup Guide](Conda_Installation.md) for detailed instructions.

---

TODO: How to install (developer)

---

## License

[![CC BY-NC 4.0][cc-by-nc-shield]][cc-by-nc]

This work is licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License][cc-by-nc].

[cc-by-nc]: http://creativecommons.org/licenses/by-nc/4.0/
[cc-by-nc-shield]: https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg
