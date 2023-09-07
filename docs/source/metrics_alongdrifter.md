# Currents - Along drifter metrics

<br>
 

<br>

## Statistics

[**Check example notebook**](gallery/alongtrack_statistics_description.ipynb)

<br>

### &#x2022; Error variance 

<br>

### &#x2022;  Explained variance 

<br>

<br>

## Spectral


[**Check example notebook**](gallery/alongtrack_spectral_description.ipynb)

<br> 

### &#x2022; Rotary spectrum and noise-to-signal ratio

Rotary spectrum are a frequently used approach for current data analysis. The idea is to resolve the velocity vector into two rotational components: clockwise and anti-clockwise (Mooers, 1973 ; Gonella, 1972). This allows to represent the current energy distribution between the rotation and the latitude. 

For instance, this rotation/latitude representation of the current energy distribution allows to clearly see the near-inertial oscillation induced currents (present in the drifter currents and not in DUACS) around the inertial frequency (dashed line). 

![DUACS currents effective resolution](figures/Maps_DUACS_effres_glob_uv.png)



Also, similarly to the noise-to-signal ratio needed to compute the alongtrack effective resolution, the spectrum of the difference between reconstructed currents and drifter measured currents is divided by the spectrum of the drifter measured currents in order to provide rotation/latitude plots of the noise-to-signal ratio. 


<br>

## References 

- Gonella, J. (1972, December). A rotary-component method for analysing meteorological and oceanographic vector time series. In Deep Sea Research and Oceanographic Abstracts (Vol. 19, No. 12, pp. 833-846). Elsevier.

- Mooers, C. N. (1973, December). A technique for the cross spectrum analysis of pairs of complex-valued time series, with emphasis on properties of polarized components and rotational invariants. In Deep Sea Research and Oceanographic Abstracts (Vol. 20, No. 12, pp. 1129-1141). Elsevier.
