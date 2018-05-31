#!python2

import pandas as pd
import pytz
import os
import sys

def onetick_to_lss(filename, header_line_num, units):
    # read CSV file
    filename_parts = filename.split('/')
    instrument = filename_parts[len(filename_parts)-1].split('.')[0]
    df = pd.read_csv(filename, header=header_line_num)


    # convert timestamp from Unix epoch in ms
    eastern = pytz.timezone('US/Eastern')
    utc = pytz.timezone('UTC')
    df['eastern_timestamp'] = pd.to_datetime(df['#TIMESTAMP'], format='%Y%m%d %H:%M:%S.%f').dt.tz_localize(eastern)
    df['utc_timestamp'] = df.eastern_timestamp.dt.tz_convert(utc)

    # shift ET-timezone timestamps 6 hours ahead to get the offical trade date
    df['trade_date'] = (df.eastern_timestamp + pd.Timedelta('6 hours')).dt.strftime('%Y%m%d')

    # UTC LSS-formatted timestamp
    df['timestring'] = df.utc_timestamp.dt.strftime('%Y-%m-%d %H:%M:%S.%f')

    # forward fill price and volume data
    df[['BID_PRICE', 'ASK_PRICE', 'BID_SIZE', 'ASK_SIZE', 'BID_SIZE_OUTRIGHT', 'ASK_SIZE_OUTRIGHT', 'BID_SIZE_IMPLIED', 'ASK_SIZE_IMPLIED']] = df[['BID_PRICE', 'ASK_PRICE', 'BID_SIZE', 'ASK_SIZE', 'BID_SIZE_OUTRIGHT', 'ASK_SIZE_OUTRIGHT', 'BID_SIZE_IMPLIED', 'ASK_SIZE_IMPLIED']].fillna(method='ffill')

    # set which side of the book each trade occurs on
    df['SIDE'] = 0
    df.loc[df.PRICE == df.BID_PRICE, 'SIDE'] = -1
    df.loc[df.PRICE == df.ASK_PRICE, 'SIDE'] = 1

    # set tick type
    df['TICK_TYPE'] = 'Q'
    df.loc[~pd.isnull(df.PRICE), 'TICK_TYPE'] = 'T'

    #convert to dollars if the original data is in cents
    if units == 'cents':
        df.BID_PRICE = df.BID_PRICE/100.0
        df.ASK_PRICE = df.ASK_PRICE/100.0
        df.PRICE = df.PRICE/100.0

    # construct the output dataframe that will be written to a CSV
    out_df = pd.DataFrame(index=df.index)
    out_df['COLLECTION_TIME'] = df.timestring
    out_df['SOURCE_TIME'] = df.timestring
    out_df['SEQ_NUM'] = out_df.index
    out_df['TICK_TYPE'] = df.TICK_TYPE
    out_df['MARKET_CENTER'] = 'CME_GLOBEX'
    out_df['1'] = ''
    out_df['2'] = ''
    out_df['3'] = ''
    out_df['4'] = ''

    # copy data for quotes
    out_df.loc[df.TICK_TYPE == 'Q', '1'] = df.BID_PRICE
    out_df.loc[df.TICK_TYPE == 'Q', '2'] = df.BID_SIZE
    out_df.loc[df.TICK_TYPE == 'Q', '3'] = df.ASK_PRICE
    out_df.loc[df.TICK_TYPE == 'Q', '4'] = df.ASK_SIZE

    # copy data for trades
    out_df.loc[df.TICK_TYPE == 'T', '1'] = df.PRICE
    out_df.loc[df.TICK_TYPE == 'T', '2'] = df.SIZE
    out_df.loc[df.TICK_TYPE == 'T', '3'] = ''
    out_df.loc[df.TICK_TYPE == 'T', '4'] = df.SIDE

    # copy trade date information
    out_df['trade_date'] = df.trade_date

    # group the data by trade date and output to CSV
    grouped_out_df = out_df.groupby('trade_date')

    # create directory for data if it does not exist
    if not os.path.exists(instrument):
        os.makedirs(instrument)

    for trade_date, data in out_df.groupby('trade_date'):
        filename = instrument + '/tick_' + instrument + '_' + trade_date + '.txt'
        data.drop('trade_date', axis=1).to_csv(filename, index=False, header=False)


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print("USAGE: %s input-file header-line-number [units]" % (sys.argv[0]))
        sys.exit(1)

    header_line_num = int(sys.argv[2])

    units = ''

    if len(sys.argv) == 4:
        units = sys.argv[3]

    onetick_to_lss(sys.argv[1], header_line_num, units)
