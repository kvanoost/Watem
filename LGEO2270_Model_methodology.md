# LGEO2270 — WaTEM/SEDEM methodology and technical reference

This document explains the baseline teaching implementation. It is not a calibrated model or a complete description of WaTEM/SEDEM. The student notebook is the authoritative executable implementation; the exported parameter and provenance files record effective settings.

<img src="https://cdn.uclouvain.be/groups/cms-editors-arec/charte-graphique-uclouvain/telechargements/logo_UCLouvain_format_jpg_quadri.jpg?itok=hCkd3jyK" alt="UCLouvain" width="220">

# LGEO2270 | Physical geography excursion
## WaTEM/SEDEM — NB01: Catchment baseline
**Condroz–Famenne · Soil erosion, runoff and landscape connectivity**

School of Geography · Earth and Life Institute · UCLouvain

### Model concept

![Conceptual diagram: geographic inputs, two model branches, soil management, buffer strips, infrastructure and scenario evaluation](https://raw.githubusercontent.com/kvanoost/Watem/main/assets/model_workflow.svg)

[Open full-size model diagram](https://github.com/kvanoost/Watem/blob/main/assets/model_workflow.svg)

The branches share the spatial domain and routing framework; event sediment production is erosivity-based, not dynamically coupled to runoff. Channel runoff uses explicit D8 links when enabled.

**How to use this notebook:** Run the seven numbered code blocks in order. Confirm both maps explicitly. All computations are local to the Colab runtime; no Google Drive mount. Retain the final ZIP for NB02 and NB03. This is a teaching model, not a calibrated forecast.

[Official UCLouvain logo and graphic charter](https://uclouvain.be/fr/presse/logo-de-l-uclouvain)

**Simulation design:** one annual erosion run and one 40 mm rainfall event per baseline or management scenario.


## Automatic acquisition and reproducibility

The notebooks run on a fresh Google Colab Linux runtime. The student supplies an outlet location, not geographical input files. No Google Drive mount, Earth Engine authentication or manually prepared catchment is required. Access to the GitHub repository and the public data endpoints is required; temporary service outages can interrupt a run.

### Software acquisition

| Component | Automatic source | Purpose |
|---|---|---|
| SAGA GIS command-line tools | Ubuntu package repositories (apt) | Terrain import/export, stream burning and depression filling |
| SAGA-WaTEM 2025.6.11 | [DOV-Vlaanderen/saga-watem releases](https://github.com/DOV-Vlaanderen/saga-watem/releases/tag/2025.6.11) | Additional WaTEM and topology tools required by the wrapper |
| WaTEM/SEDEM 5.0.3 Linux binary | [watem-sedem release](https://github.com/watem-sedem/watem-sedem/releases/tag/5.0.3) | Native erosion, sediment delivery and event runoff calculations |
| pywatemsedem | [Pinned upstream revision](https://github.com/watem-sedem/pywatemsedem/tree/226a7c06ae836f9736c1a88b74b5346033a2a8d6) | Prepare native inputs and model settings |
| Python dependencies | Colab environment and PyPI as required | NumPy, Numba, rasterio, geopandas, fiona and related libraries |
| Reporting utilities | [Pinned teaching helper](https://github.com/kvanoost/Watem/blob/50839661b3a72d2f7a78b7c3d0a4ba7019908cc7/watem_student_common.py) | Packaging, native execution, raster/report extraction and comparison |

NB01 installs only terrain software for block 2; WaTEM-specific components are deferred until the basin is accepted in block 5. Installed software is reused where possible within the runtime. The wrapper is checked out at the pinned revision without downloading Git LFS data; plugin libraries and binary shared-library dependencies are checked. NB02 uses the frozen native model inputs and retrieves the same executable directly; it does not rebuild the geographic baseline. NB03 reads exported results.

### Data endpoints and spatial processing

The following URLs are the actual endpoints configured in NB01 (not independently rechecked during this documentation update).

| Dataset | Server and access | Spatial preparation |
|---|---|---|
| Copernicus DEM GLO-30 | [AWS public COG bucket](https://copernicus-dem-30m.s3.amazonaws.com/) | Derive intersecting 1° tile names, read spatial windows, reproject bilinearly |
| ESA WorldCover 2021 v200 | [AWS public map bucket](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/) | Derive intersecting 3° tile names, read windows, nearest-neighbour reprojection |
| RHW hydrographic axes | [SPW MapServer layer 1](https://geoservices.wallonie.be/arcgis/rest/services/EAU/RES_HYDRO_WAL/MapServer/1) | Query full buffered terrain extent, clip, explode line geometries, rasterize all touched cells |
| SIGEC parcels 2025 | [SPW MapServer layer 4](https://geoservices.wallonie.be/arcgis/rest/services/AGRICULTURE/SIGEC_PARC_AGRI_2025/MapServer/4) | Query watershed bounding box, clip parcels, decode crop labels, assign IDs and lookup values |
| CNSW soil map | [SPW MapServer layer 2](https://geoservices.wallonie.be/arcgis/rest/services/SOL_SOUS_SOL/CNSW/MapServer/2) | Clip to catchment; currently for interpretation, not parameter estimation |
| PICC infrastructure and water | [SPW PICC_VDIFF MapServer](https://geoservices.wallonie.be/arcgis/rest/services/TOPOGRAPHIE/PICC_VDIFF/MapServer) | Discover layer IDs from service metadata; retrieve road axes, building footprints and water polygons |
| Visual basemap | Esri World Topographic / Imagery / Street tile services at server.arcgisonline.com | Browser-only map context, not numerical model data |

SPW feature requests first retrieve object IDs intersecting the bounding box, then request those IDs in bounded batches with geometry and necessary attributes. RHW regional requests use up to four concurrent workers, retry failed requests and fall back to sequential retrieval. The returned feature count is checked against the requested IDs. Features are reprojected to Belgian Lambert 72 (EPSG:31370), repaired where needed and clipped to the working geometry. Exact dataset URLs and metadata are retained in the exported package.

All numerical rasters share a 20 m grid aligned in Lambert 72. A point selection creates an approximately 6 km search window with a 12 km margin on every side. SAGA burns the RHW mask by 1 m (method 0) and applies Wang–Liu depression filling with a 0.01° minimum slope. The D8 kernel selects the steepest strictly downhill neighbour, using cardinal and diagonal distances, then accumulates cell counts and propagates a boundary flag in one topological traversal. It checks for cycles and conservation of terminal contributing area. Each cell represents 0.04 ha. Block 4 independently traverses upstream links to validate the selected watershed count. The regional buffer is a pragmatic safeguard, not a guarantee of complete major transboundary basins.

### From geographical data to model inputs

The parcel map (PRC) combines agricultural parcel IDs, WorldCover background and mapped infrastructure/water. Native codes are positive for agricultural cells, zero outside the basin, and negative for special classes such as rivers, roads/infrastructure, forest, pasture and water. The model channel network is derived from D8 upstream area (25 ha default), not simply the RHW lines. Crop labels set provisional C and CN; uncovered agricultural cells use generic defaults. The exact D8 mask, full rectangular conditioned DEM and constant K raster are checked/repaired after wrapper export. Native annual and event configurations use the same grid and fixed baseline inputs, apart from mode-specific forcing and runoff extensions.

The exported ZIP is the reproducibility unit: reference GIS layers, data_lineage.csv, source schemas, parcel parameter table, effective settings, native input/output files, reports and completion manifest. NB02 checks the baseline fingerprint before cloning the inputs. Live data may change between new NB01 runs; retain the original ZIP to compare scenarios consistently.

## 2. Download terrain and prepare hydrology
Software: pinned pywatemsedem, WaTEM/SEDEM 5.0.3 and SAGA-WaTEM. No tutorial geographical files or Git LFS downloads are required. Model settings are embedded as a local teaching preset; an exact checksum-verified cached Langegracht INI is used if available. The preset is based on the upstream Molenbeek example and wrapper tests and is not verified identical to Langegracht.

| Web input | Source resolution / type | Conversion |
|---|---|---|
| Copernicus GLO-30 elevation | ~30 m | Bilinear resampling to 20 m Belgian Lambert 72; optional supplied SPW DEM |
| ESA WorldCover 2021 v200 | 10 m | Nearest-neighbour resampling to common grid |
| SPW RHW river axes | Vector | Rasterize for stream burning; condition DEM with SAGA sink filling |

The 20 m grid does not imply 20 m original elevation detail. D8 flow directions, contributing area and upstream boundary connectivity are computed together using a compiled Numba kernel. A fixed 12 km margin surrounds the initial search extent.

Software diagnostics are hidden by default; enable VERBOSE in block 1 to see them. Final effective settings are exported in effective_model_settings.csv; verbose mode displays them in block 5.

Block 2 reports five timed stages. Software is reused within the same runtime when the pinned version is available. A new Colab runtime still needs installation; remote raster and river services and the initial D8 numerical compilation can be slow. Debug output is off by default.

Terrain coverage: a fixed 12 km margin surrounds the initial search area (approximately 30 × 30 km for a point). No student buffer setting is required. The outlet map checks upstream coverage and area before confirmation. Select yellow or orange channels; grey channels have incomplete coverage and red channels exceed the 5,000 ha classroom limit.

## 4. Delineate and inspect the watershed
The original D8 watershed raster defines the active domain. Check its area, boundary and agricultural fraction. If unsuitable, return to block 3, move and confirm the outlet and rerun block 4. Only continue if the watershed is acceptable.

## 5. Download catchment data and convert to model inputs
Tick ACCEPT only after inspecting the watershed. The following layers are clipped to the basin and exported for GIS inspection.

| Downloaded dataset | Role |
|---|---|
| SPW SIGEC agricultural parcels (2025) | Crop labels → provisional crop C and CN, parcel IDs |
| SPW CNSW soil map | Soil interpretation only; K and HSG are not yet derived from it |
| SPW PICC roads, buildings, standing water | Infrastructure and water classes in PRC |
| SPW RHW streams | Reference and terrain conditioning; NOT the final model river raster |
| ESA WorldCover | Background forest, grass, cropland, water and built-up classes |

Final inputs: aligned conditioned DTM; exact D8 mask; PRC (positive parcel IDs and negative land-use codes, zero outside); C-factor raster with forest 0.001 and grass 0.01; provisional uniform K=30 and HSG B; CN raster; P and transport-capacity settings from tutorial; model river cells defined by contributing area ≥ MODEL_RIVER_HA. Native Idrisi exports are checked against the original D8 domain. The preview C map is not the final native C raster.

**CN extension:** the native implementation includes intensity correction `(I10/10)^alpha`, antecedent rainfall `AR5*beta` and negative rainfall excess representing potential reinfiltration. Defaults leave the first two corrections off; the negative deficit mechanism remains active. The cover/roughness CN equation is not used by the current lookup raster. Nonzero coefficients are experimental pending verification against the original thesis; AR5 is supplied in mm, not downloaded.

Event channel routing is enabled by default via ROUTE_CHANNEL_RUNOFF. This is explicit cell-to-cell D8 routing with the confirmed outlet, not native segment topology. Disable it to reproduce the earlier raster-only baseline.

### Parameter sources and assumptions

**C-factor:** the Walloon NVE manual reproduces the GISER crop lookup (Bielders et al. 2011, as cited in the manual). The teaching lookup currently uses: rapeseed 0.38, beet 0.41, cereals 0.39 (unweighted mean), maize 0.61, potatoes 0.64, flax/hemp 0.68. Grass 0.01, forest 0.001, other land 0.37 and water/infrastructure 0 are provisional teaching values associated with its other-cover table; verify the original source before scientific use. The generic crop fallback is our application of the other-land value, not a crop-specific estimate. The values are annual estimates; using them unchanged for individual storms is a teaching simplification.

**Curve Number:** USDA SCS (1986), *Urban Hydrology for Small Watersheds*, TR-55, tables 2-2a–c, reproduced by USACE HEC-HMS. HSG B and average antecedent runoff condition: CN 81 for straight-row crops in poor hydrologic condition; 76 for small grain in poor condition; 61 for pasture in good condition; 55 for woods in good condition; 98 for impervious surfaces. Applying row-crop CN 81 to every non-cereal crop and grassland CN 61 to grass strips is an analogy, not a crop-specific calibration. Open water and river CN 100 are modelling assumptions. HSG B is uniform and provisional; the soil map is not yet used to estimate HSG. The modified CN intensity and antecedent-rainfall terms are disabled by default.

**References**
- [Walloon NVE manual — Protection contre la perte en sol et l’érosion hydrique diffuse](https://natuurwaardeverkenner.marvintest.vito.be/docs/manual_FR/regulerende_diensten/Reguleren_stromen/erosie/) (GISER crop table and other-cover table).
- [USDA SCS TR-55 curve-number tables, reproduced by USACE HEC-HMS](https://www.hec.usace.army.mil/confluence/hmsdocs/hmstrm/cn-tables).
- [Panagos et al. (2015), Estimating the soil erosion cover-management factor at the European scale, Land Use Policy 48, 38–50](https://esdac.jrc.ec.europa.eu/content/cover-management-factor-c-factor-eu) — alternative European approach accounting for crop composition and management.
- [WaTEM/SEDEM model input documentation](https://watem-sedem.github.io/watem-sedem/input.html) — parameter definitions and time-scale consistency.

K and kTC remain provisional, not locally calibrated. The C and CN values are unchanged in this revision.


## 6. Run baseline simulations and inspect the model atlas
Annual erosion plus one synthetic 40 mm event. The native input atlas shows the actual model rasters; separate output atlases show erosion, sediment transport and hydrology. Total runoff is cumulative water reaching each cell in m³, not a map of independent runoff production. Event channel routing uses explicit D8 links through the native forced-routing mechanism and a manual outlet raster; the separate river-segment extension remains off. Annual settings are unchanged. The new event routing requires numerical testing and water balance verification. The sediment event response remains erosivity-based.

## 7. Export the portable GIS package
Save the ZIP locally. It contains source and derived GIS layers, data lineage and parameter records, verified native model inputs, baseline results and prepopulated management parcels and an empty grass-strip template for NB02.

## Numerical safeguards and map conventions

The outlet map uses the precomputed D8 graph and a boundary-connected flag. Yellow: 50–1000 ha; orange: >1000–5000 ha; red: >5000 ha; grey: incomplete coverage; blue: mapped RHW; purple: initial location; green: selected outlet. The basin is delineated by reverse traversal and checked against the graph count. A raster rim intersection is rejected. The 5000 ha limit is a teaching safeguard, not a model limitation.

The native inputs are repaired where necessary: exact D8 mask, full rectangular conditioned DEM, outside parcel codes zero, full-grid constant K. Input and output QA checks remain active even when diagnostics are hidden. The ZIP includes effective_model_settings.csv, data_lineage.csv, native_C_coverage.csv, parcel_parameters.csv, channel_routing_links.csv and the model atlases. Detailed console diagnostics are available by opening block 1 code and changing VERBOSE to True. The visible form intentionally omits experimental CN coefficients and routing controls.

The 40 mm synthetic event uses the existing fixed rainfall shape, 60 s routing timestep and 720 minute simulation duration; rainfall intensity and antecedent corrections default to zero. Signed rainfall excess includes potential reinfiltration deficit, not measured infiltration. Cumulative runoff is not a spatially additive water budget. Event sediment production remains erosivity-based; do not interpret it as dynamically coupled to discharge.

The reference links and parameter attribution above are inherited from the notebook; they have not been independently reverified in this editorial revision.


## Management scenarios: current implementation (NB02 and NB03)

Each named scenario is an independent perturbation of the same frozen baseline, with one annual erosion run and one 40 mm event. NB02 supports programmed selection (all fields, random parcels, high baseline erosion, or nearest model channel) and GIS upload (prepopulated management.shp with parcel IDs, crop, baseline lookup C/CN and editable c_mult and cn_delta; optional grass.shp centerlines). Programmed selection targets a cumulative polygon-area share, not an exact number of parcels; the last whole field can overshoot the target. The all-fields option ignores the percentage slider. Currently programmed targeting reads the general parcels layer, whereas the GIS template excludes mapped grass parcels; both apply changes only to positive native PRC cells. Harmonizing targeting is a development priority.

For a cell with fractional coverage f by a management polygon, its effective C multiplier is 1 + f(m−1), where m is the entered multiplier, and its CN adjustment is f times the entered delta. Multiple nonoverlapping zones contribute additively. Grass lines are buffered by half the entered total width and intersected with each eligible raster cell; overlapping strips are merged. If g is the grass fraction, final C = C_baseline × effective multiplier × (1−g) + 0.01g. CN is adjusted and clipped to 30–100, then an event-equivalent CN is obtained by inverting the conventional positive SCS runoff equation for a 40 mm event, combining the treated crop and grass (CN 61) runoff depths. This is an approximation: it does not exactly conserve the native modified CN signed deficit or routed hydrograph. Grass transport capacity is represented by a provisional harmonic blend of original kTC and grass kTC=5. It is not a calibrated trapping or connectivity model. PRC, DEM, K, routing and storm remain fixed. SOC information is descriptive only, not a causal CN model.

NB02 exports one Scenario ZIP per execution, containing the design, treated areas, summary, annual/event reports and matching baseline ID. Repeat the design and simulation blocks with unique names; do not stack interventions on the previous scenario unless deliberately encoding the combination in a new design. NB03 accepts one original baseline plus multiple completed scenario ZIPs and compares gross erosion, sediment delivered to rivers, export, event runoff volume, peak discharge, hydrographs and spatial maps. Percentage reduction = 100 × (1 − scenario/baseline); zero baseline values yield undefined reductions. The comparison uses common raster color limits and matching baseline fingerprints. The current NB03 hydrograph title says automatic outlet even when the baseline uses the explicit outlet; this label needs correction.

### Development handover — Antonin

The baseline is the more mature part of the exercise. Scenario construction and comparison remain a working prototype requiring Antonin's further development before student deployment. Priorities:

1. Run end-to-end tests of programmed and GIS scenarios, including no-change equivalence, repeated runs with unique names, grass-only and combined interventions, and NB03 multi-ZIP comparison.
2. Harmonize eligible parcel selection and area accounting; distinguish actual crop area treated from total polygon area. Add clearer intervention previews, input validation and concise student controls.
3. Establish scientifically defensible management parameter ranges and references for cover crops, residues, reduced tillage and soil structural improvement; distinguish annual C from event-specific C. Assess whether/how SOC changes can inform CN, rather than inventing a direct relationship.
4. Improve grass-strip representation: test narrow widths and orientation, review kTC=5 versus baseline low kTC=1, validate transport/trapping and runoff effects against the native implementation. Investigate explicit connectivity changes separately.
5. Define a small standard scenario set (soil management only, grass strips only, combined, and a spatial targeting contrast) with comparable treated areas and clear scientific questions. Improve NB03 metrics, outlet labels, map legends and reporting; verify water/sediment balances and interpret relative effects rather than calibrated predictions.
6. Infrastructure interventions (ponds, dams, ditches and road drainage) remain future work; do not present them as currently implemented.

See the [GIS scenario guide](LGEO2270_GIS_scenario_guide.md) for the operational workflow.
