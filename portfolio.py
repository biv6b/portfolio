import pandas as pd
import pandas_datareader.data as web
from sqlalchemy import create_engine, MetaData, Table, select
from functools import reduce

class Portfolio:
    path = "./data.sqlite3"
    def __init__(self, code, units):
        self.stocks = {}
        self.df = pd.DataFrame()
        self.engine = create_engine('sqlite:///'+Portfolio.path)
        self.db = Table('value', MetaData(), autoload=True, autoload_with=self.engine)

        for c, u in zip(code, units):
            self.stocks[c] = u
        self.loadAll()

    def __getitem__(self, code):
        return self.stocks[code]
    
    def __setitem__(self, code, units):
        self.stocks[code] = units
        
    def load(self, code):
        sql = select([self.db.c.Date, self.db.c.Close]).where(self.db.c.Code==code)
        result = pd.read_sql_query(sql, self.engine, index_col='Date', parse_dates=['Date'])

        if(len(result) == 0):
            data = web.DataReader(str(code)+'.JP', 'stooq')
            data['Code'] = code
            data.to_sql('value', self.engine, if_exists='append')

            result = data[['Close']]
        result.columns = [code]
        return result
        
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
    
if __name__ == '__main__':
    pf = Portfolio([9684], [100])
