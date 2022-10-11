import csv
import pandas as pd
from datetime import datetime
from scipy.signal import savgol_filter
from matplotlib import pyplot as plt

INFILE = 'flight_circle.csv'

with open(INFILE) as fp:
    data = [i for i in csv.DictReader(fp)]

aircraft = []
for row in data:
    if 'Aircraft' in row['What'] and 'Special Assessment' not in row['What']:
        entry = {'date': datetime.strptime(row['Date'], '%m/%d/%Y'),
                 'tach': float(row['Quantity']),
                 'cost': float(row['Charge'].replace('$', ''))}
        aircraft.append(entry)

window = 90
df = pd.DataFrame(aircraft).groupby('date').sum()  # Needed when multiple flights in a day
idx = pd.date_range(min(df.index), max(df.index))
df = df.reindex(idx, fill_value=0)
rolling = df.rolling(f"{window}D").sum()


def run(size, order):
    if size % 2 == 0:
        size += 1
        print(f"Using size {size} instead to make odd")

    # https://stackoverflow.com/questions/20618804/how-to-smooth-a-curve-in-the-right-way
    yhat = savgol_filter(rolling.cost, size, order)
    plt.plot(rolling.index, rolling.TotalTime, '-o')
    plt.plot(rolling.index, yhat, '-')
    plt.show()


run(279, 5)  # Looks reall good with a 90 day window!


# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.resample.html
df.resample('Q', convention='end').agg('sum')
