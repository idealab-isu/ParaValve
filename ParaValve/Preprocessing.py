'''
 - This script is used to generate the interior facets of the arterial wall
   (the solid domain) and the stent-solid intersections.
 - This script should be ran on a single core.
 - To generate the aorta mesh, use GMSH (https://gmsh.info/) with the provided
   .geo file in the ``aorta`` directory. To convert the .msh file to a
   FEniCS-compatible XDMF format (.xdmf + .h5), use the ChaMeleon.py utility
   provided with VarMINT.
'''

###############################################################
#### Housekeeping and Imports #################################
###############################################################
from dolfin import *
import os
import sys
import datetime

# build command-line parser and parse arguments
import argparse
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

# general arguments
p = parser.add_argument_group("general")
p.add_argument("--no-use-tsfc",dest="USE_TSFC",
               default=True, action='store_false',
               help='Use UFLACS instead of TSFC for a form compiler.')
p.add_argument("--flags",dest='FLAGS',nargs="+",type=int,
               default=[0,1,2,3,4,5,6,7,8,9,10,11],
               help='Mesh marker flags within the code, in the following \
                    order: none, fluid, solid, interface, fluid_inflow, \
                    fluid_outflow, solid_inflow, solid_outflow, solid_outer, \
                    stent_intersection, leaflet, stent.')

# fluid-solid problem parameters
p = parser.add_argument_group("fluid-solid problem")
p.add_argument("--mesh-folder",dest="MESH_FOLDER",
               default="./aorta/",
               help="Folder that contains the fluid-solid mesh and markers.")
p.add_argument("--mesh-filename",dest="MESH_FILENAME",
               default="aorta_mesh.xdmf",
               help="Filename of the fluid-solid mesh.")
p.add_argument("--subdomains-filename",dest="SUBDOMAINS_FILENAME",
               default="aorta_subdomains.xdmf",
               help="Filename of the fluid-solid subdomains markers.")
p.add_argument("--boundaries-filename",dest="BOUNDARIES_FILENAME",
               default="aorta_boundaries.xdmf",
               help="Filename of the fluid-solid boundary markers.")
p.add_argument("--facets-filename",dest="SOLID_INTERIOR_FACETS_FILENAME",
               default="solid_interior_facets.xdmf",
               help="Filename of the fluid-solid boundary markers.")
p.add_argument("--markers-string",dest="MARKERS_STRING",
               default="markers",
               help="Mesh physical group marker string.")

# shell problem parameters
p = parser.add_argument_group("shell problem")
p.add_argument("--solid-stent-intersections-filename",
               dest="SOLID_STENT_INTERSECTIONS_FILENAME",
               default="aorta_solid-stent-intersections.xdmf",
               help="Filename of the fluid-solid boundary markers.")
p.add_argument("--valve-folder",dest="VALVE_FOLDER",
               default="./valves/",
               help='The folder that contains the valve smesh files.')
p.add_argument("--valve-smesh-prefix",dest="VALVE_SMESH_PREFIX",
               default="smesh.",
               help='The prefix for the valve smesh files.')
p.add_argument("--valve-smesh-suffix",dest="VALVE_SMESH_SUFFIX",
               default=".dat",
               help='The suffix for the valve smesh files.')
p.add_argument("--num-patches",dest="NUM_PATCHES",
               type=int,
               default=1,
               help='The number of valve patches to import.')
p.add_argument("--spline-quad-deg",dest="SPLINE_QUAD_DEG",
               type=int,
               default=3,
               help='The k-degree quadrature rule for the spline.')
p.add_argument("--r-self",dest="R_SELF",
               type=float,
               default=0.0308,
               help='The self-intersection radius for shell contact.')
p.add_argument("--r-max",dest="R_MAX",
               type=float,
               default=0.0237,
               help='The maximum radius for shell contact.')
p.add_argument("--k-contact",dest="K_CONTACT",
               type=float,
               default=1e11,
               help='The contact penalty parameter.')
p.add_argument("--s-contact",dest="S_CONTACT",
               type=float,
               default=0.2,
               help='The contact smoothing parameter in [0,1] for no \
                    smoothing to complete smoothing.')

# make list of the input arguments for logging
args = parser.parse_args()
script_parameters_message = ''
for s in sys.argv:
    if s[0]=="-":     # a cheap check to find the arguments
        script_parameters_message += "\n"
    script_parameters_message += s
    script_parameters_message += " "

