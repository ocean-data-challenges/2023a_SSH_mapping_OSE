import cartopy.crs as ccrs
import hvplot.xarray
import pandas as pd
import xarray as xr
import numpy as np





def regional_zoom(ds_glob, boxlon, boxlat, namelon='lon', namelat='lat'):

    min_lon = boxlon[0] 
    max_lon = boxlon[1] 
    min_lat = boxlat[0]
    max_lat = boxlat[1] 

    import copy
    ds_reg = copy.deepcopy(ds_glob)

    long_attrs = ds_reg[namelon].attrs 
    
    ds_reg[namelon] = ds_reg[namelon].where(ds_reg[namelon]<180,ds_reg[namelon]-360).values
    ds_reg = ds_reg.sortby(ds_reg[namelon])
      
  
    ds_reg = ds_reg.where(ds_reg[namelon]<max_lon,drop=True)
    ds_reg = ds_reg.where(ds_reg[namelon]>min_lon,drop=True)
    ds_reg = ds_reg.where(ds_reg[namelat]<max_lat,drop=True)
    ds_reg = ds_reg.where(ds_reg[namelat]>min_lat,drop=True) 
    
    
    #ds_reg[namelon] = ds_reg[namelon].values%360
    #ds_reg = ds_reg.sortby(ds_reg[namelon])
    ds_reg[namelon].attrs = long_attrs 
    #ds_reg = ds_reg.sortby(ds_reg['time'])

    return ds_reg


def compare_stat_score_map(study_filename, ref_filename,boxlon = [-180, 180],boxlat = [-90, 90], vartype='err_var'):
    

    
    ds_ref_binning_allscale = xr.open_dataset(ref_filename, group='all_scale')
    ds_ref_binning_allscale = regional_zoom(ds_ref_binning_allscale,boxlon, boxlat)
    ds_ref_binning_filtered = xr.open_dataset(ref_filename, group='filtered')
    ds_ref_binning_filtered = regional_zoom(ds_ref_binning_filtered,boxlon, boxlat)
    
    explained_variance_ref_all_scale = 1 - ds_ref_binning_allscale['variance_mapping_err']/ds_ref_binning_allscale['variance_track']
    explained_variance_ref_filtered = 1 - ds_ref_binning_filtered['variance_mapping_err']/ds_ref_binning_filtered['variance_track']
    
    ds_study_binning_allscale = xr.open_dataset(study_filename, group='all_scale')
    ds_study_binning_allscale = regional_zoom(ds_study_binning_allscale,boxlon, boxlat)
    ds_study_binning_filtered = xr.open_dataset(study_filename, group='filtered')
    ds_study_binning_filtered = regional_zoom(ds_study_binning_filtered,boxlon, boxlat)
    
    explained_variance_study_all_scale = 1 - ds_study_binning_allscale['variance_mapping_err']/ds_study_binning_allscale['variance_track']
    explained_variance_study_filtered = 1 - ds_study_binning_filtered['variance_mapping_err']/ds_study_binning_filtered['variance_track']
    
    
    if vartype == 'err_var':
    
    
        fig1 = ds_ref_binning_allscale['variance_mapping_err'].hvplot.quadmesh(x='lon',
                                                                  y='lat',
                                                                  clim=(0, 0.002),
                                                                  cmap='Reds',
                                                                  rasterize=True,
                                                                  title='Error variance [All scale]: '+ds_ref_binning_allscale.attrs['method'])

        fig2 = ds_ref_binning_filtered['variance_mapping_err'].hvplot.quadmesh(x='lon',
                                                                  y='lat',
                                                                  clim=(0, 0.002),
                                                                  cmap='Reds',
                                                                  rasterize=True,
                                                                  title='Error variance [65:500km]: '+ds_ref_binning_filtered.attrs['method'])
        
    
        fig3 = ds_study_binning_allscale['variance_mapping_err'].hvplot.quadmesh(x='lon',
                                                                  y='lat',
                                                                  clim=(0, 0.002),
                                                                  cmap='Reds',
                                                                  rasterize=True,
                                                                  title='Error variance [All scale]: '+ds_study_binning_allscale.attrs['method'])

        fig4 = ds_study_binning_filtered['variance_mapping_err'].hvplot.quadmesh(x='lon',
                                                                  y='lat',
                                                                  clim=(0, 0.002),
                                                                  cmap='Reds',
                                                                  rasterize=True,
                                                                  title='Error variance [65:500km]: '+ds_study_binning_filtered.attrs['method'])

        fig5 = (100*(ds_study_binning_allscale['variance_mapping_err'] - ds_ref_binning_allscale['variance_mapping_err'])/ds_ref_binning_allscale['variance_mapping_err']).hvplot.quadmesh(x='lon',
                                                                  y='lat',
                                                                  clim=(-20, 20),
                                                                  cmap='coolwarm',
                                                                  rasterize=True,
                                                                  title='Error variance [All scale]')

        fig6 = (100*(ds_study_binning_filtered['variance_mapping_err'] - ds_ref_binning_filtered['variance_mapping_err'])/ds_ref_binning_filtered['variance_mapping_err']).hvplot.quadmesh(x='lon',
                                                                  y='lat',
                                                                  clim=(-20, 20),
                                                                  cmap='coolwarm',
                                                                  rasterize=True,
                                                                  title='Error variance [65:500km]')
    
    if vartype == 'expl_var':
    
        fig1 = explained_variance_ref_all_scale.hvplot.quadmesh(x='lon',
                                                                  y='lat',
                                                                  clim=(0, 1),
                                                                  cmap='RdYlGn',
                                                                  rasterize=True,
                                                                  title='Explained variance [All scale]: '+ds_ref_binning_allscale.attrs['method']
                                                               )

        fig2 = explained_variance_ref_filtered.hvplot.quadmesh(x='lon',
                                                                  y='lat',
                                                                  clim=(0, 1),
                                                                  cmap='RdYlGn',
                                                                  rasterize=True,
                                                                  title='Explained variance [65:500km]: '+ds_ref_binning_allscale.attrs['method']
                                                               )
        
    
        fig3 = explained_variance_study_all_scale.hvplot.quadmesh(x='lon',
                                                                  y='lat',
                                                                  clim=(0, 1),
                                                                  cmap='RdYlGn',
                                                                  rasterize=True,
                                                                  title='Explained variance [All scale]: '+ds_study_binning_allscale.attrs['method']
                                                               )

        fig4 = explained_variance_study_filtered.hvplot.quadmesh(x='lon',
                                                                  y='lat',
                                                                  clim=(0, 1),
                                                                  cmap='RdYlGn',
                                                                  rasterize=True,
                                                                  title='Explained variance [65:500km]: '+ds_study_binning_allscale.attrs['method']
                                                               )

        fig5 = (explained_variance_study_all_scale - explained_variance_ref_all_scale).hvplot.quadmesh(x='lon',
                                                                  y='lat',
                                                                  clim=(-0.2, 0.2),
                                                                  cmap='coolwarm_r',
                                                                  rasterize=True,
                                                                  title='Gain(+)/Loss(-) Explained variance [All scale]')

        fig6 = (explained_variance_study_filtered - explained_variance_ref_filtered).hvplot.quadmesh(x='lon',
                                                                  y='lat',
                                                                  clim=(-0.2, 0.2),
                                                                  cmap='coolwarm_r',
                                                                  rasterize=True,
                                                                  title='Gain(+)/Loss(-) Explained variance [65:500km]')
    
