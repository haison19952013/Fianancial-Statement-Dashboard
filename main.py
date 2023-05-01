import yfinance as yf
import streamlit as st
import yahooquery as yq
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class balance_sheet_analysis():
    def __init__(self,tickerData, frequency="a"):
        self.balance_sheet_df = tickerData.balance_sheet(frequency=frequency)
        self.preprocess()
    
    def preprocess(self):
        def format_year(year):
            return '{:.0f}'.format(year)
        df = self.balance_sheet_df
        df['asOfDate'] = pd.to_datetime(df['asOfDate'])
        df['asOfDate'] = df['asOfDate'].dt.year
        df['asOfDate'] = df['asOfDate'].apply(format_year)
        self.balance_sheet_df = df
    
    def extract_metrics(self):
        df  = self.balance_sheet_df
        # Calculate Debt-to-equity = Total Liabilities / Total Shareholders Equity (Stockholders Equity)
        Total_liabilities = df['TotalAssets'].values - df['StockholdersEquity'].values
        Debt_2_equity = Total_liabilities / df['StockholdersEquity'].values
        df['Debt_2_equity'] = Debt_2_equity.tolist()

        # Calculate current ratio = Current asset/ Current debt
        df['Current_ratio'] = df['CurrentAssets'].values / df['CurrentDebt'].values

        # Asset Turnover Rate = Total Sales / (Beginning Assets + Ending Assets)/2

        # Inventory Turnover Rate = Costs of goods solds / (Beginning Inventory + Ending Inventory)/2

        # Assets Growth = Total Assets (year) -  Total Assets (year - 1) / Total Assets (year) * 100%
        df['Assets_growth'] = df['TotalAssets'].pct_change() * 100

        # Stockholders Equity Growth = Stockholders Equity (year) -  Stockholders Equity (year - 1) / Stockholders Equity (year) * 100%
        df['StockholdersEquity_growth'] = df['StockholdersEquity'].pct_change() * 100

        self.balance_sheet_df = df
    
    def plot(self,x,y,xlabel,ylabel,kind = 'line'):
        df = self.balance_sheet_df
        # Plot data
        (fig, ax) = plt.subplots(1, 1, figsize=(10, 8))
        # Create a plot
        df.plot(x = x, y = y, kind = kind,ax = ax)
        ax.set_xlabel(xlabel, fontsize=16)
        ax.set_ylabel(ylabel, fontsize=16)
        ax.tick_params(labelsize=12)
        ax.grid(True)
        return fig

def load_symbol_name():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    html = pd.read_html(url, header = 0)
    df = html[0]
    return tuple(df['Symbol'].values.tolist())

symbol_tuple = load_symbol_name()


#define the ticker symbol
tickerSymbol = st.selectbox(label = 'Ticker Symbol of the analyzed company', options = symbol_tuple)
# tickerSymbol = 'XOM'
longname = yf.Ticker(tickerSymbol).info["longName"]
st.title('Finanicial Statement Analsysis For %s (%s)' % (longname, tickerSymbol))


# Get data and extract metrics
tickerData = yq.Ticker(tickerSymbol)

st.header('1. Balance Sheet Analysis')
balance_sheet = balance_sheet_analysis(tickerData)
balance_sheet_df = balance_sheet.balance_sheet_df
balance_sheet.extract_metrics()

# Ask for displaying raw data
with st.container():
    show_data = st.checkbox("Do you want to see the full table of balance sheet data?")
    if show_data:
        balance_sheet_df

# Analyze financial health
st.subheader('1.1 Financial Health')
st.write('- Debt-to-Equity = Total Liabilities / Total Shareholders Equity (Stockholders Equity)')
fig = balance_sheet.plot(x = 'asOfDate', y = 'Debt_2_equity', xlabel='Year',ylabel='Debt-to-Equity',kind = 'bar')
st.pyplot(fig)

st.write('- Current Ratio = Current Assets / Current Debt')
fig = balance_sheet.plot(x = 'asOfDate', y = 'Current_ratio', xlabel='Year',ylabel='Current Ratio',kind = 'bar')
st.pyplot(fig)

# Analyze asset utilization
st.subheader('1.2 Asset Utilization')
st.write('- Asset Turnover Rate = Total Sales / (Beginning Assets + Ending Assets)/2')
st.write('- Inventory Turnover Rate = Costs of goods solds / (Beginning Inventory + Ending Inventory)/2')

# Analyze bussiness growth
st.subheader('1.3 Bussiness Growth')
st.write('- Assets Growth = Total Assets (year) -  Total Assets (year - 1) / Total Assets (year) * 100%')
fig = balance_sheet.plot(x = 'asOfDate', y = 'Assets_growth', xlabel='Year',ylabel='Assets Growth (%)',kind = 'bar')
st.pyplot(fig)

st.write('- Stockholders Equity Growth = Stockholders Equity (year) -  Stockholders Equity (year - 1) / Stockholders Equity (year) * 100%')
fig = balance_sheet.plot(x = 'asOfDate', y = 'StockholdersEquity_growth', xlabel='Year',ylabel='Stockholders Equity Growth  (%)',kind = 'bar')
st.pyplot(fig)

st.header('2. Income Statement')
st.header('3. Cash Flow')


