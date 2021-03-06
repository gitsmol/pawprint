# Pawprint
Pawprint lets users of Bearable [https://bearable.app] examine their data in a browser. Its aim is to provide an easy and safe way to generate graphs and reports for personal use or sharing with others.

## barebones technical details
The BearableData() class is intialized by passing it a csv-file as exported by the Bearable app. There is no error checking! If you pass modified/unsuitable data, don't expect usable results.

Before transforming the Bearable data to longform, consider changing the parameters:
graph_configuration is a dict consisting of:
- trend_window: sets the number of measurements to average when calculating a trend (default: 9) (Already deprecated in favor of lowess-trendline from Plotly)
- lowess_fraction: set the amount of smoothing for the LOWESS trendline. (default: 0.1)
- histogram_period: sets the histogram binsize (used for factors) (default: 1 month).

categories is a list that contains the categories to be included. The default list is:
['Symptom', 'Mood', 'Energy', 'Sleep', 'Sleep quality', 'Factors']

build_longform() creates the REP_longform dataframe.

draw_bearable_fig() creates two plotly graph objects:
 - FIG_measurements
 - FIG_factors

I consider these to be roughly the facts and dimensions for a Bearable datasets. One practical reason for not mixing them is there are easily over 50 factors to report on. This is because even when indicating two degrees of one factors ('busy day', 'quiet day'), we still end up with two factors.

## Working example
A working example is provided in the form of a Dash-webapplication here: https://www.polyprax.nl/pawprint.

A basic example of using the pawprint module in python would be:

```
import pawprint                 # import pawprint module

data = pawprint.BearableData('../bearable_data.csv')    # initialize BearableData-object
data.graph_configuration['lowess_fraction'] = 0.3       # smooth out the trendlines
data.graph_configuration['histogram_period'] = '2W'     # set the histogram binsize to 2 weeks
data.build_longform()           # create long-form dataframe
data.draw_bearable_fig()        # create two figures
data.FIG_measurements.show()    # show measurements
data.FIG_factors.show()         # show factors
```

## Dependencies
This project is built entirely on 
- Python (3.9.6 but should work on earlier versions)
- Pandas
- Plotly and Plotly Express
- Dash and its Flask underpinnings

## Running this at home
In any console, firing up ```python3 pawdash.py``` should give you the pawprint interface on localhost:8050. Beware: the default config expects to run in '/pawprint/'. Change this to any suitable value or just '/'.


