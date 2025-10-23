import numpy as np
from scipy.signal import convolve2d
from PIL import Image
import matplotlib.pyplot as plt
from optiland.psf import FFTPSF
import optiland.backend as be
from scipy.signal import fftconvolve

class createImage():
    def __init__(self, system, opticalGeometry):
        self.system = system
        self.opticalGeometry = opticalGeometry
        self.psf_dict = {}
        self.arraySize = int(be.sqrt(len(system.fields.fields)))
        self.fieldFactor = 2 # full field 2 for half
        self.maxField = opticalGeometry.maxField / 1 # smaller for bigger



    def closest_field_psf(self, x_tile, y_tile, psf_keys):
        maxField = self.maxField 
        field_angles = self.opticalGeometry.field_angles
        # Map tile indices 0,1,2 to field angles [-1,0,1]
        field_angle_x = (field_angles[x_tile] / maxField) / self.fieldFactor
        field_angle_y = (field_angles[y_tile] / maxField) / self.fieldFactor

        # Find closest field key in psf_keys (should be exact match in this setup)
        return self.psf_dict[(field_angle_x, field_angle_y)]



    def simulate(self):
        maxField = self.maxField
        system = self.system
        opticalGeometry = self.opticalGeometry

        # Load and normalize image as numpy array
        img = Image.open("airForce.jpg").convert("L")
        img_np = np.asarray(img, dtype=np.float32) / 255.0


        # Assuming system.fields has been set to 3x3 grid with angles in field_angles
        for field in system.fields.fields:
            normX = (field.x / maxField) / self.fieldFactor
            normY = (field.y / maxField) / self.fieldFactor
            # Compute PSF for each field - replace with correct call for your setup
            # Make sure to pass the correct field index or angle
            try:
                psf_obj = FFTPSF(system, field=(normX, normY), wavelength=0.587, strategy='centroid_sphere')
            except:
                pass
            # Convert PSF to numpy, assuming psf_obj returns backend tensor
            psf_np = be.to_numpy(psf_obj.psf)
            psf_np = psf_np / np.sum(psf_np)  # normalize PSF

            if np.isnan(psf_np).any():
                print(f"Warning: NaNs in PSF at field ({normX}, {normY}), skipping.")
                continue
            else:
                self.psf_dict[(normX, normY)] = psf_np

            #self.psf_dict[(normX, normY)] = psf_np

        # Image tile sizes for 5x5 grid
        tile_w = img_np.shape[1] // self.arraySize
        tile_h = img_np.shape[0] // self.arraySize

        blurred_img = np.zeros_like(img_np)

        for y_tile in range(self.arraySize):
            for x_tile in range(self.arraySize):
                x_start = x_tile * tile_w
                y_start = y_tile * tile_h

                tile = img_np[y_start:y_start + tile_h, x_start:x_start + tile_w]

                # Get closest PSF from dictionary
                psf = self.closest_field_psf(x_tile, y_tile, self.psf_dict)
                #psf = self.bilinear_interpolate_psf(
                #    x_tile, y_tile, self.psf_dict,
                #    self.opticalGeometry.field_angles,
                #    self.opticalGeometry.maxField,
                #    grid_size=self.arraySize
                #)


                # Convolve tile with PSF
                blurred_tile = fftconvolve(tile, psf, mode='same')

                blurred_img[y_start:y_start + tile_h, x_start:x_start + tile_w] = blurred_tile
        #print(str(self.psf_dict))
        # Plotting

        return(img_np, blurred_img)


    def bilinear_interpolate_psf(self, x_tile, y_tile, psf_dict, field_angles, max_field, grid_size=5):
        """
        Interpolate PSF at fractional tile position (x_tile, y_tile) using bilinear interpolation.

        Parameters:
            x_tile, y_tile : float
                Tile coordinates, can be fractional (e.g. 1.5 means halfway between tiles 1 and 2)
            psf_dict : dict
                Dictionary keyed by (normX, normY) with PSF numpy arrays
            field_angles : list or np.array
                List of field angles (same length as grid_size)
            max_field : float
                Max field normalization factor
            grid_size : int
                Number of tiles along each axis (e.g. 5 for 5x5)
        
        Returns:
            interpolated_psf : np.array
                The bilinearly interpolated PSF
        """

        # Normalize tile positions to field angle space (between min and max)
        # Clamp x_tile, y_tile to grid range [0, grid_size-1]
        x_tile = np.clip(x_tile, 0, grid_size - 1)
        y_tile = np.clip(y_tile, 0, grid_size - 1)

        # Integer indices surrounding point
        x0 = int(np.floor(x_tile))
        x1 = min(x0 + 1, grid_size - 1)
        y0 = int(np.floor(y_tile))
        y1 = min(y0 + 1, grid_size - 1)

        # Fractions for interpolation
        dx = x_tile - x0
        dy = y_tile - y0

        # Get normalized field coordinates for keys in psf_dict
        def norm_angle(idx):
            return (field_angles[idx] / max_field) / self.fieldFactor  # Your existing normalization

        # PSF keys for corners
        key00 = (norm_angle(x0), norm_angle(y0))
        key10 = (norm_angle(x1), norm_angle(y0))
        key01 = (norm_angle(x0), norm_angle(y1))
        key11 = (norm_angle(x1), norm_angle(y1))

        # Fetch PSFs, fallback to zeros if missing (to avoid crashes)
        psf00 = psf_dict.get(key00, None)
        psf10 = psf_dict.get(key10, None)
        psf01 = psf_dict.get(key01, None)
        psf11 = psf_dict.get(key11, None)

        # If any missing, replace with zeros of a valid PSF shape
        shape = None
        for psf in [psf00, psf10, psf01, psf11]:
            if psf is not None:
                shape = psf.shape
                break
        if shape is None:
            raise ValueError("No valid PSFs found for interpolation")

        zero_psf = np.zeros(shape)

        psf00 = psf00 if psf00 is not None else zero_psf
        psf10 = psf10 if psf10 is not None else zero_psf
        psf01 = psf01 if psf01 is not None else zero_psf
        psf11 = psf11 if psf11 is not None else zero_psf

        # Bilinear interpolation
        interp_top = (1 - dx) * psf00 + dx * psf10
        interp_bottom = (1 - dx) * psf01 + dx * psf11
        interpolated_psf = (1 - dy) * interp_top + dy * interp_bottom

        # Normalize PSF
        interpolated_psf /= np.sum(interpolated_psf)

        return interpolated_psf
