import unittest

from src.unit_conversion import convert_unit, \
    NG_PER_DL, \
    NMOL_PER_L, \
    NG_PER_ML, \
    PG_PER_ML, \
    G_PER_DL

    
class TestConversions(unittest.TestCase):

    def test_convert_T_from_ng_per_dL_to_nmol_per_L_case1(self):
        '''
        If the concentration of T is 288.42 ng/dL, this is
        equivalent to 10nMol/L
        '''
        orig_val = 288.42
        species = 'T'
        orig_unit = NG_PER_DL
        target_unit = NMOL_PER_L
        cf = convert_unit(species, orig_unit, target_unit)
        self.assertAlmostEqual(orig_val*cf, 10.0, places=3)

    def test_convert_T_from_ng_per_dL_to_nmol_per_L_case2(self):
        '''
        If the concentration of T is 3*288.42 ng/dL (865.26), this is
        equivalent to 30nMol/L
        '''
        orig_val = 865.26
        species = 'T'
        orig_unit = NG_PER_DL
        target_unit = NMOL_PER_L
        cf = convert_unit(species, orig_unit, target_unit)
        self.assertAlmostEqual(orig_val*cf, 30.0, places=3)

    def test_convert_T_from_ng_per_mL_to_ng_per_dL(self):
        '''
        If the concentration of T is 2 ng/mL, this is
        equivalent to 200ng/dL
        '''
        orig_val = 2
        species = 'T'
        orig_unit = NG_PER_ML
        target_unit = NG_PER_DL
        cf = convert_unit(species, orig_unit, target_unit)
        self.assertAlmostEqual(orig_val*cf, 200.0, places=3)

    def test_convert_T_from_ng_per_mL_to_pg_per_mL(self):
        '''
        If the concentration of T is 1 ng/mL, this is
        equivalent to 1000pg/mL
        '''
        orig_val = 1
        species = 'T'
        orig_unit = NG_PER_ML
        target_unit = PG_PER_ML
        cf = convert_unit(species, orig_unit, target_unit)
        self.assertAlmostEqual(orig_val*cf, 1000.0, places=3)

    def test_convert_T_from_nmol_per_L_to_ng_per_dL_case1(self):
        '''
        If the concentration of T is 20 nMol/L this is
        equivalent to 576.84 ng/dL
        '''
        orig_val = 20
        species = 'T'
        orig_unit = NMOL_PER_L
        target_unit = NG_PER_DL
        cf = convert_unit(species, orig_unit, target_unit)
        self.assertAlmostEqual(orig_val*cf, 576.84, places=3)

    def test_convert_T_from_nmol_per_L_to_nmol_per_L(self):
        '''
        If the concentration of T is 20 nMol/L this is
        equivalent to 20 nMol/L
        '''
        orig_val = 20
        species = 'T'
        orig_unit = NMOL_PER_L
        target_unit = NMOL_PER_L
        cf = convert_unit(species, orig_unit, target_unit)
        self.assertAlmostEqual(orig_val*cf, 20.0, places=3)

    def test_convert_T_from_nmol_per_L_to_pg_per_mL(self):
        '''
        if T is 10nMol/L, it should convert to 288.42*10=2884.2 pg/mL
        '''
        orig_val = 10
        species = 'T'
        orig_unit = NMOL_PER_L
        target_unit = PG_PER_ML
        cf = convert_unit(species, orig_unit, target_unit)
        self.assertAlmostEqual(orig_val*cf, 2884.2, places=3)

    def test_convert_T_from_pg_per_mL_to_nmol_per_L(self):
        '''
        if T is 2884.2 pg/mL, it should convert to 10nMol/L
        '''
        orig_val = 2884.2
        species = 'T'
        orig_unit = PG_PER_ML
        target_unit = NMOL_PER_L
        cf = convert_unit(species, orig_unit, target_unit)
        self.assertAlmostEqual(orig_val*cf, 10.0, places=3)

    def test_convert_Alb_from_g_per_dL_to_nmol_per_L_case1(self):
        '''
        If the concentration of Alb is 4.3g/dL nMol/L this is
        equivalent to 646616.54135 nMol/L
        '''
        orig_val = 4.3
        species = 'Alb'
        orig_unit = G_PER_DL
        target_unit = NMOL_PER_L
        cf = convert_unit(species, orig_unit, target_unit)
        self.assertAlmostEqual(orig_val*cf, 646616.541, places=3)