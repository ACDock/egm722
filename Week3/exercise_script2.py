import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches


# ---------------------------------------------------------------------------------------------------------------------
# in this section, write the script to load the data and complete the main part of the analysis.
# try to print the results to the screen using the format method demonstrated in the workbook

# load the necessary data here and transform to a UTM projection
counties = gpd.read_file('data_files/Counties.shp')
wards = gpd.read_file('data_files/NI_Wards.shp')
counties.to_crs(epsg=32629)
wards.to_crs(epsg=32629)

# your analysis goes here...
join = gpd.sjoin(counties, wards, how='inner', lsuffix='left', rsuffix='right')

print(join.groupby(['CountyName'])['Population'].sum())

clipped = []
for county in counties['CountyName'].unique():
    tmp_clip = gpd.clip(wards, counties[counties['CountyName'] == county])
    for ind, row in tmp_clip.iterrows():
        tmp_clip.loc[ind, 'CountyName'] = county
    clipped.append(tmp_clip)

clipped_gdf = gpd.GeoDataFrame(pd.concat(clipped))

wards_total = wards['Ward'].count()
clipped_wards_total = clipped_gdf['Ward'].count()
print('Total number of wards in original file:', wards_total)
print('Total number of wards in clipped file:', clipped_wards_total)

ward_popl = wards['Population'].sum()
clipped_ward_popl = clipped_gdf['Population'].sum()
print('Total population in original wards file: ', ward_popl)
print('Total population in clipped file: ', clipped_ward_popl)

ward_popl_max = wards[['Ward', 'Population']][wards.Population == wards['Population'].max()]
ward_popl_min = wards[['Ward', 'Population']][wards.Population == wards['Population'].min()]
print('The Ward highest population is: ', ward_popl_max)
print('The Ward lowest population is: ', ward_popl_min)

# ---------------------------------------------------------------------------------------------------------------------
# below here, you may need to modify the script somewhat to create your map.
# create a crs using ccrs.UTM() that corresponds to our CRS
myCRS = ccrs.UTM(29)
# create a figure of size 10x10 (representing the page size in inches
fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection=myCRS))

# add gridlines below
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5],
                         ylocs=[54, 54.5, 55, 55.5])
gridlines.right_labels = False
gridlines.bottom_labels = False

# to make a nice colorbar that stays in line with our map, use these lines:
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1, axes_class=plt.Axes)

# plot the ward data into our axis, using
ward_plot = wards.plot(column='Population', ax=ax, vmin=1000, vmax=8000, cmap='viridis',
                       legend=True, cax=cax, legend_kwds={'label': 'Resident Population'})

county_outlines = ShapelyFeature(counties['geometry'], myCRS, edgecolor='r', facecolor='none')

ax.add_feature(county_outlines)
county_handles = [mpatches.Rectangle((0, 0), 1, 1, facecolor='none', edgecolor='r')]

ax.legend(county_handles, ['County Boundaries'], fontsize=12, loc='upper left', framealpha=1)

# save the figure
fig.savefig('Prac3_map.png', dpi=300, bbox_inches='tight')
