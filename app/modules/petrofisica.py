# ==========================================================
# MÓDULO: PETROFÍSICA
# ==========================================================
import numpy as np
import pandas as pd
from scipy.ndimage import median_filter
import warnings
warnings.filterwarnings('ignore')


class PetroConfig:
    """Parámetros petrofísicos configurables"""
    
    RHO_MATRIX = {
        'ARENISCA': 2.65,
        'LUTITA': 2.70,
        'CALIZA': 2.71,
        'DOLOMITA': 2.87,
        'ANHIDRITA': 2.98,
        'SAL': 2.03
    }
    
    RHO_FLUID = 1.0
    RHO_HC = 0.7
    
    ARCHIE_PARAMS = {
        'ARENISCA': {'A': 1.0, 'M': 2.0, 'N': 2.0},
        'ARENISCA_CONSOLIDADA': {'A': 0.62, 'M': 2.15, 'N': 2.0},
        'CALIZA': {'A': 1.0, 'M': 2.0, 'N': 2.0},
        'DOLOMITA': {'A': 1.0, 'M': 2.0, 'N': 2.0},
        'CARBONATO_VUGULAR': {'A': 1.0, 'M': 1.8, 'N': 2.0},
    }
    
    A = 1.0
    M = 2.0
    N = 2.0
    RW = 0.05
    
    DOMINANT_MATRIX = 'ARENISCA'
    DOMINANT_RHO = 2.65
    
    PHI_CUTOFF = 0.06
    VSH_CUTOFF = 0.50
    SW_CUTOFF = 0.70


LITHO_COLORS = {
    'ARENISCA': '#FFE17F',
    'ARENISCA_ARCILLOSA': '#D4AC0D',
    'LUTITA': '#808080',
    'CALIZA': '#87CEEB',
    'CARBONATO': '#87CEEB',
    'DOLOMITA': '#FFB6C1',
    'CONGLOMERADO': '#CD853F',
}


class PetroPhysics:
    """Cálculos petrofísicos"""
    
    @staticmethod
    def calc_vsh_larionov(gr, gr_min, gr_max):
        """Calcula VSH con método Larionov"""
        if pd.isna(gr):
            return np.nan
        igr = np.clip((gr - gr_min) / (gr_max - gr_min), 0, 1)
        vsh = 0.083 * (2**(3.7 * igr) - 1)
        return np.clip(vsh, 0, 1)
    
    @staticmethod
    def calc_porosity_density(rhob, rho_ma, rho_fl, vsh=0, rho_sh=2.7):
        """Calcula porosidad de densidad"""
        if pd.isna(rhob):
            return np.nan
        if pd.isna(vsh):
            vsh = 0
        
        phi_d = (rho_ma - rhob) / (rho_ma - rho_fl)
        if vsh > 0:
            phi_sh = (rho_ma - rho_sh) / (rho_ma - rho_fl)
            phi_d = phi_d - vsh * phi_sh
        return np.clip(phi_d, 0, 0.45)
    
    @staticmethod
    def calc_porosity_neutron_density(nphi, rhob, rho_ma, rho_fl, vsh=0):
        """Calcula porosidad neutron-densidad"""
        if pd.isna(nphi) or pd.isna(rhob):
            return np.nan
        if pd.isna(vsh):
            vsh = 0
            
        phi_d = PetroPhysics.calc_porosity_density(rhob, rho_ma, rho_fl, vsh)
        phi_n = nphi
        phi_avg = np.sqrt((phi_n**2 + phi_d**2) / 2)
        return np.clip(phi_avg, 0, 0.45)
    
    @staticmethod
    def calc_effective_porosity(phi_total, vsh):
        """Calcula porosidad efectiva"""
        if pd.isna(phi_total) or pd.isna(vsh):
            return np.nan
        return phi_total * (1 - vsh)
    
    @staticmethod
    def calc_water_saturation(phi, rt, a=1.0, m=2.0, n=2.0, rw=0.05):
        """Calcula saturación de agua"""
        if pd.isna(phi) or pd.isna(rt):
            return np.nan
        if phi <= 0 or rt <= 0:
            return 1.0
        sw = (a * rw / (phi**m * rt))**(1/n)
        return np.clip(sw, 0, 1)
    
    @staticmethod
    def calc_permeability_kozeny(phi, vsh):
        """Calcula permeabilidad"""
        if pd.isna(phi) or pd.isna(vsh):
            return np.nan
        if phi <= 0:
            return 0.0
        phi_eff = phi * (1 - vsh)
        if phi_eff <= 0 or phi_eff >= 1:
            return 0.0
        k = 100 * phi_eff**3 / (1 - phi_eff)**2
        return np.clip(k, 0, 10000)


