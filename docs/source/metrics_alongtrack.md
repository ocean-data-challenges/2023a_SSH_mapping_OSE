# SSH - Along track metrics

<br>
 

<br>

## Statistics


[**Check example notebook**](gallery/alongtrack_statistics_description.ipynb)

<br>

### &#x2022; Error variance

<br>

###  &#x2022; Explained variance
 

<br>

<br>

## Spectral


[**Check example notebook**](gallery/alongtrack_spectral_description.ipynb)

<br> 

### &#x2022; Effective resolution maps

The effective resolution corresponds to the spatiotemporal scales of the features that can be properly resolved in the maps (Ballarotta et al., 2019). The spatiotemporal resolution of the previous level 4 global SLA products was estimated by Chelton et al. (2011, 2014) and Chelton and Schlax (2003) based on estimates of the mapping errors in sea surface height (SSH) fields constructed from altimeter data or spectral ratio analysis between maps and along-track altimeter data. 

To estimate the effective resolution, we first compute the spectral noise-to-signal ratio, i.e. the ratio between the spectral content of the mapping error and the spectral content of independent along-track observations:

$$\text{NSR}(\lambda_s) = \frac{S_{diff}(\lambda_s)}{S_{obs}(\lambda_s)},$$

where $\lambda_s$ is the spatial wavelength, $S_{diff}(\lambda_s)$ is the power spectral density of the difference (SLA$_{obs}$–SLA$_{map}$) and $S_{obs}(\lambda_s)$ is the spectral density of the independent observation.

Here, we define the effective resolution as the wavelenght at which the noise-to-signal ratio is equal or smaller than 0.5. 

![DUACS SSH effective resolution](figures/Maps_DUACS_effres_glob.png)
<center> 
  <i>Figure 3: Global DUACS effective resolutions with respect to independent nadir SSH Altika. </i> 
</center>

The maps (see DUACS example in Figure 3) are obtained by averaging the effective resolutions on all available along-track segments in each 1°x1° longitude x latitude box.

<br>
 
 
## References

- Ballarotta, M., Ubelmann, C., Pujol, M. I., Taburet, G., Fournier, F., Legeais, J. F., ... & Picot, N. (2019). On the resolutions of ocean altimetry maps. Ocean Science, 15(4), 1091-1109.

- Chelton, D. B., & Schlax, M. G. (2003). The accuracies of smoothed sea surface height fields constructed from tandem satellite altimeter datasets. Journal of Atmospheric and Oceanic Technology, 20(9), 1276-1302.

- Chelton, D. B., Schlax, M. G., & Samelson, R. M. (2011). Global observations of nonlinear mesoscale eddies. Progress in oceanography, 91(2), 167-216.

- Chelton, D., Dibarboure, G., Pujol, M. I., Taburet, G., & Schlax, M. G. (2014). The Spatial Resolution of AVISO Gridded Sea Surface Height Fields, OSTST Lake Constance, Germany, 28–31 October 2014.

