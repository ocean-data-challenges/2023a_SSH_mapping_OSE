import matplotlib
import matplotlib.pylab as plt 
import matplotlib.ticker as mticker 
from scipy.interpolate import RegularGridInterpolator
import pickle
import gc
from matplotlib import cm 
import warnings
import xarray as xr
import numpy as np
import os


def prepare_drifter_data(ds_drifters,maps):

    time_min = (np.datetime64('2019-01-01') - np.datetime64('1950-01-01')) / np.timedelta64(1, 'D')
    time_max = (np.datetime64('2019-12-31') - np.datetime64('1950-01-01')) / np.timedelta64(1, 'D')
    lon_min = maps.longitude.min().values
    lon_max = maps.longitude.max().values
    lat_min = maps.latitude.min().values
    lat_max = maps.latitude.max().values

    box = [lon_min,lon_max,lat_min,lat_max,time_min,time_max]


    ds_drifters.longitude[ds_drifters.longitude<0] = 360 + ds_drifters.longitude[ds_drifters.longitude<0] 
    ds_drifters = ds_drifters.where(ds_drifters.longitude>lon_min,drop=True)
    ds_drifters = ds_drifters.where(ds_drifters.longitude<lon_max,drop=True)
    ds_drifters = ds_drifters.where(ds_drifters.latitude>lat_min,drop=True)
    ds_drifters = ds_drifters.where(ds_drifters.latitude<lat_max,drop=True)

    u_drifter = ds_drifters.EWCT.values
    v_drifter = ds_drifters.NSCT.values
    time_drifter = ds_drifters.time.values
    lon_drifter = ds_drifters.longitude.values
    lat_drifter = ds_drifters.latitude.values
    id_drifter = ds_drifters.sensor_id.values


    time_drifter = (time_drifter.astype('datetime64[h]') - np.datetime64('2019-01-01')).astype(int)

    ind = np.argsort(time_drifter) 
    time_drifter = time_drifter[ind]
    lon_drifter = lon_drifter[ind]
    lon_drifter[lon_drifter<0] = 360 + lon_drifter[lon_drifter<0] #?
    lat_drifter = lat_drifter[ind]
    id_drifter = id_drifter[ind]

    return ind, time_drifter, lon_drifter, lat_drifter, id_drifter 


def adv_eul(time0,lon0,lat0,fu,fv,dt=3600):
    
    u0 = fu((time0,lat0,lon0))
    v0 = fv((time0,lat0,lon0))
    
    dx = u0*dt
    dy = v0*dt

    lon1 = lon0 + dx/(1852 * 60*np.cos(np.deg2rad(lat0)))
    lat1 = lat0 + dy/(1852 * 60)

    return lon1,lat1
    
def adv_rk4(time0,lon0,lat0,fu,fv,dt=3600):
    
    #(u1, v1) = fieldset.UV[particle]
    u1 = fu((time0,lat0,lon0))
    v1 = fv((time0,lat0,lon0))
    #lon1, lat1 = (particle.lon + u1*.5*particle.dt, particle.lat + v1*.5*particle.dt)
    lon1 = lon0 + u1*.5*dt/(1852 * 60*np.cos(np.deg2rad(lat0)))
    lat1 = lat0 + v1*.5*dt/(1852 * 60)
    
    #(u2, v2) = fieldset.UV[time + .5 * particle.dt, particle.depth, lat1, lon1, particle]
    u2 = fu((time0+.5*dt/3600.,lat1,lon1))
    v2 = fv((time0+.5*dt/3600.,lat1,lon1))
    #lon2, lat2 = (particle.lon + u2*.5*particle.dt, particle.lat + v2*.5*particle.dt)
    lon2 = lon0 + u2*.5*dt/(1852 * 60*np.cos(np.deg2rad(lat0)))
    lat2 = lat0 + v2*.5*dt/(1852 * 60)
    
    #(u3, v3) = fieldset.UV[time + .5 * particle.dt, particle.depth, lat2, lon2, particle]
    u3 = fu((time0+.5*dt/3600.,lat2,lon2))
    v3 = fv((time0+.5*dt/3600.,lat2,lon2))
    #lon3, lat3 = (particle.lon + u3*particle.dt, particle.lat + v3*particle.dt)
    lon3 = lon0 + u3*dt/(1852 * 60*np.cos(np.deg2rad(lat0)))
    lat3 = lat0 + v3*dt/(1852 * 60)
    
    #(u4, v4) = fieldset.UV[time + particle.dt, particle.depth, lat3, lon3, particle]
    u4 = fu((time0+dt/3600.,lat3,lon3))
    v4 = fv((time0+dt/3600.,lat3,lon3))
    #particle.lon += (u1 + 2*u2 + 2*u3 + u4) / 6. * particle.dt
    #particle.lat += (v1 + 2*v2 + 2*v3 + v4) / 6. * particle.dt
    lon0 +=  (u1 + 2*u2 + 2*u3 + u4)/6. * dt/(1852 * 60*np.cos(np.deg2rad(lat0)))
    lat0 +=  (v1 + 2*v2 + 2*v3 + v4)/6. * dt/(1852 * 60)
    
    return lon0,lat0
  
