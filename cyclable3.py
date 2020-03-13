# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 17:26:53 2020

@author: andre
"""
import pandas as pd
import json
from pandas.io.json import json_normalize
import matplotlib.pyplot as plt
import folium
import seaborn as sns

##############################################################################'Stamen Toner'
def plot_map(df,filename):
    maps=[]
    maps = folium.Map(location=[ 48.857082, 2.344875],tiles='CartoDB dark_matter',zoom_start=13)
    for i in df.index:
    
        coord = df['geo_shape.coordinates'][i]
        location =[ (c[1],c[0]) for c in coord] 
        folium.vector_layers.PolyLine(locations=location,color=df.colors[i], weight=2.5, opacity=1).add_to(maps)
        
    maps.save(filename+'.html')

##############################################################################

# Read the database
df = pd.read_json('reseau-cyclable.json')

# Flat the data and remove row 677 THAT IS ONLY NULL VALUES
df_flat=json_normalize(df.fields)
df_flat.drop([677],inplace=True)
df_flat.reset_index(drop=True,inplace=True)


# get types and associate with colors
types= list (df_flat.typologie_simple.unique())
colors = ['orange','green','red','blue']
color_types ={types[i]:colors[i] for i in range(len(types))}
df_flat['colors']=df_flat['typologie_simple'].map(color_types)

# ajusting the year column and index
no_date_mask = df_flat.date_de_livraison.isna()
df_flat.date_de_livraison = df_flat.date_de_livraison.map(pd.Timestamp)
df_flat['Year'] = df_flat['date_de_livraison'].dt.year
df_flat['Year'].fillna(0,inplace=True)
df_flat['Year']=df_flat['Year'].astype('int32')

###############################################################################

# preparing variables for plot
stacks = df_flat.pivot_table(values ='longueur_du_troncon_en_km', index='Year',columns='typologie_simple',aggfunc=sum)
stacks.columns = [t.split('(')[0] for t in stacks.columns]

# set base map with define style and zoom

plot_map(df_flat,'Total_map')

plot_map(df_flat[no_date_mask],'Before2000_map')

plot_map(df_flat[ (df_flat['Year']>=2005) & (df_flat['Year']<=2006) ],'2005_2006_map')

plot_map(df_flat[ (df_flat['Year']>=2008) & (df_flat['Year']<=2014) ],'2008_2014_map')

plot_map(df_flat[ (df_flat['Year']>=2015) & (df_flat['Year']<=2019) ],'2015_2019_map')

###########

plot_map(df_flat[ (df_flat['typologie_simple']>=types[0]) & (df_flat['typologie_simple']<=types[0]) ],'type1_map')

plot_map(df_flat[ (df_flat['typologie_simple']>=types[1]) & (df_flat['typologie_simple']<=types[1]) ],'type2_map')

plot_map(df_flat[ (df_flat['typologie_simple']>=types[2]) & (df_flat['typologie_simple']<=types[2]) ],'type3_map')

plot_map(df_flat[ (df_flat['typologie_simple']>=types[3]) & (df_flat['typologie_simple']<=types[3]) ],'type4_map')



## Ploting  stacked bars

fs=16
_, ax=plt.subplots()
stacks.iloc[2:,::-1].plot(kind='bar',stacked=True,figsize=(15, 10), fontsize=fs,ax=ax)
plt.xlabel('Year',fontsize=fs)
plt.ylabel('Total delivered (km)',fontsize=fs)
plt.title('The length of the cycle network delivered by year' ,fontsize=fs)
