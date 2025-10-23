import visisipy
import optiland.backend as be

def createGeometry():
    #add eye
    visisipy.set_backend("optiland")
    # Initialize the default Navarro model
    default_navarro_geometry = visisipy.NavarroGeometry()

    return default_navarro_geometry

def createEyeModel(eyeModelGeometry, opticalGeometry):

    opticalEyeModel = visisipy.EyeModel(geometry=eyeModelGeometry)

    geometry = opticalEyeModel
    model = eyeModelGeometry
    retina_radius = model.retina.radius

    cardinal_points = visisipy.analysis.cardinal_points(geometry)

    second_nodal_point = cardinal_points.nodal_points.image + (model.lens_thickness + model.vitreous_thickness)    

    axial_length = model.axial_length
    nodalToRetina = axial_length - second_nodal_point

    mm_per_degree = be.tan(be.deg2rad(1)) * nodalToRetina

    opticalGeometry.eyeNodalFromCornea = second_nodal_point
    opticalGeometry.eyeNodalToRetina = nodalToRetina
    opticalGeometry.eyeMilimetersPerDeg = mm_per_degree

    return opticalEyeModel


def insert(system, opticalEyeModel):

    index = len(system.surface_group.surfaces) - 1

    # Build the model in OpticStudio
    #model.build()
    visisipy.optiland.models.OptilandEye(opticalEyeModel).build(optic=system, start_from_index=index)
    


    return(system)