def compute_traj(dict_drifter_adv_maps, horizons, fu, fv ,Np, Nt, dt_h, method_name='DUACS',dir_out='../Data', prefix_out='dict_drifter_adv', mode='euler', write=False):


    for h in horizons[1:]:
        print('h',h)

        print(h,horizons[-1],end='\r')

        # maps

        if not write and os.path.exists(f'{dir_out}/{prefix_out}_{method_name}_{mode}_{int(h)}.pic'): 
            with open(f'{dir_out}/{prefix_out}_{method_name}_{mode}_{int(h)}.pic','rb') as f:
                dict_drifter_adv_maps[h] = pickle.load(f)

        else:
            dict_drifter_adv_maps[h] = {}            
            dict_drifter_adv_maps[h]['time'] = np.empty((Np,),dtype='int')
            dict_drifter_adv_maps[h]['lon'] = np.empty((Np,))
            dict_drifter_adv_maps[h]['lat'] = np.empty((Np,))
            dict_drifter_adv_maps[h]['id'] = np.empty((Np,),dtype='int')


            for i,(time0,lon0,lat0,id0) in enumerate(zip(dict_drifter_adv_maps[h-1]['time'],
                                                     dict_drifter_adv_maps[h-1]['lon'],
                                                     dict_drifter_adv_maps[h-1]['lat'],
                                                     dict_drifter_adv_maps[h-1]['id'])):


                if time0<Nt:

                    try:
                        if mode=='euler': 
                            lon1,lat1 = adv_eul(time0,lon0,lat0,fu,fv,dt_h*3600)

                        elif mode=='rk4':
                            lon1,lat1 = adv_rk4(time0,lon0,lat0,fu,fv,dt_h*3600)
                    except:
                        lon1,lat1 = np.nan,np.nan

                    dict_drifter_adv_maps[h]['time'][i] = time0+dt_h 
                    dict_drifter_adv_maps[h]['lon'][i] = lon1%360
                    dict_drifter_adv_maps[h]['lat'][i] = lat1
                    dict_drifter_adv_maps[h]['id'][i] = id0

            with open(f'{dir_out}/{prefix_out}_{method_name}_{mode}_{int(h)}.pic','wb') as f:
                pickle.dump(dict_drifter_adv_maps[h],f)    


    with open(f'{dir_out}/{prefix_out}_{method_name}_{mode}.pic','wb') as f:
        pickle.dump(dict_drifter_adv_maps,f)

    return dict_drifter_adv_maps 


from math import sin, cos, sqrt, atan2, radians

def dist_drifters(lat1,lon1,lat2,lon2):
    # Approximate radius of earth in km
    R = 6373.0

    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    distance = R * c 
    
    return distance




