### This is a script to visualize bearable data 

### What do we want to do?
# groupby
# condense days
# show weeks over long periods

import sys, getopt
import pandas as pd
import numpy as np
from datetime import timedelta
import seaborn as sns
import matplotlib.pyplot as plt
import tkinter as tk

### classes
class bearable_datavis(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        container = tk.Frame(selfp)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        frame = StartPage(container, self)
        self.frames[StartPage] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(StartPage)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

### global variables
global filter_time
global filter_group
global filter_status

### FUNCTIONS GO HERE
# read arguments etc
def main(argv):
    global inputfile
    global outputfile
    inputfile = 'None'
    outputfile = 'None'
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('bearable_datavis.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
          print('bearable_datavis.py -i <inputfile> -o <outputfile>')
          sys.exit()
       elif opt in ("-i", "--ifile"):
          inputfile = arg
       elif opt in ("-o", "--ofile"):
          outputfile = arg
    print('Input file is', inputfile)
    print('Output file is', outputfile)
if __name__ == "__main__":
    main(sys.argv[1:])

# Lets find out all aanmeldingen in a given year.
# returns a dataframe with selected aanmeldingen.
def select_aanmeldingen(source_df):
    print("Geef op voor welk jaar je de aanmeldingen wil zien. [Return] voor aanmeldingen van alle jaren.")
    year_selection = input("Jaar: ")
    if year_selection:
        print("Geef op voor welk kwartaal je de aanmeldingen wil zien. [Return] voor aanmeldingen van het hele jaar.")
        quarter_selection = input("Kwartaal: ")
        print("Alle aanmeldingen in ", year_selection)
        daterange_start = pd.to_datetime(year_selection, format='%Y')
        year_selection = timedelta(days=365)
        daterange_end = daterange_start + year_selection
        print("\n ---------------------- \n")
        aanmeldingen_select = df[source_df['Datum aanmelding'].between(pd.to_datetime(daterange_start), pd.to_datetime(daterange_end))]
        aanmeldingen_select = aanmeldingen_select.sort_values(by='Status')
        aanmeldingen_select['Kwartaal'] = aanmeldingen_select['Datum aanmelding'].dt.quarter
        if quarter_selection:
            aanmeldingen_select = aanmeldingen_select[aanmeldingen_select['Kwartaal'] == int(quarter_selection) ]
        df_output = aanmeldingen_select[['Aanmelding', 'Datum aanmelding', 'Kwartaal', 'Status', 'Voornaam', 'Naam', 'Fase 1', 'Fase 2', 'Fase 3']]
        print(df_output)
        return df_output
#    return pd.DataFrame(aanmeldingen_select, columns=['Fase 1', 'Fase 2', 'Fase 3'], index=groepen_unique)

# function to create a summary, counting deelnemers in a given dataframe
# be sure to prepare/select the right dataframe!
# NB df_summary is declared as global pending a better solution
def create_summary(source_df):
    global df_summary
    groepen_unique = df['Fase 1'].unique()
    df_summary = pd.DataFrame(source_df, columns=['Fase 1', 'Fase 2', 'Fase 3'], index=groepen_unique)
    count_selection(source_df, 'Fase 1', verbose=False)
    count_selection(source_df, 'Fase 2')
    count_selection(source_df, 'Fase 3')
    print("Totaal aantal deelnemers in dataframe")
    df_summary.index = df_summary.index.map(str)
    df_summary = df_summary.sort_index(axis=0)
    total = df_summary.sum()
    total.name = 'Totaal'
    df_summary = df_summary.append(total.transpose())
    df_summary.loc['No NNB'] = df_summary.loc['Totaal'] - df_summary.loc['NNB']
    print(df_summary)

# function to count deelnemers in groepen
def count_selection(df, column, verbose=False):
    selection = df[column].unique()
    for elem in selection:
        details = df.apply(lambda x : True
            if x[column] == elem else False, axis = 1)
        num_rows = len(details[details == True].index)
        if verbose is False:
            pass
        else:
            print("Deelnemers in", column, "selectie", elem, ": ", num_rows)
        df_summary.loc[elem, column] = num_rows

### LETS ROLL
# LOAD DATA AND CLEANUP
df = pd.read_csv(inputfile, parse_dates=[0], dtype={'category':str})
# NaN data gets replaced by NNB-values.
#df.fillna({'Fase 1':'NNB', 'Fase 2':'NNB', 'Fase 3':'NNB'}, inplace=True)

# DEBUG STUFF
df.info()
print('\n')
print(df[['date', 'category', 'rating/amount']].head)

def average_symptoms():
    df_symptoms = df.loc[df['category'] == 'Symptom']
    print(df_symptoms)
    selection = df_symptoms['date'].unique()
    for elem in selection:
        details = df.apply(lambda x : True
            if x['date'] == elem else False, axis = 1)
        num_rows = len(details[details == True].index)
        df_symptoms_summary.loc[elem, 'sympcount'] = num_rows

average_symptoms()
#df_aanmeldingen['Year/Week'] = df_aanmeldingen['Datum aanmelding'].apply(lambda x: "%d/%d" % (x.year, x.week))
#colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral','red','green','blue','orange','white','brown']
#df_aanmeldingen['Kwartaal'].value_counts().plot(kind='bar', title='Aanmeldingen')

#plt.show()