#     fig5 = ds_binning_allscale['rmse'].hvplot.quadmesh(x='lon',
#                                                               y='lat',
#                                                               clim=(0, 0.1),
#                                                               cmap='Reds',
#                                                               rasterize=True,
#                                                               title='RMSE [All scale]')
    
#     fig6 = ds_binning_filtered['rmse'].hvplot.quadmesh(x='lon',
#                                                               y='lat',
#                                                               clim=(0, 0.1),
#                                                               cmap='Reds',
#                                                               rasterize=True,
#                                                               title='RMSE [65:500km]')
    
    return (fig1 + fig2 + fig3 + fig4 + fig5 + fig6).cols(2)



def compare_psd_score(study_filename, ref_filename,boxlon = [-180, 180],boxlat = [-90, 90]):
    
    ds_ref = xr.open_dataset(ref_filename)
    ds_ref = regional_zoom(ds_ref,boxlon, boxlat)
    ds_study = xr.open_dataset(study_filename)
    ds_study = regional_zoom(ds_study,boxlon, boxlat)
    
    fig0 = ds_ref.effective_resolution.hvplot.quadmesh(x='lon', 
                                                   y='lat', 
                                                   cmap='Spectral_r', 
                                                   clim=(100, 500), 
                                                   title='Effective resolution [km]: '+ds_ref.attrs['method'],
                                                   rasterize=True, 
                                                   projection=ccrs.PlateCarree(), 
                                                   project=True, 
                                                   geo=True, 
                                                   coastline=True)
    
    
    fig1 = ds_study.effective_resolution.hvplot.quadmesh(x='lon', 
                                                   y='lat', 
                                                   cmap='Spectral_r', 
                                                   clim=(100, 500), 
                                                   title='Effective resolution [km]: '+ds_study.attrs['method'],
                                                   rasterize=True, 
                                                   projection=ccrs.PlateCarree(), 
                                                   project=True, 
                                                   geo=True, 
                                                   coastline=True)
    
    fig2 = (100*(ds_study.effective_resolution - ds_ref.effective_resolution)/ds_ref.effective_resolution).hvplot.quadmesh(x='lon', 
                                                   y='lat', 
                                                   cmap='coolwarm', 
                                                   clim=(-20, 20), 
                                                   title='Gain(-)/loss(+) Effective resolution [%]',
                                                   rasterize=True, 
                                                   projection=ccrs.PlateCarree(), 
                                                   project=True, 
                                                   geo=True, 
                                                   coastline=True)
    
    return (fig0 + fig1 + fig2).cols(1)


