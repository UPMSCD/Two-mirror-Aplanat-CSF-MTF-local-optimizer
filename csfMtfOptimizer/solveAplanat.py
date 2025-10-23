import numpy as np

class aplanat:

    def __init__(self, l, f1):#input variables
        self.l = l
        self.f1 = f1
        self.r1 = f1 * 2

        #starting variables
        self.efl = -300
        self.ca = 50
        self.maxField = 0.9 #change these programmatically later
        self.f2 = 0
        self.r2 = 0
        self.d2 = 0
        self.co = 0
        self.m = 0
        self.bfl = 0
        self.ubfl = 0
        self.k1 = 0
        self.k2 = 0
        self.k = 0
        self.n = 0
        self.field = 0
        self.h = 0
        self.eflEye = 0
        self.eyepieceEfl = 0
        self.eyepieceFov = 0
        self.eyeNodalFromCornea = 0
        self.eyeNodalToRetina = 0
        self.eyeMilimetersPerDeg = 0
        self.diffraction_cutoff_frequency = 0
        self.wavelength = 0
        self.eyePupilDiameter = 0
        self.meritValue = 0
        self.bestSystem = None
        self.bestScore = 0
        self.stopFlag = False
        self.field_angles = [-0.9, -0.5, 0.0 , 0.5, 0.9]
        
        #starting aberration vars
        self.sphericalAberration = 0
        self.comaAberration = 0
        self.astigmatismAberration = 0
        self.medianCurvature = 0
        self.petzvalCurvature = 0
        self.sagittalCurvature = 0
        self.tangentialCurvature = 0
        self.accomodationRatio = 0




#start paraxial solve first    
    def solve_paraxial(self):
        
        efl = self.efl
        f1 = self.f1
        l = self.l
        ca = self.ca

        try:




            i = f1 - l

            f2 = ((i * efl) / (efl + f1))

            r1 = f1 * 2

            r2 = f2 * 2

            m = r2/(r2 - r1 + 2 * l)

            i1 = ((i * f2) / (i - f2))

            bfl = i1

            ubfl = bfl + l

            k = i / f1

            d2 = k * ca

            co = d2 / ca

            b = l + i1

            n = -b / f1



            k1 = ((-2*(1 + n)) / ((m - n) * m**2)) -1

            k2 = -( (m + 1) / (m - 1) )**2 + ( (k1 + 1) / (k * ( 1 - ( 1 / m))**3))


            #setting k1 and k2 to 0 to test optimization

            #geometry solved set class attributes to solved values
            #f1 set
            #efl set
            #l set
            #ca set
            self.f2 = f2
            self.r2 = r2
            self.bfl = bfl
            self.ubfl = ubfl
            self.d2 = d2
            self.co = k
            self.k = k
            self.m = m
            self.n = n
            self.k1 = k1
            self.k2 = k2

        except Exception as e:

            print(e)




#aberration solves
    def solve_spherical_aberrations(self):

        k1 = self.k1
        k2 = self.k2
        k = self.k
        m = self.m
        ca = self.ca
        f1 = self.f1

        numerator = (( k1 + 1 - k) * abs(( k2 + ( ( m + 1) / m -1)**2 )) * ( 1 - (1 / m))**3) * ca
        denomenator = 2048 * f1**3

        Ws = numerator / denomenator

        self.sphericalAberration = Ws


    def solve_coma_aberrations(self):

        k1 = self.k1
        m = self.m
        n = self.n
        efl = self.efl

        numerator1 = (( (k1 + 1) * (m - n) ) * m**2)
        numerator2 = ( 2 * ( 1 + n ))

        numerator = 1 + (numerator1 / numerator2)

        denomenator = ( 4 * efl**2 )

        Cs = numerator / denomenator

        self.comaAberration = Cs


    def solve_astigmatism_aberrations(self):

        k1 = self.k1
        m = self.m
        n = self.n
        efl = self.efl

        leftNumerator = ( m**2 + n)
        leftDenomenator = ( m * (1 + n ))

        rightNumerator = ( m * (k1 + 1) * (m - n)**2 )
        rightDenomenator = ( 4 * (1 + n)**2 )

        numerator = ( ( leftNumerator / leftDenomenator) - ( rightNumerator / rightDenomenator))

        denomenator = ( 2 * efl)

        As = numerator / denomenator

        self.astigmatismAberration = As


    def solve_median_field_curvature_aberrations(self):

        k1 = self.k1
        m = self.m
        n = self.n
        efl = self.efl

        numerator = ( 1 + n)

        leftDenomenator = ( m * (m - n))

        rightDenomenator1 = (2 / m**2)
        rightDenomenator2 = ( ( m + 1) / ( m * (m - n)))
        rightDenomenator3 = ( ((m - n) * (k1 + 1)) / ( 2 * (1 + n)))

        denomenator = leftDenomenator * (1 - rightDenomenator1 + rightDenomenator2 - rightDenomenator3)

        Rm = -(numerator / denomenator) * efl

        self.medianCurvature = Rm


    def solve_petzval_field_curvature_aberrations(self):

        n = self.n
        m = self.m
        efl = self.efl

        numerator = ( (1 + n) * efl)
        denomenator = ( m * ( m - n) - m - 1)

        Rp = -(numerator / denomenator)

        self.petzvalCurvature = Rp


    def solve_sagittal_field_curvature_aberrations(self):

        k1 = self.k1
        m = self.m
        n = self.n
        efl = self.efl

        numerator = (1 + n)
        denom_left = m * (m - n)
        term1 = (2 / m**2)
        term2 = ((m + 1) / (m * (m - n)))
        # No conic term
        denominator = denom_left * (1 - term1 + term2)
        Sc =  -(numerator / denominator) * efl

        self.sagittalCurvature = Sc
        

    def solve_tangential_field_curvature_aberrations(self):

        k1 = self.k1
        m = self.m
        n = self.n
        efl = self.efl

        numerator = (1 + n)
        denom_left = m * (m - n)
        term1 = (2 / m**2)
        term2 = ((m + 1) / (m * (m - n)))
        term3 = (((m - n) * (k1 + 1)) / (1 + n))  # Full conic term
        denominator = denom_left * (1 - term1 + term2 - term3)
        Tc = -(numerator / denominator) * efl

        self.tangentialCurvature = Tc

    def solve_image_height(self):
        field = self.field
        efl = self.efl

        fieldRadians = np.deg2rad(field)

        h = abs(efl) * np.tan(fieldRadians)
        self.h = h

    def solve_accomodation_ratio(self):
        accomodationDiopters = 1
        m_sys = self.efl / self.eflEye
        efl_sys = self.efl / m_sys
        field_curvature = self.medianCurvature
        h = self.h

        efl_m = efl_sys / 1000 #meters
        sag = field_curvature - np.sqrt((field_curvature**2 - h**2))

        accomodation_depth_mm = (efl_m**2 / (1 / accomodationDiopters)) * 1000 #milimeters

        ratio = abs(sag / accomodation_depth_mm)
        
        self.accomodationRatio = ratio


        #image shift in mm eye can accomodate
    

    def solve_efl(r1, r2, l):

        m = r2/(r2 - r1 + 2 * l)

        eflObj = (r1 * m) / 2

        return eflObj       