def compute_deviation(dict1, Nt, dt_hr, horizon_days,lon_out=np.arange(0, 360, 1),lat_out=np.arange(-90, 90, 1), dir_out='../results/', method_name= 'DUACS', results_out='deviat_uv_DUACS.nc'):
    
    
    import pyinterp

    d1 = {} 
    lo1 = {} 
    la1 = {} 

    # Compute deviation (dist between real and artif drifters)
    
    it = 0
    for t in np.arange(dt_hr,Nt,dt_hr):
        #print(t,Nt,end='\r')
        ind0 = (dict1[0]['time']==t) 
        lon0 = dict1[0]['lon'][ind0]
        lat0 = dict1[0]['lat'][ind0]
        id0 = dict1[0]['id'][ind0]
        for h in dict1:
            if h==0:
                continue
            else:   
                if h not in d1:
                    d1[h] = [] 
                    lo1[h] = [] 
                    la1[h] = [] 

                ind1 = dict1[h]['time']==t  



                lon1 = dict1[h]['lon'][ind1]
                lat1 = dict1[h]['lat'][ind1]
                id1 = dict1[h]['id'][ind1]




                for (_lon0,_lat0,_id0) in zip(lon0,lat0,id0):
                    if _id0 in id1 : 
                        d1[h].append(dist_drifters(_lat0,_lon0,lat1[id1==_id0],lon1[id1==_id0])[0]) 
                        lo1[h].append(_lon0)
                        la1[h].append(_lat0)
                        
    d_mean_1 = np.array([np.sqrt(np.nansum(np.array(d1[h])**2)/np.count_nonzero(~np.isnan(d1[h]))) for h in d1])


    binning = pyinterp.Binning2D(pyinterp.Axis(lon_out, is_circle=True),
                                 pyinterp.Axis(lat_out))
 

    rmse_norm = np.zeros([np.size(horizon_days),np.size(lon_out),np.size(lat_out)]) 
    var_norm = np.zeros([np.size(horizon_days),np.size(lon_out),np.size(lat_out)])  
 
    for h in horizon_days:
        binning.clear()
        binning = binning.push_delayed(lo1[h], la1[h], d1[h]).compute() 
        rmse_norm[h-1,:,:] = binning.variable('mean')
        var_norm[h-1,:,:] = binning.variable('variance')
        
        
   
    # Save results
    ds1 = xr.Dataset({'deviation_maps' : (('lat', 'lon','horizons'), rmse_norm.T),
                      'var_deviation_maps' : (('lat', 'lon','horizons'), var_norm.T), 
                      'deviation_mean' : (('horizons'), d_mean_1) 
                      },
                      coords={'lon': lon_out, 
                              'lat': lat_out,
                              'horizons': horizon_days,
                               }
                       )
     
    
    ds1 = ds1.assign_attrs({'method':method_name})
    ds1.to_netcdf(f'{dir_out}/{results_out}', format="NETCDF4")
        
    return rmse_norm, var_norm, d_mean_1 



def plot_traj_deviation_maps(lon_g, lat_g, rmse_norm, dt_hr=24, horizon_days=[1,2,3],vmax_h = [40,80,120], method_name='DUACS'):
 
    idays=0
    for ndays in horizon_days: 
        h = ndays*24/dt_hr
         


        import cartopy.crs as ccrs
        from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
        import matplotlib.ticker as mticker
        import cmocean
        #from conv_glo2 import read_drifters

        plt.figure(figsize=(12,12))
        ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
        plt.title(method_name+', Horizon:'+str(ndays)+'days',fontsize=25)
        
        lon_g0, lat_g0 = np.meshgrid(lon_g, lat_g)
         

        im = ax.pcolormesh(lon_g0,lat_g0,rmse_norm[idays,:,:].T,vmin=0,vmax=vmax_h[idays],cmap='viridis',transform=ccrs.PlateCarree()) 


        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,alpha=0.5)
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabels_top = False
        gl.ylabels_right = False 
        gl.xlabel_style = {'size': 20}
        gl.ylabel_style = {'size': 20}
        #gl.ylocator = mticker.FixedLocator([-30,-35,-40])
        ax.coastlines(linewidth=3)


        cbar = plt.colorbar(im,ax=ax,fraction=0.023, pad=0.04)
        cbar.ax.set_ylabel('km',size=20)
        cbar.ax.tick_params(labelsize=15)  

        plt.show()
        
        idays +=1 
        
        
        
def plot_meantraj_deviation(dir_out='../results/',just_basin=None,prefix_='deviat_uv_'):

    plt.figure(figsize=(8,6))
    plt.title('Drifter trajectory deviation',fontsize=18)
    
    for file in os.listdir(dir_out):
        if file.startswith(prefix_):
            if just_basin is not None:
                if just_basin in dir_out+file:
                    ds_dev_uv = xr.open_dataset(dir_out+file)
                    plt.plot(ds_dev_uv.horizons,ds_dev_uv.deviation_mean,label=ds_dev_uv.method)
            else: 
                ds_dev_uv = xr.open_dataset(dir_out+file)
                plt.plot(ds_dev_uv.horizons,ds_dev_uv.deviation_mean,label=ds_dev_uv.method)

    plt.xlabel('Horizon (days)',fontsize=15)
    plt.ylabel('Deviation (km)',fontsize=15)
    plt.xticks(ds_dev_uv.horizons,fontsize=14) 
    plt.yticks(fontsize=14)
    plt.legend()
    plt.grid()
    
    plt.show()
