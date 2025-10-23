import numpy as np



# graph the mirror surfaces quickly
def mirror_surface(R, D):
    x = np.linspace(-D/2, D/2, 500)
    z = R - np.sqrt(R**2 - x**2)
    z -= z.min()  # Shift so vertex is at z = 0
    if(R < 0):
        return x, -z
    else:
        return x, z


def plotMirrors(opticalGeometry, ax):

    ax.clear() #clear existing plot
    # === PRIMARY MIRROR ===
    x1, z1 = mirror_surface(opticalGeometry.r1, opticalGeometry.ca)
    z1 = z1  # Located at z = 0

    # === SECONDARY MIRROR ===
    x2, z2 = mirror_surface(opticalGeometry.r2, opticalGeometry.d2)
    z2 = z2 + opticalGeometry.l  # Shift to secondary location

    # === IMAGE PLANE (FOCAL SURFACE) ===
    x3, z3 = mirror_surface(opticalGeometry.medianCurvature, (opticalGeometry.h))
    z3 = z3 + opticalGeometry.l + opticalGeometry.bfl  # Shift to image plane location

    # Use ax.plot instead of plt.plot
    ax.plot(z1, x1)
    ax.plot(z2, x2)
    ax.plot(z3, x3)

    ax.axhline(0, color='gray', linestyle='--', linewidth=0.5)
    ax.set_aspect('equal')
    ax.set_xlabel('Optical Axis (mm)')
    ax.set_ylabel('Aperture Height (mm)')
    ax.set_title('2-Mirror Telescope Geometry with Curved Image Plane')
    ax.grid(True)
    ax.legend()


def plot_simple_rays(opticalGeometry, ax):
    """ Trace simple marginal rays through Gregorian telescope """

    # 1. Define entrance ray: from far left to edge of M1
    x0 = opticalGeometry.ca / 2  # marginal ray height
    z_m1 = 0                     # primary mirror at z = 0

    z_entry = (opticalGeometry.l * 1.1)  # Where the ray enters (arbitrary)
    ax.plot([z_entry, z_m1], [x0, x0], color='orange', linestyle='--', label='Incoming Ray')

    # 2. Reflect from M1 to intermediate focus (approx)
    z_focus = opticalGeometry.f1  # Approximate real focus before M2
    ax.plot([z_m1, z_focus], [x0, 0], color='red', linestyle='-', label='To Focus')

    # 3. Reflect from focus to edge of M2 (z = l, height = d2/2)
    z_m2 = opticalGeometry.l
    x_m2 = opticalGeometry.d2 / 2
    ax.plot([z_focus, z_m2], [0, x_m2], color='green', linestyle='-', label='To Secondary')

    # 4. Reflect from M2 to final image plane (on axis)
    z_img = opticalGeometry.l + opticalGeometry.bfl
    ax.plot([z_m2, z_img], [x_m2, 0], color='blue', linestyle='-', label='To Image')

    # Optional: opposite-side marginal ray for symmetry
    ax.plot([z_entry, z_m1], [-x0, -x0], color='orange', linestyle='--')
    ax.plot([z_m1, z_focus], [-x0, 0], color='red', linestyle='-')
    ax.plot([z_focus, z_m2], [0, -x_m2], color='green', linestyle='-')
    ax.plot([z_m2, z_img], [-x_m2, 0], color='blue', linestyle='-')


def plot_aberrations_bar(opticalGeometry, ax):
    ax.clear()
    
    labels = ['Ss', 'Cs', 'As']
    values = [
        opticalGeometry.sphericalAberration,
        opticalGeometry.comaAberration,
        opticalGeometry.astigmatismAberration
    ]
    ax.bar(labels, values, color=['purple', 'teal', 'orange'])
    ax.set_ylim(0, max(values) * 1.2 if max(values) > 0 else 0.1)
    ax.set_title('Aberrations')
    ax.set_xlabel('RMS')
    ax.grid(True, axis='x')



def plot_aberration_text(opticalGeometry, ax):
    ax.clear()
    ax.axis('off')

    text_str = (
        f"UBFL: {opticalGeometry.ubfl:.2f}    |    "
        f"CO: {opticalGeometry.co:.3f}    |    "
        f"Magnification: {opticalGeometry.m:.2f}    |    "
        f"Accomodation Ratio: {opticalGeometry.accomodationRatio:.2f}    |    "
        f"Median Field Curvature: {opticalGeometry.medianCurvature:.2f}"
    )

    ax.text(0, 0.1, text_str, fontsize=10, verticalalignment='center', horizontalalignment='left', transform=ax.transAxes)
