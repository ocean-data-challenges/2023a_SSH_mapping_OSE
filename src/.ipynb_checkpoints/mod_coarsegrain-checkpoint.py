import numpy as np
from scipy.optimize import curve_fit
from numpy.fft import fft, ifft, fftfreq, fftshift
from joblib import Parallel, delayed
import xarray as xr
# Attempt to import PyFFTW
try:
    import pyfftw
    pyfftw_available = True
except ImportError:
    pyfftw_available = False


def first_below_threshold(snr, threshold):
    """Finds the first index where an array falls below a threshold.

    Args:
        snr: The array to search.
        threshold: The threshold value.

    Returns:
        The first index where the array falls below the threshold, 
        or None if the array never falls below the threshold.
    """

    indices_below_threshold = np.where(snr < threshold)[0]  # Find indices where snr < threshold

    if len(indices_below_threshold) > 0:
        return indices_below_threshold[0]  # Return the first index
    else:
        return None  


def compute_effective_coarse_graining_scale_single_lat(args):
    jj, wavenumber, snr, coarse_graining_kernel = args
    """Computes the effective coarse graining scale for a single latitude index."""
    
    snr_threshold = 0.1
    min_curve_fit_length = 5
    
    if coarse_graining_kernel == 'tanh':
        def fit_function(x, l):
            return f_tanh(x, l)
    else:
        'Supported coarse_graining_kernel types: [tanh, gaussian]'

    coarse_graining_scale_row = np.empty(snr.shape[-1])

    for ii in range(snr.shape[-1]):
        if not np.ma.is_masked(snr[:, ii]):
            params, _ = curve_fit(
                    fit_function,
                    2 * np.pi * wavenumber,
                    snr[:, ii],
                    p0=[100],
                    bounds=(10, 500),
                )
            coarse_graining_scale_row[ii] = params[0]

    return coarse_graining_scale_row


def compute_effective_coarse_graining_scale(lon, lat, wavenumber, psd_diff, psd_ref, num_workers = 1, coarse_graining_kernel="tanh"):
    
    snr = 1 - psd_diff / psd_ref
    coarse_graining_scale = np.empty((lat.size, lon.size))
    args = [(wavenumber.copy(), snr[:, jj, :].copy(), coarse_graining_kernel) for jj in range(lat.size)]
    # Parallelization with Joblib
    with Parallel(n_jobs=num_workers, verbose=10) as parallel:
        results = parallel(
            delayed(compute_effective_coarse_graining_scale_single_lat)(
                [jj, wavenumber, snr[:, jj, :], coarse_graining_kernel]
            )
            for jj in range(lat.size)
        )

    # Combine results
    for jj, result in enumerate(results):
        coarse_graining_scale[jj] = result
    
    return coarse_graining_scale

# filter kernel
def g_tanh(x, l):
    return 1-np.tanh(10*(np.abs(x)/(l/2)-1))

if pyfftw_available:
    # dummy data to instantiate the pyFFTW object
    x = np.linspace(-10000,10000,100001)
    l = 100
    y = g_tanh(x,l)
    fft_object = pyfftw.builders.fft(fftshift(y), planner_effort='FFTW_ESTIMATE') 
else:
    fft_object = fft

# Fourier transform of filter kernel
def g_fourier_transform_tanh(k_sampled, l, fft_object):
    x = np.linspace(-10000,10000,100001)
    y = g_tanh(x,l)
    # ft = fft(fftshift(y))/len(y)
    ft = fft_object(fftshift(y))/len(y)
    first_negative_index = np.argmax(ft < 0)
    ft[first_negative_index:] = 0
    indices = 2*np.pi*fftfreq(len(x), d=(x[1] - x[0]))
    
    g_transform = ft[1:ft.shape[0]//2]
    indices = indices[1:indices.shape[0]//2]

    return np.interp(k_sampled, indices, g_transform)

# functional form for 1 - SNR as function of wavenumber assuming tanh filter kernel with scale l
def f_tanh(x, l):
    g_h = g_fourier_transform_tanh(x,l, fft_object)
    a = 1/np.abs(g_h[0]) #ensures proper normalisation
    return 2*a*np.real(g_h) - np.abs(a*g_h)**2

# calculate effective coarse graining scale from saved psd data
def write_coarse_graining_scales(psd_filename, num_workers):
    ds = xr.open_dataset(psd_filename)
    
    lon = np.ma.masked_invalid(ds['lon'].values)
    lat = np.ma.masked_invalid(ds['lat'].values)
    wavenumber = np.ma.masked_invalid(ds['wavenumber'].values)
    psd_diff = np.ma.masked_invalid(ds['psd_diff'].values)
    psd_ref = np.ma.masked_invalid(ds['psd_ref'].values)
    
    scales = compute_effective_coarse_graining_scale(lon, lat, wavenumber, psd_diff, psd_ref, num_workers = num_workers)
    
    eff_res = ds['effective_resolution'].values
    scales[np.isnan(eff_res)] = np.nan
    
    ds['effective_coarse_graining_scale'] = xr.DataArray(data = scales, dims = ['lat','lon'], coords = dict(lat = ('lat', lat), lon = ('lon', lon)))
    
    ds.to_netcdf(psd_filename[:-3] + '_w_coarsegrain.nc')
    