"""Shared student reporting / raster IO for WaTEM 5.0.3. Pilot parameters, not calibration."""
from pathlib import Path
import numpy as np, pandas as pd, rasterio, matplotlib.pyplot as plt
import configparser, re, shutil, json, subprocess
from rasterio.shutil import copy as rio_copy
def read_ini(path):
    c=configparser.ConfigParser(interpolation=None); c.read(path); return c
def raster_path(c,folder,key):
    matches=[v for sec in c.sections() for k,v in c[sec].items() if k.lower()==key.lower()]
    assert len(matches)==1,(key,matches)
    return Path(folder)/Path(matches[0]).name
def read_raster(path):
    with rasterio.open(path) as ds: return ds.read(1),ds.profile.copy()
def tif_write(path,a,p,valid=None):
    p=dict(driver='GTiff',height=a.shape[0],width=a.shape[1],count=1,dtype='float32',transform=p['transform'],crs='EPSG:31370',nodata=-9999,compress='deflate')
    v=np.asarray(a,dtype='float32')
    if valid is not None: v=np.where(valid,v,-9999)
    with rasterio.open(path,'w',**p) as ds: ds.write(v,1)
def native_write(path,a,p):
    path=Path(path); tmp=path.with_name('_temp_'+path.stem+'.tif'); rst=tmp.with_suffix('.rst')
    tif_write(tmp,a,p)
    rio_copy(tmp,rst,driver='RST')
    for ext in ['.rst','.rdc']: shutil.copy2(rst.with_suffix(ext),path.with_suffix(ext))
    for ext in ['.aux.xml','.msk','.ovr']: Path(str(path)+ext).unlink(missing_ok=True)
    with rasterio.open(path) as ds: assert np.allclose(ds.read(1),a,atol=1e-5) and ds.transform.almost_equals(p['transform'])
    for f in [tmp,rst,rst.with_suffix('.rdc'),Path(str(rst)+'.aux.xml')]: f.unlink(missing_ok=True)
