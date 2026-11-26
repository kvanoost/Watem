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


## 5. Construct several independent scenarios

The aim is to compare the effects of interventions, not simply find the scenario giving the largest reduction. Keep the original baseline ZIP as the common reference for every run. Start each GIS design from a fresh copy of the original editable_scenario folder. In programmed mode, change the controls directly instead.

The following is a proposed exercise, to be finalized by Antonin. The numbers are illustrative sensitivity settings, not validated effects of particular agricultural practices.

| Scenario name | Design | Example settings | Question |
|---|---|---|---|
| S01_soil | Improved management of selected high-erosion parcels | Target 25% of parcel area; C multiplier 0.6; CN delta −5; no grass strips | How does reducing erosion susceptibility and runoff potential affect the basin? |
| S02_grass | Grass strips only | C multiplier 1; CN delta 0; e.g. 6 m strips beside channels or at downslope field margins | Can strategic interception reduce delivery to rivers? |
| S03_combined | Same soil treatment as S01 and same strips as S02 | Combine the two designs in a fresh copy of the baseline templates | Are their effects complementary? |
| S04_targeting | Alternative spatial placement of the soil treatment | Same C and CN changes and approximately the same treated crop area as S01, but different parcels (e.g. random or near river) | Does placement matter as much as treated area? |

For programmed mode, the grass-width control generates strips centered along the model river network, not arbitrary field margins. Use GIS mode for explicit field-margin locations. The percentage slider targets the cumulative area of whole parcels, so achieved treatment can differ slightly from the requested percentage. The all-cropland option ignores the slider; actual raster treatment is restricted to eligible positive parcel-code cells. For fair comparisons inspect the reported effective treatment areas.

### Running and saving
- Upload the original Baseline ZIP once in NB02 block 1.
- Set a unique scenario name in block 2; choose Programmed or GIS upload. In GIS mode upload the design ZIP for that scenario. Inspect the C multiplier, CN adjustment and grass-fraction maps.
- Tick ACCEPT in block 3 and run. Each run clones the original baseline inputs, executes the annual and 40 mm event modes, and downloads a Scenario ZIP.
- Repeat blocks 2 and 3 for the next scenario. If the runtime has restarted, upload the original baseline again. Keep the individual ZIPs. Do not overwrite or use a previous scenario as the baseline.
- Open NB03 and upload the original Baseline ZIP and all completed Scenario ZIPs together. SELECT=all compares all scenarios; alternatively enter comma-separated names. Save the comparison ZIP.

### Interpretation

Compare gross erosion, sediment delivery to channels and catchment export separately. A measure that reduces sediment delivery need not reduce gross erosion by the same amount. For the storm, examine runoff volume and peak discharge as well as hydrograph shape. Compare treated areas and locations, not just percentage reductions. Note that cumulative runoff maps cannot be summed into a water budget. The model is a teaching sensitivity exercise and is not locally calibrated.

## 6. Development note — Antonin

**NB02/NB03 and this proposed exercise need further development by Antonin before student deployment.** The baseline workflow is more mature; the scenario examples above are starting points. Antonin should test both input modes, verify no-change equivalence and multi-scenario exports/comparison, harmonize crop eligibility and area accounting, validate the grass-width and trapping representation, and establish defensible parameter assumptions. The final assignment should specify which scenarios are compulsory, what students may vary and what figures and discussion they must deliver. Infrastructure changes are not implemented yet. The [technical methodology](LGEO2270_Model_methodology.md) provides the detailed handover and equations.
