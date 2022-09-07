# Databricks notebook source
# MAGIC %md
# MAGIC #### Get latest COVID-19 hospitalization data

# COMMAND ----------

!wget -q https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/hospitalizations/covid-hospitalizations.csv -O /tmp/covid-hospitalizations.csv

# COMMAND ----------

# MAGIC %md #### Transform with bamboolib

# COMMAND ----------

# MAGIC %pip install bamboolib

# COMMAND ----------

import pandas as pd

# read from /tmp, subset for USA, pivot and fill missing values
df = pd.read_csv("/tmp/covid-hospitalizations.csv")

display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC This data is in a long format and contains a large number of unique entities and iso_codes. To better visualize the trends over time we'll need to cast it to wide format and filter down to a single country.  Lets do that now with bamboolib!
# MAGIC 
# MAGIC *Note: Give a new name to the dataframe you create in each step using bamboolib, e.g., `filtered_df`, then `wide_df`.  The last few cells in this notebook assume you have named your output dataframe `wide_df`.*
# MAGIC 
# MAGIC **To do:**
# MAGIC 1. **Filter the data on the `entity` column** for the country you live in (or a country of your choice). 
# MAGIC 2. **Pivot the data [from long to wide format](https://towardsdatascience.com/reshaping-a-pandas-dataframe-long-to-wide-and-vice-versa-517c7f0995ad)**, spreading the `indicator` column into multiple columns with the associated date and value for each observation.
# MAGIC 3. This will generate some missing values due to a lack of data collection on some dates for specific indicators.  **Fill all missing values in the data with zero.**

# COMMAND ----------

# RUN THIS CELL TO IMPORT AND USE BAMBOOLIB

import bamboolib as bam

# This opens a UI from which you can import your data
bam  

# Printing a pandas dataframe will also open bamboolib
df

# COMMAND ----------

import pandas as pd; import numpy as np
# Step: Keep rows where entity is one of: Canada
filtered_df = df.loc[df['entity'].isin(['Canada'])]

# Step: Pivot dataframe from long to wide format using the variable column 'indicator' and the value column 'value'
wide_df = filtered_df.set_index(['entity', 'iso_code', 'date', 'indicator'])['value'].unstack(-1).reset_index()
wide_df.columns.name = ''

# Step: Replace missing values
wide_df = wide_df.fillna(0)



# COMMAND ----------

import pandas as pd; import numpy as np
# Step: Keep rows where entity is one of: Canada
df = df.loc[df['entity'].isin(['Canada'])]

# Step: Pivot dataframe from long to wide format using the variable column 'indicator' and the value column 'value'
wide_df = df.set_index(['entity', 'iso_code', 'date', 'indicator'])['value'].unstack(-1).reset_index()
wide_df.columns.name = ''

# Step: Replace missing values
wide_df = wide_df.fillna(0)


display(wide_df)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Visualize 
# MAGIC Now that we have a tidy dataset we can visualize the trends over time.  Let's use bamboolib to create a plot that we will ultimately include in our weekly report.
# MAGIC 
# MAGIC In the following cell, enter the name of your pandas dataframe that you created in the previous step and run the cell to launch bamboolib again.
# MAGIC 
# MAGIC **To Do:**
# MAGIC 1. Using the Plot Creator in bamboolib, **create a Line plot**.  
# MAGIC 2. **Choose `date` for the xAxis, and all of the former `indicator` columns for the yAxis**.
# MAGIC 3. **Title your plot** by choosing Figure: title, then Legend: title.
# MAGIC 4. **Change the background theme** by choosing Figure: theme, then selecting 'plotly_white'.
# MAGIC 5. Export the code and run it in its own cell.

# COMMAND ----------

wide_df

# COMMAND ----------

# Insert plotting code here
import plotly.express as px
fig = px.line(wide_df.sort_values(by=['date'], ascending=[True]), x='date', y=['Daily ICU occupancy', 'Daily ICU occupancy per million', 'Daily hospital occupancy', 'Daily hospital occupancy per million'], template='plotly_white', title='Hospitalizations')
fig.update_layout(legend_title_text='Indicator')
fig.update_yaxes(title_text='Patients')
fig

# COMMAND ----------

# MAGIC  %md
# MAGIC #### Save to Delta Lake
# MAGIC The current schema has spaces in the column names, which are incompatible with Delta Lake.  To save our data as a table, we'll replace the spaces with underscores.  
# MAGIC 
# MAGIC *Note: Please run the following cell to ensure that when you write a Delta table it won't conflict with anyone elses!*

# COMMAND ----------

dbutils.widgets.text("db_prefix", "covid_trends")
dbutils.widgets.text("reset_all_data", "false")

import re
current_user = dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().apply('user')
if current_user.rfind('@') > 0:
  current_user_no_at = current_user[:current_user.rfind('@')]
else:
  current_user_no_at = current_user
current_user_no_at = re.sub(r'\W+', '_', current_user_no_at)

db_prefix = dbutils.widgets.get("db_prefix")

dbName = db_prefix+"_"+current_user_no_at
cloud_storage_path = f"/Users/{current_user}/field_demos/{db_prefix}"
reset_all = dbutils.widgets.get("reset_all_data") == "true"

if reset_all:
  spark.sql(f"DROP DATABASE IF EXISTS {dbName} CASCADE")
  dbutils.fs.rm(cloud_storage_path, True)

spark.sql(f"""create database if not exists {dbName} LOCATION '{cloud_storage_path}/tables' """)
spark.sql(f"""USE {dbName}""")

print("using cloud_storage_path {}".format(cloud_storage_path))
print("new database created {}".format(dbName))

# COMMAND ----------

import pyspark.pandas as ps

clean_cols = wide_df.columns.str.replace(' ', '_')

# Create pandas on Spark dataframe
psdf = ps.from_pandas(wide_df)

psdf.columns = clean_cols

# Write to Delta table, overwrite with latest data each time
psdf.to_table(name='dev_covid_analysis', mode='overwrite')

# COMMAND ----------

# MAGIC %md
# MAGIC #### View table

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT * FROM dev_covid_analysi

# COMMAND ----------


