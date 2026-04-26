import geopandas as gpd
import pandas as pd

# ── 1. Charger les deux fichiers ──────────────────────────────────
gdf_arr = gpd.read_file("arrondissements_mtl.geojson")
gdf_ct  = gpd.read_file("ct2021_qc.geojson")

# ── 2. Filtrer Montréal seulement ─────────────────────────────────
gdf_ct_mtl = gdf_ct[gdf_ct['CTUID'].str.startswith('462')].copy()
print(f"Census tracts Montréal : {len(gdf_ct_mtl)}")  # 1004

# ── 3. Harmoniser les CRS (tout en WGS84) ─────────────────────────
gdf_arr    = gdf_arr.to_crs("EPSG:4326")
gdf_ct_mtl = gdf_ct_mtl.to_crs("EPSG:4326")

# ── 4. Spatial join : centroïde de chaque CT → arrondissement ─────
gdf_ct_mtl['geometry'] = gdf_ct_mtl.geometry.centroid

ct_with_arr = gpd.sjoin(
    gdf_ct_mtl[['CTUID', 'geometry']],
    gdf_arr[['NOM', 'geometry']],
    how='left',
    predicate='within'
)

print(ct_with_arr[['CTUID', 'NOM']].head(10))
print(f"\nCT sans arrondissement : {ct_with_arr['NOM'].isna().sum()}")

# ── 5. Table de correspondance CTUID → Arrondissement ─────────────
correspondance = ct_with_arr[['CTUID', 'NOM']].rename(
    columns={'NOM': 'arrondissement'}
)
correspondance.to_csv("ctuid_to_arrondissement.csv", index=False)
print("✅ Table de correspondance sauvegardée")