# parse arguments
USE_TSFC = args.USE_TSFC
LABELS = ("none", "fluid", "solid", "interface", "fluid_inflow", 
          "fluid_outflow", "solid_inflow", "solid_outflow", "solid_outer",
          "stent_intersection", "leaflet", "stent")
FLAG = {}
for i,label in enumerate(LABELS):
    FLAG[label] = args.FLAGS[i]

FILEPATH_IN_MESH = args.MESH_FOLDER + args.MESH_FILENAME
FILEPATH_IN_SUBDOMAINS = args.MESH_FOLDER + args.SUBDOMAINS_FILENAME
FILEPATH_IN_BOUNDARIES = args.MESH_FOLDER + args.BOUNDARIES_FILENAME
FILEPATH_IN_SOLID_INTERIOR_FACETS = args.MESH_FOLDER + args.SOLID_INTERIOR_FACETS_FILENAME
MARKER = args.MARKERS_STRING

FILEPATH_SHELL_INTERSECTIONS = args.MESH_FOLDER + \
                               args.SOLID_STENT_INTERSECTIONS_FILENAME
FILEPATH_IN_SHELL_PREFIX = args.VALVE_FOLDER + args.VALVE_SMESH_PREFIX
FILEPATH_IN_SHELL_SUFFIX = args.VALVE_SMESH_SUFFIX
NUM_PATCHES = args.NUM_PATCHES

SPLINE_QUAD_DEG = args.SPLINE_QUAD_DEG
CONTACT = {'R_SELF': args.R_SELF, 
           'R_MAX': args.R_MAX, 
           'K': args.K_CONTACT,
           'S': args.S_CONTACT}


# imports
from tIGAr.BSplines import *            # splines
from tIGAr.timeIntegration import *     # time integration
from ShNAPr.SVK import *                # shells
from ShNAPr.contact import *            # shell contact
from ShNAPr.kinematics import *         # shell kinematics
from ShNAPr.hyperelastic import *       # hyperelastic shell materials

# define MPI communicators
comm = MPI.comm_world
rank = comm.Get_rank()
size = comm.Get_size()

# logging active on master processor only
from CouDALFISh import log
set_log_active(False)
if (rank==0):
    set_log_active(True)

if size != 1:
    log("This program must run on a single core.")
    exit(1)

# put out a title for the script log
log(80*"=")
log("  Heart Valve Simulation Preprocessing")
log(80*"=")

# display basic information in log
log("Current time: " + str(datetime.datetime.now()))
log("Script invoked with the following command-line arguments:")
log(script_parameters_message)
log("")
log(80*"=")
log("Parameters used in this script:")
log(80*"=")
for arg, value in vars(args).items():
   log((str(arg) + " = " + str(value)))
log(80*"=")

# set up global timer
global_timer = Timer("Global Elapsed Time")
global_timer.start()

# use TSFC form compiler representation
if USE_TSFC:
    parameters['form_compiler']['representation'] = 'tsfc'
    sys.setrecursionlimit(10000)


###############################################################
#### Import aorta mesh ########################################
###############################################################

# import mesh
log("Importing mesh.")
mesh = Mesh()
with Timer("HV 00: import mesh"):
    with XDMFFile(comm, FILEPATH_IN_MESH) as f:
        f.read(mesh)

# Mesh-derived quantities:
nsd = mesh.geometry().dim()

# import subdomains
log("Importing subdomains.")
mvc = MeshValueCollection('size_t', mesh, nsd)
with Timer("HV 01: import subdomains"):
    with XDMFFile(comm, FILEPATH_IN_SUBDOMAINS) as f:
        f.read(mvc, MARKER)
subdomains = cpp.mesh.MeshFunctionSizet(mesh, mvc)

# import boundaries
log("Importing boundaries.")
mvc = MeshValueCollection('size_t', mesh, nsd-1)
with Timer("HV 02: import boundaries"):
    with XDMFFile(comm, FILEPATH_IN_BOUNDARIES) as f:
        f.read(mvc, MARKER)
boundaries = cpp.mesh.MeshFunctionSizet(mesh, mvc)

# initialize mesh connectivities
log("Building mesh connectivities.")
with Timer("HV 03: build mesh connectivities"):
    mesh.init(nsd, nsd-1)
    mesh.init(nsd-3, nsd-1)

