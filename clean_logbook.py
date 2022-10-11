import csv
import pandas as pd
from matplotlib import pyplot as plt
from scipy.signal import savgol_filter
from datetime import datetime

with open('logbook_2021-12-02_20 38 56.csv') as fp:

    # skip log summary for ForeFlight
    while 'Flights Table' not in fp.readline():
        continue

    data = [row for row in csv.DictReader(fp)]

df = pd.DataFrame(data)
df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')
df = df[['Date', 'TotalTime']]
df.TotalTime = pd.to_numeric(df.TotalTime)
df = df.groupby('Date').sum()
idx = pd.date_range(min(df.index), datetime.now()) # make max today
df = df.reindex(idx, fill_value=0)


def run(size, order):
    if size % 2 == 0:
        size += 1
        print(f"Using size {size} instead to make odd")

    # https://stackoverflow.com/questions/20618804/how-to-smooth-a-curve-in-the-right-way
    yhat = savgol_filter(rolling.TotalTime, size, order)
    plt.plot(rolling.index, rolling.TotalTime, '-o')
    plt.plot(rolling.index, yhat, '-')


for window in [30, 60, 90]:
    rolling = df.rolling(f"{window}D").sum() # rename, or assign elsewhere to new column
    run(279, 5)

