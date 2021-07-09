import dash_html_components as html
from datetime import datetime

def getStockTable(df, stock_info):
    '''
    GENERATE STOCK INFORMATION TABLE
    '''

    last_day = df.iloc[-1,1:6]

    # OPEN PRICE
    last_open_price = last_day['Open']
    last_open_price = f'{last_open_price:,.2f}'

    # FORMAT THE DAY RANGE OF PRICE
    low_day = last_day['Low']
    high_day = last_day['High']
    range_day = f'{low_day:,.2f}'+' - '+f'{high_day:,.2f}'

    # OBTAIN AND FORMAT 52 WEEKS RANGE OF PRICE
    low_52weeks = df['Low'].min()
    high_52weeks = df['High'].max()
    range_52weeks = f'{low_52weeks:,.2f}'+' - '+f'{high_52weeks:,.2f}'

    # FORMAT VOLUMNE AND AVERAGE VOLUME
    vol = last_day['Volume']
    vol = f'{vol:,.0f}'
    avg_vol = stock_info['averageVolume10days']
    avg_vol = f'{avg_vol:,.0f}'

    # OBTAIN SHARES OUTSTANDING
    shareOutstanding = stock_info['sharesOutstanding']

    # CALCULATE MARKET CAP AND FORMAT IT
    mktcap = last_day['Close']*shareOutstanding
    mktcap = f'{mktcap:,.0f}'

    # FORMAT BETA
    if 'beta' in stock_info and stock_info['beta'] is not None:
        beta = stock_info['beta']
        beta = f'{beta:.2f}'
    else:
        beta = 'N/A'

    # FORMAT PE AND FORWARD PE, IF NO PE, PE NOT IN THE DICTIONARY
    if 'trailingPE' in stock_info:
        pe = stock_info['trailingPE']
        pe = f'{pe:.2f}'
    else:
        pe = 'N/A'
    if 'forwardPE' in stock_info and stock_info['forwardPE'] != None:
        fpe = stock_info['forwardPE']
        fpe = f'{fpe:.2f}'
    else:
        fpe = 'N/A'

    # FORMAT EPS
    eps = stock_info['trailingEps']
    eps = f'{eps:.2f}'

    # FORMAT PROFIT MARGIN
    margin = stock_info['profitMargins']
    margin = f'{margin:.2f}'

    # PREPARE DATA FOR DIVIDENT RATE
    if stock_info['dividendRate'] is None or stock_info['dividendRate']=='':
        dividend = 'N/A'
    else:
        dividend = stock_info['dividendRate']

    # PREPATE DATA FOR EX-DIVIDEND DATE
    if stock_info['exDividendDate'] is not None:
        ex_dividend_date = datetime.fromtimestamp(stock_info['exDividendDate'])
        ex_dividend_date = ex_dividend_date.strftime('%m-%d-%Y')
    else: 
        ex_dividend_date = 'N/A'

    return html.Table([
        html.Tr([html.Td('Industry'), html.Td(),
                    html.Td(stock_info['industry'])]),
        html.Tr([html.Td('Previous Close'), html.Td(),
                    html.Td(stock_info['previousClose'])]),
        html.Tr([html.Td('Open'), html.Td(),
                    html.Td(last_open_price)]),
        html.Tr([html.Td('Day Range'), html.Td(),
                    html.Td(range_day)]),
        html.Tr([html.Td('52 Weeks Range'), html.Td(),
                    html.Td(range_52weeks)]),
        html.Tr([html.Td('Volume'), html.Td(),
                    html.Td(vol)]),
        html.Tr([html.Td('Average Volume'), html.Td(),
                    html.Td(avg_vol)]),
        html.Tr([html.Td('Market Capitalization'), html.Td(),
                    html.Td(mktcap)]),
        html.Tr([html.Td('Beta'), html.Td(),
                    html.Td(beta)]),
        html.Tr([html.Td('PE'), html.Td(),
                    html.Td(pe)]),
        html.Tr([html.Td('Forward PE'), html.Td(),
                    html.Td(fpe)]),
        html.Tr([html.Td('Earning Per Share (EPS)'), html.Td(),
                    html.Td(eps)]),
        html.Tr([html.Td('Profit Margin'), html.Td(),
                    html.Td(margin)]),
        html.Tr([html.Td('Dividend'), html.Td(),
                    html.Td(dividend)]),
        html.Tr([html.Td('Ex-Dividend Date'), html.Td(),
                    html.Td(ex_dividend_date)]),
        html.Tr([html.Td('Shares Outstanding'), html.Td(),
                    html.Td(f'{shareOutstanding:,.0f}')]),
        html.Tr([html.Td('Business Summary'), html.Td(),
            html.Td(stock_info['longBusinessSummary'])]),
        ])
