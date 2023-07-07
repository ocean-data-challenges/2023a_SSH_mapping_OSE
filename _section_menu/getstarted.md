---
name: Get started
url: https://ocean-data-challenges.github.io/2023a_SSH_mapping_OSE/docs/getstarted.html
---

# Get started

<br>

## Installation
:computer: _**How to get started ?**_

Clone the data challenge repo: 
```
git clone https://github.com/ocean-data-challenges/2023a_SSH_mapping_OSE.git
```
or using SSH: 
```
git clone git@github.com:ocean-data-challenges/2023a_SSH_mapping_OSE.git
```

create the data challenge conda environment, named env-dc-swot-filtering, by running the following command:
```
conda env create --file=dc_environment.yml 
```
and activate it with:

```
conda activate env-dc-global-ose
```
then add it to the available kernels for jupyter to see: 
```
ipython kernel install --name "env-dc-global-ose" --user
```
finally, select the "env-dc-global-ose" kernel in your notebook with Kernel > Change Kernel.

You're now good to go ! 


## Download the data

The data are hosted and can be accessed on the MEOM server opendap [here](https://ige-meom-opendap.univ-grenoble-alpes.fr/thredds/catalog/meomopendap/extract/ocean-data-challenges/dc_Map_global_OSE/catalog.html). The disk space needed to locally download the full dataset (for the reconstruction experiment, the independant evaluation and the comparison) is approximately 33Go. The comparison data is by far the heaviest with approximately 26Go. 

#### A notebook to illustrate how to download and read the global data is available: [download_and_acces_global_data.ipynb](https://github.com/ocean-data-challenges/2023a_SSH_mapping_OSE/blob/main/nb_download_data/download_and_acces_global_data.ipynb)


#### If you are only interested in regional data, a notebook is available to read online the global data and download only regional data: [read_and_download_regional_data.ipynb](https://github.com/ocean-data-challenges/2023a_SSH_mapping_OSE/blob/main/nb_download_data/read_and_download_regional_data.ipynb)

The dataset is presented with the following directory structure:

### 1) Data for experiment

##### Nadir alongtrack data (L3 products) for SSH map reconstruction

```
.
|-- alongtrack
``` 

### 2) Data for evaluation

##### Independant nadir alongtrack data (L3 products) for SSH evaluation

```
.
|-- independant_alongtrack
|   |-- alg		% DT Altika Drifting Phase Global Ocean Along track SSALTO/DUACS Sea Surface Height L3 product
|   |   |-- 2019
|   |   |   |-- dt_global_alg_phy_l3_2019*.nc
```

##### Independant drifters for currents evaluation

```
.
|-- independent_drifters
|   |-- uv_drifters_*.nc           % Drifter data
|   |-- index_history.txt          % Preprocessing drifter data information
|   |-- reformate_drifters.ipynb   % Preprocessing notebook (for informational purposes, not needed for experiments)
```

##### Auxiliary data for diagnostics

```
.
|-- sad
|   |-- distance_to_nearest_coastline_60.nc
|   |-- land_water_mask_60.nc
|   |-- variance_cmems_dt_allsat.nc

```

### 3) Data for comparison

##### Reconstruction maps for comparison

```
.
|-- maps
|   |-- DUACS_global_allsat-alg			% DUACS reconstruction			
|   |-- MIOST_geos_global_allsat-alg		% MIOST reconstruction
|   |-- MIOST_geos_barotrop_eqwaves_global_allsat-alg	% MIOST reconstruction with barotropic and equatorial waves processing
```


### Download and read the data

The data can be downloaded locally using the wget command. We recommand that the data be stored in the `data/` repository. 
For example, to download and unzip the experiment alongtrack data:



## Evaluation

The mapping methods are evaluated against independent data using two independant datasets:

### Independant nadir SSH data: [Check example 1](https://github.com/ocean-data-challenges/2023a_SSH_mapping_OSE/blob/main/nb_diags_global/ssh_scores_DUACS_geos.ipynb)

The ocean surface topography reconstruction is compared with independant data from Saral/AltiKa altimeter. The metrics available using this independant dataset are:

- Grid boxes statistics (maps)
- Statistics by regimes (scalar scores) 
- Spectral effective resolution (maps)

### Independant drifter currents data: [Check example 2](https://github.com/ocean-data-challenges/2023a_SSH_mapping_OSE/blob/main/nb_diags_global/uv_scores_DUACS_geos.ipynb)

The surface currents are assessed by comparing them to the surface drifter velocities. The metrics available using this independant dataset are:

- Grid boxes statistics (maps)
- Statistics by regimes (scalar scores)
- Zonaly averaged rotary spectra (omega-latitude plots) 
- 1D along trajectory spectrum (plots)