def report(folder,mode,rain_mm=None):
    folder=Path(folder); inp=folder/'modelinput'; out=folder/'modeloutput'; result=folder/'report'; result.mkdir(exist_ok=True)
    cfg=read_ini(inp/'inifile.ini'); prc,p=read_raster(raster_path(cfg,inp,'Parcel filename')); mask=prc!=0; res=abs(p['transform'].a); area=mask.sum()*res**2/10000
    t=(out/'Total sediment.txt').read_text()
    vals=[float(re.search(k+r'\s*([-+\d.]+)',t).group(1)) for k in ['Total erosion:','Total deposition:','Sediment leaving the catchment, via the river:','Sediment leaving the catchment, not via the river:']]
    e,d,river,other=-vals[0]/1000,vals[1]/1000,vals[2]/1000,vals[3]/1000
    row=dict(mode=mode,area_ha=area,erosion_t=e,deposition_t=d,river_t=river,other_export_t=other,export_t=river+other,erosion_t_ha=e/area,river_t_ha=river/area,delivery_ratio_pct=100*(river+other)/max(e,1e-12),mass_residual_t=e-d-river-other,mass_pass=abs(e-d-river-other)<=max(.0001,.02*e))
    for native,name,scale in [('WATEREROS (kg per gridcel).rst','erosion_t_ha',10/res**2),('SediIn_kg.rst','sediment_in_t',.001),('SediExport_kg.rst','sediment_export_t',.001),('RUSLE.rst','potential_erosion_t_ha',10),('SLOPE.rst','slope_deg',180/np.pi),('UPAREA.rst','effective_uparea_ha',.0001),('Remap.rst','rainfall_excess_signed_mm',1)]:
        if (out/native).exists():
            a,_=read_raster(out/native); valid=mask & np.isfinite(a) & (a!=-9999); tif_write(result/(name+'.tif'),a*scale,p,valid)
            if native=='Remap.rst':
                tif_write(result/'local_runoff_mm.tif',np.maximum(a,0),p,valid)
                row['gross_runoff_m3']=float(np.maximum(a[valid],0).sum()*res**2/1000)
    for key,name in [('C factor map filename','C_factor'),('CN map filename','CN'),('K factor filename','K_factor'),('ktc map filename','kTC'),('Parcel filename','PRC'),('DTM filename','DEM')]:
        try: a,_=read_raster(raster_path(cfg,inp,key))
        except (AssertionError,FileNotFoundError,rasterio.errors.RasterioIOError): continue
        tif_write(result/(name+'.tif'),a,p,None if name=='DEM' else mask)
    if mode.startswith('event'):
        def numeric(df): return df.apply(lambda s:pd.to_numeric(s.astype(str).str.replace(',','.',regex=False),errors='raise'))
        q=pd.read_csv(out/'Discharge.txt',sep='\t',skiprows=1).dropna(axis=1,how='all'); total=pd.read_csv(out/'Total discharge.txt',sep='\t',skiprows=1).dropna(axis=1,how='all')
        time=q.columns[0]; q=numeric(q); total=numeric(total)
        assert q.shape[1]==2,'Pilot reporting expects one automatic outlet'
        sec=q.iloc[:,0].to_numpy()*(60 if 'min' in time.lower() else 1); flow=q.iloc[:,1].to_numpy(); vol=float(total.iloc[0,1]); dt=float(np.median(np.diff(sec)))
        assert np.allclose(np.diff(sec),dt) and (flow>=-1e-8).all()
        row.update(rain_mm=rain_mm,runoff_m3=vol,runoff_mm=vol/(area*10),runoff_pct=100*vol/(rain_mm*area*10),peak_m3_s=float(flow.max()),peak_time_min=float(sec[flow.argmax()]/60),tail_m3_s=float(flow[-1]),hydro_integral_m3=float(flow.sum()*dt),hydro_pass=bool(np.isclose(flow.sum()*dt,vol,rtol=1e-4,atol=.01)))
        pd.DataFrame(dict(time_min=sec/60,discharge_m3_s=flow)).to_csv(result/'hydrograph.csv',index=False)
        fig,ax=plt.subplots(figsize=(9,4)); ax.plot(sec/60,flow); ax.set(xlabel='Time (min)',ylabel='Discharge (m³/s)',title='Reported automatic outlet'); fig.savefig(result/'hydrograph.png',dpi=160); plt.show()
    pd.DataFrame([row]).to_csv(result/'summary.csv',index=False)
    a,_=read_raster(result/'erosion_t_ha.tif'); valid=mask & (a!=-9999); lim=max(float(np.percentile(np.abs(a[valid]),98)),.01)
    fig,ax=plt.subplots(figsize=(7,6)); im=ax.imshow(np.ma.masked_where(~valid,a),cmap='RdBu',vmin=-lim,vmax=lim); rr,cc=np.where(prc==-1); ax.scatter(cc,rr,s=3,c='navy'); ax.set_title(mode+' redistribution (t/ha)'); fig.colorbar(im,ax=ax); fig.savefig(result/'erosion.png',dpi=160); plt.show()
    assert row['mass_pass'],row
    return row
def clone_run(source,dest,binary,rain_mm=None):
    source,dest=Path(source),Path(dest); assert not dest.exists(),dest
    inp=dest/'modelinput'; out=dest/'modeloutput'; shutil.copytree(source/'modelinput',inp); out.mkdir()
    cfg=read_ini(inp/'inifile.ini'); cfg['Working directories']['Input directory']=str(inp); cfg['Working directories']['Output directory']=str(out)
    for sec in cfg.sections():
        if sec.lower()=='working directories': continue
        for k,v in list(cfg[sec].items()):
            if (inp/Path(v).name).is_file() and v: cfg[sec][k]=Path(v).name
    if rain_mm is not None:
        r=np.array([0,2,4,7,9,8,5,3,2,0],float)*rain_mm/40
        rain=raster_path(cfg,inp,'Rainfall filename'); np.savetxt(rain,np.column_stack([np.arange(len(r))*10,r]),fmt=['%d','%.6f'],delimiter='\t')
        intensity=r[1:]*6; R=float(np.sum(.29*(1-.72*np.exp(-.05*intensity))*r[1:])*np.max(np.convolve(r[1:],np.ones(3),'valid'))*2)
        cfg['Parameters']['R factor']=str(R)
    with (inp/'inifile.ini').open('w') as f: cfg.write(f)
    return cfg,inp,out
def execute(dest,binary):
    dest=Path(dest); p=subprocess.run([str(binary),str(dest/'modelinput/inifile.ini')],capture_output=True,text=True,errors='replace',cwd=dest)
    (dest/'model.log').write_text(p.stdout+'\n'+p.stderr); p.check_returncode()
