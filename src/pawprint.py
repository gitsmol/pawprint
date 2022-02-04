import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
import logging

logging.basicConfig(encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')


class BearableData:

    """This is a basic ETL process wrapped up in a class.
    This allows one to examine the data created in various stages of the process."""
    def __init__(self, bearable_file):
        logging.info('Initializing Bearable class')
        self.bearable_file = bearable_file
        self.STA_df = self.extract_data(self.bearable_file)
        self.categories = ['Symptom', 'Mood', 'Energy', 'Sleep', 'Sleep quality', 'Factors', 'Meds/Supplements']
        self.no_measure_categories = ['Factors', 'Meds/Supplements']
        self.INT_df = self.wrangle(self.STA_df)
        self.graph_configuration = {
            'trend_window' : 9,
            'histogram_period' : '1M',
            'lowess_fraction' : 0.1
        }
        
    def wrangle(self, df):
        # Timestamps are problematic in bearable export data.
        # We have to convert all data to usable timestamps before we can report anything.
        mask = df['time of day'].isna() # find missing data
        df.loc[mask, 'time of day'] = '00:00' # fill in 00:00 for missing data
        df['time of day'] = df.apply(lambda x: self.get_time(x['time of day']), axis=1)
        timedelta = pd.to_timedelta(df['time of day'] + ':00') # add seconds
        df['datetime'] = df['date'] + timedelta # create timestamp from date and time

        return df

    def extract_data(self, file):
        df = pd.read_csv(file)
        df.loc[:, 'date'] = pd.to_datetime(df.loc[:, 'date'])

        return df

    def get_binsize(self, key):
         return {
            '1W': '604800000',
            '2W': '1209600000',
            '3W': '1814400000',
            '1M': 'M1',
            '2M': 'M2',
            '3M': 'M3'
            }.get(key)

    def get_time(self, key):
        # the data contains strings vaguely pointing to periods. 
        # we have to convert these to hours and minutes for wrangle().
        if isinstance(key, str):
            if ':' in key:
                return key
        if not key:
            return '00:00'
        return {
            'pre': '00:00',
            'am': '06:00',
            'mid': '12:00',
            'pm': '18:00',
            'all day' : '00:00',
            }.get(key)

    def get_factors_unique(self, df_category):
            # get unique factors from data and store in a set
            all_factors = df_category.detail + str(' | ')
            all_factors = all_factors.sum().split(' | ')
            factors_unique = set(all_factors)
            factors_unique.remove('')
            factors_unique = sorted(factors_unique)
            
            return factors_unique

    def build_longform(self):
        df_longform = pd.DataFrame()
        df = self.INT_df
        for category in self.categories:
            df_category = df.loc[(df['category'] == category)]

            # hours of sleep need to be converted to floating point.
            if category == 'Sleep':             
                df_category['rating/amount'] = df_category['rating/amount'] + ":0"
                # TODO: don't use apply for this.
                df_category['rating/amount'] = df_category.apply(lambda x: pd.to_timedelta(x['rating/amount']), axis=1)
                df_category['rating/amount'] = df_category['rating/amount'] / datetime.timedelta(minutes=1) / 60
            
            # always convert to float for rating/amount
            df_category['rating/amount'] = pd.to_numeric(df_category.loc[:, 'rating/amount'], downcast='float')

            # symptoms are averaged and aggregated to daily levels. 
            # TODO: retain different symptoms and create reporting option for this.
            # To do this, remove one sequence of .groupby() from the last line.
            # NOTE: there are a lot of choices to be made regarding the aggregation of symptom values.
            if category == 'Symptom':
                df_category['detail'] = df_category['detail'].str.extract(r'(.*(?=\ \())')
                
                # NOTE: this averages each symptom per period of the day and sums them per period of the day. (Hence grouping on datetime.)
                # df_category = df_category.groupby(['datetime', 'category', 'detail']).agg('sum').reset_index().groupby(['datetime', 'category']).agg('sum').reset_index()

                # NOTE: this takes the max of each symptom per day and sums them per day.
                # (Hence grouping on date and normalizing periods of the day.)
                # (This is the way Bearable reports in app.)
                df_category = df_category.groupby(['date', 'category', 'detail']).agg('max').reset_index().groupby(['date', 'category']).agg('sum').reset_index()
                df_category['datetime'] = df_category['date']

            if category == 'Factors':
                # find factors in dataframe and set a numeric value
                # we use this to aggregate values and create a barchart
                df_factors = pd.DataFrame()
                self.factors_unique = self.get_factors_unique(df_category)
                for factor in self.factors_unique:
                    mask = df_category[(df_category['detail'].str.contains(factor))]
                    mask['factor'] = factor
                    mask['rating/amount'] = 1
                    mask = mask[['datetime', 'category', 'factor', 'rating/amount']]
                    df_factors = df_factors.append(mask)
                df_category = df_factors

            df_longform = df_longform.append(df_category)

        df_longform = df_longform[['datetime', 'category', 'factor', 'rating/amount', 'detail']]
        df_longform.sort_values(by='datetime', inplace=True)
        self.REP_longform = df_longform

    def draw_bearable_fig(self):
        # this is the Okabe Ito colorblind-friendly palette in hex.
        colors = ['#000000', '#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7']
        draw_categories = self.categories
        fig_measurements = go.Figure()
    
        while any(item in self.no_measure_categories for item in draw_categories):

            if 'Factors' in draw_categories:
                    selection = self.REP_longform.loc[(self.REP_longform['category'] == 'Factors')]
                    fig_factors = go.Figure()
                    # get configuration options
                    binsize = self.get_binsize(self.graph_configuration.get('histogram_period'))
                    # create histograms for every factor
                    for factor in self.factors_unique:
                        df_factor = selection.loc[selection['factor'] == factor]
                        fig_factors.add_trace(go.Histogram(x=df_factor['datetime'], y=df_factor['rating/amount'], name = factor, histfunc='sum', xbins=dict(size= binsize), autobinx=False))
                    fig_factors.update_layout(
                        autosize=True,
                        margin=dict(t=40, b=10, l=10, r=10),
                        template="plotly")
                    fig_factors.update_xaxes(rangeslider_visible = True)
                    # add figure to object, then remove category from list
                    self.FIG_factors = fig_factors
                    draw_categories.remove('Factors')            

            if 'Meds/Supplements' in draw_categories:
                    selection = self.REP_longform.loc[(self.REP_longform['category'] == 'Meds/Supplements')]
                    fig_meds = go.Figure()
                    meds_unique = selection.detail.unique()
                    # get configuration options
                    binsize = self.get_binsize(self.graph_configuration.get('histogram_period'))
                    # create histograms for every med/supplement
                    for meds in meds_unique:
                        df_meds = selection.loc[selection['detail'] == meds]
                        fig_meds.add_trace(go.Histogram(x=df_meds['datetime'], y=df_meds['rating/amount'], name = meds, histfunc='sum', xbins=dict(size= binsize), autobinx=False))
                    fig_meds.update_layout(
                        autosize=True,
                        margin=dict(t=40, b=10, l=10, r=10),
                        template="plotly")
                    fig_meds.update_xaxes(rangeslider_visible = True)
                    # add figure to object, then remove category from list
                    draw_categories.remove('Meds/Supplements')
                    self.FIG_meds = fig_meds
            
        for category in draw_categories:
            logging.debug('Building fig_measurements')
            logging.debug('draw_categories contains: %s', draw_categories)
            selection = self.REP_longform.loc[(self.REP_longform['category'] == category)]
            # pop off a color for every iteration to match the primary trace and the trendline
            trace_color = colors.pop() 

            # get configuration options
            lowess_fraction = self.graph_configuration.get('lowess_fraction')
            # create traces
            category_trace = go.Scatter(x=selection['datetime'], y=selection['rating/amount'], name=category, showlegend=True, line_shape='linear', fill='tozeroy')
            category_trace.line.color = trace_color
            trend_trace = px.scatter(selection, x=selection['datetime'], y=selection['rating/amount'], color_discrete_sequence=[trace_color], trendline='lowess', trendline_options=dict(frac=lowess_fraction)).data[1]
            trend_trace.name = f'{category} LOWESS'
            trend_trace.line.color = trace_color

            # add traces to figure
            fig_measurements.add_trace(category_trace)
            fig_measurements.add_trace(trend_trace)

        fig_measurements.update_traces(showlegend=True)
        fig_measurements.update_layout(
            autosize=True,
            margin=dict(t=40, b=10, l=10, r=10),
            template="plotly")
        fig_measurements.update_xaxes(rangeslider_visible = True)
        self.FIG_measurements = fig_measurements
     
if __name__ == "__main__":
    print("Pawprint is a module to be imported by a script.")