class LithoClassifier:
    """Clasificación litológica"""
    
    @staticmethod
    def classify_advanced(vsh, phi, rhob, nphi, pef=None, dominant_matrix='ARENISCA'):
        """Clasificación litológica avanzada"""
        if pd.isna(vsh):
            vsh = 0.5
        if pd.isna(rhob):
            rhob = PetroConfig.RHO_MATRIX.get(dominant_matrix, 2.65)
        if pd.isna(nphi):
            nphi = 0.15
        
        if vsh > 0.7:
            return 'LUTITA'
        
        if pd.notna(pef):
            if pef > 4.5:
                if rhob > 2.80:
                    return 'DOLOMITA'
                else:
                    return 'CALIZA'
            elif pef > 2.5:
                return 'DOLOMITA'
            elif pef < 2.2 and vsh < 0.35:
                return 'ARENISCA'
        
        if vsh > 0.35:
            if rhob > 2.68:
                return 'CALIZA'
            else:
                return 'ARENISCA_ARCILLOSA'
        
        if rhob > 2.78:
            return 'DOLOMITA'
        elif rhob > 2.68:
            return 'CALIZA'
        elif rhob > 2.60:
            if dominant_matrix == 'CALIZA':
                return 'CALIZA'
            elif dominant_matrix == 'DOLOMITA':
                return 'DOLOMITA'
            else:
                return 'ARENISCA'
        else:
            return 'ARENISCA'


def smooth_curve(data, window=5):
    """Suaviza curva con filtro de mediana"""
    valid = data.notna()
    if valid.sum() < window:
        return data
    smoothed = data.copy()
    smoothed[valid] = median_filter(data[valid], size=window)
    return smoothed


def flag_bad_data(df, curve_name, min_val, max_val):
    """Marca datos fuera de rango"""
    if curve_name not in df.columns:
        return pd.Series(False, index=df.index)
    return (df[curve_name] < min_val) | (df[curve_name] > max_val)


def clean_depth_data(df):
    """Limpia datos de profundidad"""
    original_len = len(df)
    
    null_depth = df['DEPTH_FT'].isna()
    if null_depth.any():
        df = df[~null_depth].copy()
    
    duplicates = df.duplicated(subset=['DEPTH_FT'], keep='first')
    if duplicates.any():
        df = df[~duplicates].copy()
    
    if len(df) > 1:
        depth_diff = df['DEPTH_FT'].diff()
        negative_steps = (depth_diff < 0).sum()
        if negative_steps > 0:
            df = df.sort_values('DEPTH_FT').reset_index(drop=True)
    
    df = df.reset_index(drop=True)
    return df


def detect_dominant_matrix(df):
    """Detecta matriz dominante del pozo"""
    if not df['RHOB'].notna().any():
        return 'ARENISCA', 2.65
    
    rhob_valid = df['RHOB'].dropna()
    rhob_median = rhob_valid.median()
    rhob_p25 = rhob_valid.quantile(0.25)
    rhob_p75 = rhob_valid.quantile(0.75)
    
    if 'PEF' in df.columns and df['PEF'].notna().any():
        pef_valid = df['PEF'].dropna()
        pef_median = pef_valid.median()
        
        if pef_median > 4.5:
            if rhob_median > 2.80:
                return 'DOLOMITA', 2.87
            else:
                return 'CALIZA', 2.71
        elif pef_median > 2.5:
            return 'DOLOMITA', 2.87
        elif pef_median < 2.2:
            return 'ARENISCA', 2.65
        else:
            if rhob_median > 2.75:
                return 'DOLOMITA', 2.87
            elif rhob_median > 2.68:
                return 'CALIZA', 2.71
            else:
                return 'ARENISCA', 2.65
    
    if rhob_median > 2.80:
        return 'DOLOMITA', 2.87
    elif rhob_median > 2.68:
        if rhob_p75 > 2.75:
            return 'CALIZA', 2.71
        else:
            if 'GR' in df.columns and df['GR'].notna().any():
                gr_median = df['GR'].dropna().median()
                if gr_median < 50:
                    return 'CALIZA', 2.71
                else:
                    return 'ARENISCA', 2.65
            else:
                return 'CALIZA', 2.71
    elif rhob_median < 2.60:
        return 'ARENISCA', 2.65
    else:
        if 'GR' in df.columns and df['GR'].notna().any():
            gr_median = df['GR'].dropna().median()
            if gr_median < 60:
                return 'CALIZA', 2.71
            else:
                return 'ARENISCA', 2.65
        else:
            return 'ARENISCA', 2.65


def get_valid_data_range(df, key_curves=['GR', 'RHOB', 'NPHI', 'RT', 'CALI']):
    """Encuentra rango de profundidad con datos válidos"""
    available = [c for c in key_curves if c in df.columns and df[c].notna().any()]
    
    if not available:
        return df['DEPTH_FT'].min(), df['DEPTH_FT'].max()
    
    has_data = df[available].notna().any(axis=1)
    
    if not has_data.any():
        return df['DEPTH_FT'].min(), df['DEPTH_FT'].max()
    
    valid_indices = has_data[has_data].index
    first_idx = valid_indices[0]
    last_idx = valid_indices[-1]
    
    depth_start = df.loc[first_idx, 'DEPTH_FT']
    depth_end = df.loc[last_idx, 'DEPTH_FT']
    
    margin = (depth_end - depth_start) * 0.02
    
    return depth_start - margin, depth_end + margin
