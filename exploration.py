import pandas as pd
from datetime import datetime

with open('tracklogs/meta_data.csv') as fp:
    df = pd.read_csv(fp)

df['dateCreated'] = df['dateCreated'].apply(datetime.fromtimestamp)
missing = df[df['tailNumber'].isna()]
nonx = missing[missing['initialGPSSource'] != 'X-Plane']
nonx['dateCreated']