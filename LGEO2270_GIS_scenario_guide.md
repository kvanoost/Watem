# LGEO2270 — GIS scenario quick guide

## 1. Open your baseline
Keep the original Baseline ZIP unchanged. Extract a working copy. In QGIS or ArcGIS Pro, add:
- reference/catchment.shp and reference/river.shp
- baseline_results/annual/erosion_t_ha.tif
- editable_scenario/management.shp and editable_scenario/grass.shp

The management layer already contains SIGEC agricultural parcel polygons (excluding parcels classified as grass in the baseline). No copying or drawing fields is needed.

## 2. Edit the parcel attributes
Open the management layer attribute table. Enable editing (QGIS pencil icon; ArcGIS Pro Edit tab). Select the parcels you wish to treat. Change only the last two attributes:

| Field | Meaning | Example |
|---|---|---|
| parcel_id | Original parcel identifier; do not edit | 12 |
| crop | Baseline crop label; do not edit | Maize |
| c_base | Baseline crop lookup C; informational | 0.61 |
| cn_base | Baseline crop lookup CN; informational | 81 |
| c_mult | C multiplier (0–1); default 1 | 0.6 = 40% lower C |
| cn_delta | CN adjustment (−20 to 0); default 0 | −5 = five points lower |

Use the field calculator on selected rows to set the same value for several parcels. Leave untreated parcels unchanged. Do not delete rows, change IDs or edit the geometry. Save edits. Baseline lookup values are informational; actual raster adjustments use the native model inputs. Examples are sensitivity assumptions, not calibrated effects.

## 3. Optional grass strips
Select grass.shp and start editing. Use Add Line Feature (QGIS) or Create Features (ArcGIS Pro) to draw a centreline along a field margin, stream or across a slope. Enter width_m between 1 and 40 m (total width). Save edits. Only the fraction intersecting eligible model cropland is treated. An empty grass layer is fine.

## 4. Run NB02
Save edits and stop editing. ZIP the entire editable_scenario folder, including .shp, .shx, .dbf, .prj and any .cpg files.
Open [NB02 in Colab](https://colab.research.google.com/github/kvanoost/Watem/blob/main/Watem_NB02_Management_scenarios.ipynb).
Upload the unchanged original Baseline ZIP first. Enter a unique scenario name, choose GIS upload and upload your edited ZIP. Check the design maps, tick ACCEPT and run. Save the Scenario ZIP. Repeat with other designs, then compare with [NB03](https://colab.research.google.com/github/kvanoost/Watem/blob/main/Watem_NB03_Compare_evalaution.ipynb).

Older baseline ZIPs contain empty C_change.shp and CN_change.shp polygon templates instead. NB02 still accepts those legacy layers with their original fields c_mult and cn_delta, but do not mix them with management.shp. To obtain the new prepopulated layer without repeating simulations, rerun the updated NB01 export block 7 in the original runtime if it is still available.

[Model methodology](LGEO2270_Model_methodology.md)
