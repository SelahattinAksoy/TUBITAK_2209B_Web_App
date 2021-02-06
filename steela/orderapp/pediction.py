import pandas as pd
from io import StringIO
from datetime import date
import numpy as np

def selo():
    period=106

    rng = pd.date_range('20190731', periods=period)
    #df = pd.DataFrame({'date': rng})  
    
    from random import seed
    from random import randint
    # seed random number generator
    seed(1)#bu alınan değeri sabit tutuyo bunu yapmazsan her run edince değer değişir
    # generate some integers
    numbers=[]
    for _ in range(period):
    value = randint(5, 16)
    numbers.append(value)

    #df["order"]=x
    df=pd.read_csv("static/csv/selo.csv")

    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)


    df.plot(figsize=(20,10))
    # Plot a 30 day moving average
    df.rolling(window=30).mean()['new_deaths_per_million'].plot()