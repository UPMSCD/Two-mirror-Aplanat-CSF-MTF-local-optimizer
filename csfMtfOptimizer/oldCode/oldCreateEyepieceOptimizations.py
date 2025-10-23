
def rke(system):
    ##init #does rough alignment to best focus

    eyepieceGeometry = zemax_handler.load_zemax_file('rke12mm.ZMX')
    eyepieceGeometry.flip()
    eyepieceGeometry.add_surface(index=(9))#new image plane

    eyepieceGeometry.set_aperture(aperture_type="EPD", value=13.02)

    #field
    eyepieceGeometry.set_field_type(field_type="angle")
    eyepieceGeometry.add_field(y=0)
    eyepieceGeometry.add_field(y=0.3)
    eyepieceGeometry.add_field(y=0.7)


    #wavelngth
    eyepieceGeometry.add_wavelength(value=0.587, is_primary=True)
    eyepieceGeometry.info()
    ###



    imageOffset = optimizePlacement_wfe(eyepieceGeometry, 8)#8 should now be air
    #reload original geometry now after getting offset
    #eyepieceGeometry.draw(num_rays=4)
    eyepieceGeometry.flip()
    #eyepieceGeometry = zemax_handler.load_zemax_file('rke12mm.ZMX')
    #add calculated paraxial offset to bfl from secondary
    eyepieceGeometry.set_thickness(surface_number=1, value = (imageOffset))
    eyepieceGeometry.set_thickness(surface_number=8, value = (0))
    eyepieceGeometry.info()



def optimizePlacement(system, surfaceIndex):
    problem = optimization.OptimizationProblem()

    #define operand and system
    for wave in system.wavelengths.get_wavelengths():
        input_data = {
            "optic": system,
            "surface_number": -1,#-1 might be why the code is fucked
            "Hx": 0,
            "Hy": 0,
            "num_rays": 3,
            "wavelength": wave,
            "distribution": "hexapolar",
        }

        # add RMS spot size operand
        problem.add_operand(
            operand_type="rms_spot_size",
            target=0,
            weight=1,
            input_data=input_data,
        )

    #define variables
    problem.add_variable(system, "thickness", surface_number=surfaceIndex) #set bfl from secondary to find eyepiece placement
    problem.info()
    optimizer = optimization.OptimizerGeneric(problem)
    optimizer.optimize()
    problem.info()
    problem.update_optics()
    return (system.surface_group.surfaces[surfaceIndex].thickness)


def optimizePlacement_wfe(system, surfaceIndex):
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
    problem.add_variable(system, "thickness", surface_number=surfaceIndex) #set bfl from secondary to find eyepiece placement
    problem.info()
    optimizer = optimization.OptimizerGeneric(problem)
    optimizer.optimize()
    problem.info()
    #problem.update_optics()
    return (system.surface_group.surfaces[surfaceIndex].thickness)


def optimizeExitPupil_wfe(system, surfaceIndex):
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
    problem.add_variable(system, "thickness", surface_number=surfaceIndex) #set bfl from secondary to find eyepiece placement
    problem.info()
    optimizer = optimization.OptimizerGeneric(problem)
    optimizer.optimize()
    problem.info()
    problem.update_optics()
    return (system.surface_group.surfaces[surfaceIndex].thickness)
