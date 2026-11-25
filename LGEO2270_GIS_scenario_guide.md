# LGEO2270 — GIS scenario quick guide

**Goal:** design a management scenario for the same watershed as NB01. No new geographical downloads are needed.

## 1. Open your baseline in QGIS
1. Keep the original NB01 Baseline ZIP unchanged. Extract a working copy.
2. Start QGIS. Drag reference/parcels.shp, reference/catchment.shp, reference/river.shp and baseline_results/annual/erosion_t_ha.tif into the map. Optionally add reference/dtm.tif.
3. Add the empty shapefiles in editable_scenario/ (C_change.shp, CN_change.shp, grass.shp). These are your editable layers. All use Belgian Lambert 72 (EPSG:31370). An ESRI shapefile consists of several files: keep .shp, .shx, .dbf, .prj and any .cpg together.

## 2. Design interventions
| Layer | Geometry | Required field | Example |
|---|---|---|---|
| C_change.shp | Polygon | c_mult (0–1) | 0.6 = 40% lower C |
| CN_change.shp | Polygon | cn_delta (−20 to 0) | −5 = subtract five CN points |
| grass.shp | Line | width_m (1–40 m) | 6 = total width 6 m (3 m either side) |

All other template fields (id, practice, years, comments, SOC etc.) are descriptive; SOC does not automatically determine CN. Use unique IDs for documentation. Choose defensible assumptions; examples are sensitivity tests, not calibrated practice effects.

### A. Change individual fields (QGIS)
- Select reference/parcels in the Layers panel. Use Select Features to select one or several fields (Ctrl/Shift selection as appropriate). Copy selected features (Ctrl+C).
- Select C_change, toggle editing (pencil), paste (Ctrl+V). If QGIS requests field mapping, map geometry and leave unmatched attributes empty.
- Open its attribute table and enter c_mult for each new feature. Save edits and stop editing.
- Repeat for CN_change if desired, filling cn_delta instead.
- Alternatively use Add Polygon Feature in either editable polygon layer to draw part of a field or a management zone spanning several fields. Zones may not overlap within the same layer. C and CN layers may overlap each other.
- If copy/paste between different schemas fails, digitize the polygons using parcel snapping or use QGIS Processing 'Refactor fields' to export selected parcels with exactly the template field names, then replace the corresponding shapefile in the working scenario folder.

### B. Add grass strips
- Select grass, toggle editing and choose Add Line Feature.
- Click vertices along a field margin, stream, or across a slope. Right-click to finish the line.
- Enter width_m (e.g. 6), optionally type and comment. Save and stop editing.
- Width is total width; buffer is centered on the line. Only the portion intersecting eligible model cropland cells contributes to the intervention. A narrow strip does not automatically become a full 20 m grass cell.

### ArcGIS Pro equivalent
Add the same layers to a map. Select fields in parcels, then use Edit > Copy and Paste Special into the chosen editable polygon layer (or digitize with Create Features and snapping). Set attributes in the target layer and save edits. For grass use Create Features > grass line template; enter width_m and save. Do not change the schema or CRS.

## 3. Upload to NB02
1. Save all edits and exit editing mode. ZIP only the editable_scenario folder (including the component files of all shapefiles); do not ZIP just the .shp files. Empty unused templates can remain. The importer recognizes exact names C_change.shp, CN_change.shp and grass.shp.
2. Open [NB02 in Colab](https://colab.research.google.com/github/kvanoost/Watem/blob/main/Watem_NB02_Management_scenarios.ipynb).
3. Upload the original unchanged Baseline ZIP in the first code block.
4. Enter a unique scenario name, select GIS upload, run the design block and upload the new editable_scenario ZIP.
5. Check the three intervention maps and treated areas. Tick ACCEPT, run the simulation and download the Scenario ZIP.
6. Repeat for other designs, always using the same baseline. Use [NB03](https://colab.research.google.com/github/kvanoost/Watem/blob/main/Watem_NB03_Compare_evalaution.ipynb) to compare the baseline and scenario ZIPs.

## Example
Copy three high-erosion fields into C_change and assign c_mult=0.6, then copy the same fields into CN_change and assign cn_delta=−5. Draw a 6 m grass strip on their downslope boundary. Save and ZIP. This is a combined scenario. To isolate effects, run separate soil-only and grass-only scenarios too.

## Important
NB02 alters only eligible positive parcel-code cells, not all polygons regardless of baseline land use. Partial coverage is accounted for. Keep reference layers and native baseline inputs unchanged. No overlapping polygons within each adjustment layer; no missing required numeric attributes. The programmed mode is a simpler alternative if GIS editing is not needed. See [model methodology](LGEO2270_Model_methodology.md) for assumptions.
