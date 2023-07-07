
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