# initialize and fill a facet function for the solid region, leaving off 
# anything touching the interface facets (Run on one core)
log("Building solid-region interior MeshFunction.")
solid_interior_facets = MeshFunction("size_t", mesh, nsd-1)
solid_interior_facets.set_all(FLAG['none'])
with Timer("HV 04: build interior solid markers"):
    for cell in cells(mesh):
        if (subdomains[cell]==FLAG["solid"]):
            for facet in facets(cell):
                solid_interior_facets[facet] = FLAG["solid"]
    for cell in cells(mesh):
        if (subdomains[cell]==FLAG["solid"]):
            for facet in facets(cell):
                if (boundaries[facet]==FLAG["interface"]):
                    for vertex in vertices(facet):
                        for facet in facets(vertex):
                            solid_interior_facets[facet] = FLAG["none"]

log("Saving solid_interior_facets to file.")
with Timer("HV 05: saving solid_interior_facets to file"):
    solid_interior_facets.rename(MARKER,MARKER)
    XDMFFile(comm,FILEPATH_IN_SOLID_INTERIOR_FACETS).write(solid_interior_facets)


###############################################################
#### Import valve geometry ####################################
###############################################################

if not os.path.isfile(FILEPATH_IN_SHELL_PREFIX+"1"+FILEPATH_IN_SHELL_SUFFIX):
    error("Missing data files for valve geometry.")

# Load a control mesh from several files in a legacy ASCII format.
log("Importing smesh files as control mesh.")
controlMesh = LegacyMultipatchControlMesh(FILEPATH_IN_SHELL_PREFIX,
                                          NUM_PATCHES,
                                          FILEPATH_IN_SHELL_SUFFIX)

# Every processor has a full copy of the shell structure, on its
# MPI_SELF communicator.
log("Creating spline generator from control mesh.")
with Timer("HV 06: create spline generator"):
    splineGenerator = EqualOrderSpline(selfcomm,nsd,controlMesh)

# Generate the extracted representation of the spline.
log("Generating extracted spline.")
spline = ExtractedSpline(splineGenerator,SPLINE_QUAD_DEG)

# Define contact context:
log("Specify shell self-contact rules.")

def phiPrime(r):
    if (r>CONTACT["R_MAX"]):
        return 0.0
    elif (r>(1-CONTACT['S'])*CONTACT["R_MAX"]):
        return -CONTACT['K']/(2*CONTACT["R_MAX"]*CONTACT['S'])*\
               (CONTACT["R_MAX"]-r)**2
    else:
        return -CONTACT['K']*(CONTACT["R_MAX"]*(1-CONTACT['S']/2)-r)
def phiDoublePrime(r):
    if (r>CONTACT["R_MAX"]):
        return 0.0
    elif (r>(1-CONTACT['S'])*CONTACT["R_MAX"]):
        return CONTACT['K']/(CONTACT["R_MAX"]*CONTACT['S'])*\
               (CONTACT["R_MAX"]-r)
    else:
        return CONTACT['K']

contactContext_sh = ShellContactContext(spline,CONTACT["R_SELF"],
                                        CONTACT["R_MAX"],
                                        phiPrime,phiDoublePrime)


###############################################################
#### Compute stent-solid intersections ########################
###############################################################

log("Computing intersection between stent and the arterial wall.")

# initiate bounding box tree for background mesh
log("  Generating bounding box tree for background mesh.")
bbt = mesh.bounding_box_tree()

# fetch dof coordinates on shell from contact context
points_list = contactContext_sh.nodeXs

# initiate intersection markers on cells
intersections = MeshFunction('bool',mesh,nsd)
intersections.set_all(False)

# compute cell intersections
log("  Computing collisions between fluid-solid mesh and shell.")
for pts in points_list:
    for i in range(np.size(pts,axis=0)):
        p = Point(pts[i,:])
        collisions = bbt.compute_entity_collisions(p)
        intersections_arr = intersections.array()
        for cell in collisions:
            intersections_arr[cell] = True

# transfer cell intersections to a facet function
# applies marker to only the solid-stent intersections
log("  Computing intersected facets of solid cells.")
stent_intersection = MeshFunction('size_t',mesh,nsd-1)
stent_intersection.set_all(FLAG["none"])
for cell in cells(mesh):
    if (intersections[cell] is True) and \
        (subdomains[cell]==FLAG["solid"]):
        for facet in facets(cell):
            stent_intersection[facet] = FLAG["stent_intersection"]

# write to filesystem
log("  Saving solid-stent intersections to file.")
stent_intersection.rename(MARKER,MARKER)
XDMFFile(comm,FILEPATH_SHELL_INTERSECTIONS).write(stent_intersection)


###############################################################
#### Display Timings for Imports ##############################
###############################################################
log("\nTimings:")
list_timings(TimingClear.clear,[TimingType.wall])
log("")
log("Global time elapsed: " + str(global_timer.elapsed()[0]))
