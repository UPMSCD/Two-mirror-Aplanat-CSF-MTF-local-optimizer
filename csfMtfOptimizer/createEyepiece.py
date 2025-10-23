from optiland import optic, optimization, surfaces
import optiland.backend as be
from optiland.fileio import zemax_handler



def rke(system, opticalGeometry):
    ##init #does rough alignment to best focus

    eyepieceGeometry2 = zemax_handler.load_zemax_file('rke12mm.ZMX')
    system = system.__add__(eyepieceGeometry2)

    opticalGeometry.eyepieceEfl = 12
    opticalGeometry.eyepieceFov = 45
    system.info()
    return(system)


def optimizeAfterEye_spotField(system, surfaceIndex1, surfaceIndex2):
    problem = optimization.OptimizationProblem()

    #define operand and system
    for field in system.fields.get_field_coords():
        input_data = {
            "optic": system,
            "surface_number": -1,#-1 might be why the code is fucked
            "Hx": field[0],
            "Hy": field[1],
            "num_rays": 3,
            "wavelength": 0.587,
            "distribution": "hexapolar",
        }
        problem.add_operand(
            operand_type="rms_spot_size",
            target=0,
            weight=1,
            input_data=input_data,
        )

    #define variables
    problem.add_variable(system, "thickness", surface_number=surfaceIndex1)
    problem.add_variable(system, "thickness", surface_number=surfaceIndex2)
     #set bfl from secondary to find eyepiece placement
    problem.info()
    optimizer = optimization.OptimizerGeneric(problem)
    optimizer.optimize()
    problem.info()
    problem.update_optics()

    return(system)


def optimizeAfterEye_wfe(system, surfaceIndex1, surfaceIndex2):
    problem = optimization.OptimizationProblem()

    #define operand and system
    for wave in system.wavelengths.get_wavelengths():
        input_data = {
            "optic": system,
            "Hx": 0,
            "Hy": 0,
            "num_rays": 3,
            "wavelength": wave,
            "distribution": "gaussian_quad",
        }

        # add RMS spot size operand
        problem.add_operand(
            operand_type="OPD_difference",
            target=0,
            weight=1,
            input_data=input_data,
        )

    #define variables
    problem.add_variable(system, "thickness", surface_number=surfaceIndex1)
    problem.add_variable(system, "thickness", surface_number=surfaceIndex2)

     #set bfl from secondary to find eyepiece placement
    problem.info()
    optimizer = optimization.OptimizerGeneric(problem)
    optimizer.optimize()
    problem.info()
    problem.update_optics()

    return(system)


def optimizeAfterEye_wfeField(system, surfaceIndex1, surfaceIndex2):
    problem = optimization.OptimizationProblem()

    #define operand and system
    for field in system.fields.get_field_coords():
        input_data = {
            "optic": system,
            "Hx": field[0],
            "Hy": field[1],
            "num_rays": 3,
            "wavelength": 0.587,
            "distribution": "gaussian_quad",
        }
        problem.add_operand(
            operand_type="OPD_difference",
            target=0,
            weight=1,
            input_data=input_data,
        )
    #define variables
    problem.add_variable(system, "thickness", surface_number=surfaceIndex1)
    problem.add_variable(system, "thickness", surface_number=surfaceIndex2)
    problem.add_variable(system, "conic", surface_number=2, min_val=-6, max_val=0)
    problem.add_variable(system, "conic", surface_number=1, min_val=-6, max_val=0)

     #set bfl from secondary to find eyepiece placement
    problem.info()
    optimizer = optimization.OptimizerGeneric(problem)
    optimizer.optimize()
    problem.info()
    problem.update_optics()

    return(system)


def optimizeAfterEye_wfeFieldSystem(system, surfaceIndex1, surfaceIndex2):
    problem = optimization.OptimizationProblem()

    #define operand and system
    for field in system.fields.get_field_coords():
        input_data = {
            "optic": system,
            "Hx": field[0],
            "Hy": field[1],
            "num_rays": 3,
            "wavelength": 0.587,
            "distribution": "gaussian_quad",
        }
        problem.add_operand(
            operand_type="OPD_difference",
            target=0,
            weight=1,
            input_data=input_data,
        )
    #define variables
    #problem.add_variable(system, "thickness", surface_number=surfaceIndex1)
    #problem.add_variable(system, "thickness", surface_number=surfaceIndex2)


    r1 = (system.surface_group.surfaces[1].geometry.radius)
    r2 = (system.surface_group.surfaces[2].geometry.radius)

    problem.add_variable(system, "radius", surface_number=1, min_val=(r1 - 2), max_val=(r1 + 2))
    problem.add_variable(system, "thickness", surface_number=1, min_val=-150, max_val=30)
    problem.add_variable(system, "conic", surface_number=1, min_val=-6, max_val=0)


    problem.add_variable(system, "radius", surface_number=2, min_val=(r2 - 2), max_val=(r2 + 2))
    problem.add_variable(system, "thickness", surface_number=2, min_val=30, max_val=150)
    problem.add_variable(system, "conic", surface_number=2, min_val=-6, max_val=0)


    problem.add_variable(system, "thickness", surface_number=8, min_val=1, max_val=20)


   # print(problem.sum_squared())
     #set bfl from secondary to find eyepiece placement
    problem.info()
    optimizer = optimization.OptimizerGeneric(problem)
    optimizer.optimize()
    problem.info()
    problem.update_optics()

    return(system)