# Databricks notebook source
# MAGIC %md
# MAGIC # Extend and customize bamboolib with plugins
# MAGIC *Notebook compiled by Mimi Qunell, Solutions Architect, Databricks*
# MAGIC 
# MAGIC In this notebook you'll learn how to add functionality to bamboolib via plugins, making it easy to automate repetitive tasks in data analysis and visualization.  This can boost productivity for advanced users, or oepn up a whole new set of analyses for non-technical users.  You can find the original source material for this notebook [here](https://github.com/tkrabel/bamboolib).

# COMMAND ----------

# MAGIC %md
# MAGIC ### How to use plugins
# MAGIC Plugins are defined in Python, and any bamboolib session that is started after plugins have been defined will have the latest plugins available.  As we go through this notebook and add more plugins, you'll notice them available in the UI after each successive call to launch bamboolib.

# COMMAND ----------

# MAGIC %pip install bamboolib

# COMMAND ----------

#We'll be using the covid-19-data for hospitalizations
import pandas as pd
pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/hospitalizations/covid-hospitalizations.csv')

# COMMAND ----------

# MAGIC %md
# MAGIC When launching bamboolib here, notice how we do not have the option to select COVID data from the outset.

# COMMAND ----------

import bamboolib as bam
bam

# COMMAND ----------

# MAGIC %md
# MAGIC ### Types of plugins

# COMMAND ----------

# MAGIC %md
# MAGIC #### Loader plugin
# MAGIC - Create a new loader option, ingesting COVID data, and prefiltering for countries and a specific indicator type
# MAGIC - A great way to show specific datasets to analysts, with some quick preset wrangling upfront

# COMMAND ----------

#Create a plug in to add an option to the DataLoader, Offering the Covid Dataset, and a country pre-filter with multi-select
import ipywidgets as widgets
import pandas as pd
from bamboolib.plugins import LoaderPlugin, DF_NEW, Multiselect, Singleselect

#Create the pandas function that will prefilter the dataset based on a list of countries
def load_covid(countries, indicator):
  df_covid=pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/hospitalizations/covid-hospitalizations.csv')
  df_covid1=df_covid[df_covid['entity'].isin(countries)]
  df_covid2=df_covid1[df_covid1['indicator']==indicator]
  return df_covid2


#Create the plugin
class LoadCovidData(LoaderPlugin):

    name = "Load COVID Data"
    new_df_name_placeholder = "df"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.country_input = Multiselect(options=["United States","Canada","Australia","United Kingdom","Japan","Denmark","Greece","Russia","Spain"])
        self.indicator_input=Singleselect(options=["Daily hospital occupancy","Daily hospital occupancy per million","Daily ICU occupancy", "Daily ICU occupancy per million", "Weekly new hospital admissions per million", "Weekly new ICU admissions per million"])
       
   
    def render(self):
        self.set_title("Load COVID Data")
        self.set_content(
            widgets.HTML("Load countries (multi) and indicator(single) for analysis"),
            self.country_input,
            self.indicator_input,
            self.new_df_name_group,
            self.execute_button,
        )
    
    def get_code(self):
        return f"""{DF_NEW} = load_covid({self.country_input.value}, '{self.indicator_input.value}')"""

# COMMAND ----------

#Call bamboolib, select Daily ICU occupancy per million
bam

# COMMAND ----------

# MAGIC %md
# MAGIC #### Transform Plugin
# MAGIC - Create a new 'action' to get the diff within groups. This will be useful to show the change in the daily metric, grouped by country for example

# COMMAND ----------

import ipywidgets as widgets
from bamboolib.plugins import TransformationPlugin, DF_OLD, Multiselect, Singleselect, Text

class DiffWithinGroups(TransformationPlugin):

    name = "Diff within groups"
    description = "e.g. for each country, calculate the diff to the previous day/row"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        columns = list(self.get_df().columns)

        self.groupby_columns = Multiselect(
            options=columns,
            placeholder="Choose groupby column(s)",
            focus_after_init=True,
        )

        self.value_column = Singleselect(options=columns, placeholder="Choose value column")

        self.new_column_name = Text(
            value="diff", placeholder="Name of diff column"
        )

    def render(self):
        self.set_title("Diff within groups")
        self.set_content(
            widgets.HTML("Groupby"),
            self.groupby_columns,
            widgets.HTML("and calculate diff of"),
            self.value_column,
            widgets.HTML("Name of new column"),
            self.new_column_name,
        )

    def get_code(self):
        return f"{DF_OLD}['{self.new_column_name.value}'] = {DF_OLD}.groupby({self.groupby_columns.value})['{self.value_column.value}'].transform(lambda series: series.diff())"

# COMMAND ----------

bam

# COMMAND ----------

# import pandas as pd; import numpy as np
# df = load_covid(['United States', 'Canada', 'Denmark'], 'Daily hospital occupancy')
# # Step: Diff within groups
# df['diff'] = df.groupby(['entity'])['value'].transform(lambda series: series.diff())



# COMMAND ----------

# MAGIC %md
# MAGIC #### Visualization Plugin

# COMMAND ----------

import bamboolib as bam
import pandas as pd

import ipywidgets as widgets  # We use that to display e.g. HTML

from bamboolib.plugins import ViewPlugin, Singleselect, Button


class ComputeMeanOfColumn(ViewPlugin):

    # You will find the plugin via it's name and/or description.
    name = "Compute mean of a column"
    description = "Compute the mean of a selected column"

    def render(self):
        column_names = list(self.get_df().columns)

        self.column_input = Singleselect(
            options=column_names,
            placeholder="Choose column",
            focus_after_init=True,
        )
        
        self.execute_button = Button(
            description="Compute mean", 
            style="primary",  # Make the button green.
            # Whenever user clicks on self.execute_button, we call update_output.
            # For more info, type `help(Button)`
            on_click=self.update_output  
        )
        
        self.output = widgets.VBox([])
        
        self.set_title("Compute mean of column")
        self.set_content(
            widgets.HTML("Column"),
            self.column_input,
            self.execute_button,
            self.output,
        )
    
    def update_output(self, button):  # button is a required argument (convention by ipywidgets).
        selected_column_name = self.column_input.value
        selected_series = self.get_df()[selected_column_name]
        
        try:
            result = selected_series.mean()
            message = f"Mean of <b>{selected_column_name}</b>: {result:.2f}"
        except:
            # Fails e.g. if column is not numeric.
            message = f"Couldn't compute the mean for column <b>{selected_column_name}</b>"
            
        # This re-renders self.output.
        self.output.children = [widgets.HTML(message)]  # Need to use ipywidgets.

# COMMAND ----------

bam

# COMMAND ----------

# MAGIC %md
# MAGIC #### Figure Plugin

# COMMAND ----------

import bamboolib.views.plot_creator as pc

class XAxisForCovid(pc.XAxis):
  default_value="date"
  
class YAxisForCovid(pc.YAxisWithMultipleColumns):
  default_value="value"
  
class ColorForCovid(pc.Color):
  default_value="entity"
  
class LinePlotForCovid(pc.LinePlot):
  name="Line plot for Covid analysis"
  recommended_configs=[
    XAxisForCovid,
    YAxisForCovid,
    ColorForCovid,
    pc.XAxisRangeSlider,
    pc.XAxisDefaultDateRangeSelectors,
  ]

# COMMAND ----------

bam

# COMMAND ----------


