import pandas as pd
import pandas_datareader.data as web
from functools import reduce

class Portfolio:
    path = "./data/"
    def __init__(self, code, units):
        self.stocks = {}
        self.df = pd.DataFrame()
        self.since = 2015
        self.to = 2020

        for c, u in zip(code, units):
            self.stocks[c] = u
        self.loadAll()

    def __getitem__(self, code):
        return self.stocks[code]
    
    def __setitem__(self, code, units):
        self.stocks[code] = units
        
    def load(self, code):
        data = web.DataReader(str(code)+'.JP', 'stooq')
        close = data[['Close']]
        close.columns = [code]
        return close
        
    def loadAll(self):
        p = []
        for code in self.stocks.keys():
            data = self.load(code)
            p.append(data)
        self.df = reduce(lambda x, y: x.join(y, how='inner'), p)
       
    def add(self, code, units):
        if code not in self.stocks.keys():
            data = self.load(code)
            self.df = self.df.join(data, how='inner')
        self.stocks[code] = units

    def remove(self, code):
        try:
            del self.stocks[code]
        except KeyError:
            print('does not exist')
        else:
            self.df.drop(code, axis=1, inplace=True)
        
    def plot(self, _figsize=(16,4), _legend=False):
        self.df.plot(figsize=_figsize, legend=_legend)

    def subplots(self, _figsize=(16,3)):
        fs = _figsize[0], _figsize[1]*len(self.stocks)
        self.df.plot(figsize=fs, subplots=True)
        
    def total(self, _figsize=(16,4), _legend=False):
        value = self.df * list(self.stocks.values())
        value.sum(axis=1).plot(figsize=_figsize, legend=_legend)


def nikkei():
    data = web.DataReader('^NKX', 'stooq')
    close = data[['Close']]
    close.columns = ['Nikkei225']
    return close
    
    
