# Databricks notebook source
# MAGIC %md
# MAGIC # IPyWidgets: Building Blocks for Python Data Apps
# MAGIC 
# MAGIC *Notebook compiled by Mimi Qunell, Solutions Architect, Databricks*
# MAGIC 
# MAGIC <br><br>
# MAGIC In this notebook we explore a variety of ways that **IPython Widgets can extend the notebook and transform it into an interactive application**.  These widgets form the basis of our very own bamboolib, and are widely used in the Python data science community.  Fun fact, one of the creators is Jason Grout, who is now at Databricks!  
# MAGIC 
# MAGIC To learn more, see the following links:
# MAGIC 
# MAGIC - [Official docs](https://docs.databricks.com/notebooks/ipywidgets.html)
# MAGIC - [Introductory tutorial](https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20Basics.html)
# MAGIC - [Official Git Repo](https://github.com/jupyter-widgets/ipywidgets)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Starting Simple

# COMMAND ----------

# MAGIC %md
# MAGIC #### DropDowns, RadioButtons, ProgressBars, and More
# MAGIC See the full widget list [here](https://ipywidgets.readthedocs.io/en/stable/examples/Widget%20List.html).

# COMMAND ----------

# MAGIC %matplotlib inline
# MAGIC import ipywidgets as widgets
# MAGIC import matplotlib.pyplot as plt
# MAGIC import numpy as np
# MAGIC from ipywidgets import interactive
# MAGIC from IPython.display import Audio, display  
# MAGIC import numpy as np

# COMMAND ----------

#Toggle Button

widgets.ToggleButton(
    value=False,
    description='Click me',
    disabled=False,
    button_style='', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Description',
    icon='check'
)

# COMMAND ----------

#Checkbox
widgets.Checkbox(
    value=False,
    description='Check me',
    disabled=False
)

# COMMAND ----------

#DropDown
i=widgets.Dropdown(
    options=[('One', 1), ('Two', 2), ('Three', 3)],
    value=2,
    description='Number:',
)
display(i)

# COMMAND ----------

i.value

# COMMAND ----------

#RadioButton
topping=widgets.RadioButtons(
    options=['pepperoni', 'pineapple', 'anchovies'],
#     value='pineapple',
    description='Pizza:',
    disabled=False
)
display(topping)

# COMMAND ----------

topping.value

# COMMAND ----------

#SelectionSlider
widgets.SelectionSlider(
    options=['scrambled', 'scrambled', 'poached', 'over easy'],
    value='scrambled',
    description='I like eggs ...',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True
)

# COMMAND ----------

#Progress Bar, with floating value
widgets.FloatProgress(
    value=7.5,
    min=0,
    max=10.0,
    step=0.1,
    description='Loading:',
    bar_style='info',
    orientation='horizontal'
)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Layout Options
# MAGIC [Tutorial source](https://financeandpython.com/courses/introduction-to-ipywidgets/lessons/layouts/)

# COMMAND ----------

from IPython.display import display
from ipywidgets import widgets

A = widgets.FloatSlider(value=50,min=10,max=200, step=.1,description='Value')
B = widgets.FloatSlider(value=50,min=10,max=200,step=.1,description='Value')
C = widgets.FloatSlider(value=50,min=10,max=200,step=.1,description='Value')

#The HBox layout is a horizontal box layout.
box_items = widgets.Box([A,B,C])
display(box_items)

# COMMAND ----------

#The VBox layout is a vertical box layout.
box_items = widgets.VBox([A,B,C])
display(box_items)

# COMMAND ----------

#If we use Layout we can pass the argument grid_template_columns with repeat(3, 300px) where the 3 is the number of columns to use and then 300px is the width of for the widget.
# https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Layout.html#The-Grid-layout
items = []
for i in range(9):
    items.append(widgets.FloatSlider(value=50,min=10,max=200,step=.1,description='Value {}:'.format(i+1)))
widgets.GridBox(items, layout=widgets.Layout(grid_template_columns="repeat(3, 300px)"))

# COMMAND ----------

#The Accordion layout is nice if you want to look at just one widget at a time. You add in the widgets with the children argument. Then from there you can set each title with set_title when you pass the index for setting a title and the title to set. Below is an example.
accordion = widgets.Accordion(children=[A, B])
accordion.set_title(0, 'Title 1')
accordion.set_title(1, 'Title 2')
display(accordion)

# COMMAND ----------

#A similar option is to use tabs like below.
tab = widgets.Tab([A, B])
tab.set_title(0, 'Title 1')
tab.set_title(1, 'Title 2')
display(tab)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Data Apps

# COMMAND ----------

# MAGIC %md 
# MAGIC #### Image browser
# MAGIC [Tutorial source](https://github.com/jupyter-widgets/ipywidgets/blob/master/docs/source/examples/Image%20Browser.ipynb)

# COMMAND ----------

from sklearn import datasets
from ipywidgets import interact

digits = datasets.load_digits()
def browse_images(digits):
    n = len(digits.images)
    def view_image(i):
        plt.imshow(digits.images[i], cmap=plt.cm.gray_r, interpolation='nearest')
        plt.title('Training: %s' % digits.target[i])
        plt.show()
    interact(view_image, i=(0,n-1))
browse_images(digits)

# COMMAND ----------

# MAGIC %md 
# MAGIC #### Beat Frequencies
# MAGIC [Tutorial source](https://github.com/jupyter-widgets/ipywidgets/blob/master/docs/source/examples/Beat%20Frequencies.ipynb)

# COMMAND ----------

# Interesting audio manipulation from: 
# https://github.com/jupyter-widgets/ipywidgets/blob/master/docs/source/examples/Beat%20Frequencies.ipynb

%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
from ipywidgets import widgets
from ipywidgets import interactive
from IPython.display import Audio, display  

def beat_freq(f1=220.0, f2=224.0):
    max_time = 3
    rate = 8000
    times = np.linspace(0,max_time,rate*max_time)
    signal = np.sin(2*np.pi*f1*times) + np.sin(2*np.pi*f2*times)
    display(Audio(data=signal, rate=rate))
    return signal
  
v = interactive(beat_freq, f1=(200.0,300.0), f2=(200.0,300.0))

display(v)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Interactive Viz
# MAGIC This next example creates interactive scatter plots for the bike sharing dataset.

# COMMAND ----------

#Ingest data
sparkDF = spark.read.csv("/databricks-datasets/bikeSharing/data-001/day.csv", header="true", inferSchema="true")
pdf = sparkDF.toPandas()
pdf

# COMMAND ----------

#Interactively create plots
import ipywidgets as widgets
import seaborn as sns 
from ipywidgets import interact

# In this code, the list ['temp', 'atemp', 'hum', 'windspeed'] creates a drop-down menu widget. 
# Setting a variable to True or False (`fit=True`) creates a checkbox widget.
@interact(column=['temp', 'atemp', 'hum', 'windspeed'], fit=True)
def f(column='temp', fit=True):
  sns.lmplot(x=column, y='cnt', data=pdf, fit_reg=fit)

# COMMAND ----------

# MAGIC %md 
# MAGIC #### Data Analysis 
# MAGIC Made with [FigureWidget](https://plotly.com/python/figurewidget-app/)

# COMMAND ----------

import datetime
import numpy as np
import pandas as pd

import plotly.graph_objects as go
from ipywidgets import widgets

df = pd.read_csv('https://raw.githubusercontent.com/yankev/testing/master/datasets/nycflights.csv')
df = df.drop(df.columns[[0]], axis=1)
df = df.sample(frac=0.1) # We sampled 10% of the original dataframe to avoid message size exceeding 1MB
df.sample(3)

# COMMAND ----------

month = widgets.IntSlider(
    value=1.0,
    min=1.0,
    max=12.0,
    step=1.0,
    description='Month:',
    continuous_update=False
)

use_date = widgets.Checkbox(
    description='Date: ',
    value=True,
)

container = widgets.HBox(children=[use_date, month])

textbox = widgets.Dropdown(
    description='Airline:   ',
    value='DL',
    options=df['carrier'].unique().tolist()
)

origin = widgets.Dropdown(
    options=list(df['origin'].unique()),
    value='LGA',
    description='Origin Airport:',
)


# Assign an empty figure widget with two traces
trace1 = go.Histogram(x=df['arr_delay'], opacity=0.75, name='Arrival Delays')
trace2 = go.Histogram(x=df['dep_delay'], opacity=0.75, name='Departure Delays')
g = go.FigureWidget(data=[trace1, trace2],
                    layout=go.Layout(
                        title=dict(
                            text='NYC FlightDatabase'
                        ),
                        barmode='overlay'
                    ))

# COMMAND ----------

def validate():
    if origin.value in df['origin'].unique() and textbox.value in df['carrier'].unique():
        return True
    else:
        return False


def response(change):
    if validate():
        if use_date.value:
            filter_list = [i and j and k for i, j, k in
                           zip(df['month'] == month.value, df['carrier'] == textbox.value,
                               df['origin'] == origin.value)]
            temp_df = df[filter_list]

        else:
            filter_list = [i and j for i, j in
                           zip(df['carrier'] == 'DL', df['origin'] == origin.value)]
            temp_df = df[filter_list]
        x1 = temp_df['arr_delay']
        x2 = temp_df['dep_delay']
        with g.batch_update():
            g.data[0].x = x1
            g.data[1].x = x2
            g.layout.barmode = 'overlay'
            g.layout.xaxis.title = 'Delay in Minutes'
            g.layout.yaxis.title = 'Number of Delays'


origin.observe(response, names="value")
textbox.observe(response, names="value")
month.observe(response, names="value")
use_date.observe(response, names="value")

# COMMAND ----------

container2 = widgets.HBox([origin, textbox])
widgets.VBox([
  container,
  container2,
  g
])

# COMMAND ----------

# MAGIC %md
# MAGIC #### Record matching
# MAGIC Label a pair of records as matches or not, then read in the values of those widgets and add them to the dataframe

# COMMAND ----------

#Create a dataframe of sample record pairs
pairs = [('Walt Disney', 'Walter Disney'),('Jiminy Cricket','Mickey Mouse'), ('Mickey Mouse', 'Minnie Mouse'), ('Goofy','Pluto'),('Mary Poppins', 'Julie Andrews')]
df = spark.createDataFrame(pairs, ['recordA','recordB'])


#Create python lists from the dataframe of suggested pairs
recordA=list(df.select('recordA').toPandas()['recordA'])
recordB=list(df.select('recordB').toPandas()['recordB'])

#Create a list of widgets to display
items=[]

#The first 3 widgets are column headers
items.append(widgets.HTML(value=f'<b>RECORD A</b>'))
items.append(widgets.HTML(value=f'<b>RECORD B</b>'))
items.append(widgets.HTML(value=f'<b>LABEL</b>'))

#For each suggested pair, generate a widget for recordA, recordB, and a radio button to select the label
for i in range(df.count()):
  items.append(widgets.HTML(value=recordA[i]))
  items.append(widgets.HTML(value=recordB[i]))
  items.append(widgets.RadioButtons(options=['Match!!', 'No Match', 'Not Sure'], value='Not Sure', disabled=False))

#tile all the widgets into a 3-column grid
g=widgets.GridBox(items, layout=widgets.Layout(grid_template_columns="repeat(3,300px)",grid_gap='20px 20px'))

#Generate a 'Review Label' button
s=widgets.Button(
    description='Review Labels',
    disabled=False,
    button_style='success', # 'success', 'info', 'warning', 'danger' or ''
    tooltip='Click this button when you are done labelling',
    #icon='check' # (FontAwesome names without the `fa-` prefix, https://fontawesome.com/v4/icons/)
    icon='thumbs-o-up'
)

#Create a callback function when the 'Review Label' button is clicked, that will echo back the current value of the labels
sOutput = widgets.Output()
def on_button_clicked(s):
    with sOutput:
        print(f"Labels Submitted:{[items[5+3*i].value for i in range(df.count())]}")

#Create a final prompt to submit the work and move on
prompt=widgets.HTML(value='You can review your labels and continue to adjust and review until you are satisfied with the final state. If you are sure you are done, Toggle the button below')
toggle=widgets.Checkbox(
    value=False,
    description="I'm Done",
    disabled=False,
    indent=False
)

# COMMAND ----------

#vertically stack and display the grid, the button, the label summary, the prompt, and the final toggle
gui=widgets.VBox(children=[g,s,sOutput,prompt,toggle])
display(gui)
s.on_click(on_button_clicked)

if not toggle.value :
  print("Please check the 'I'm Done' button to continue")
else:
  values=[items[5+3*i].value for i in range(df.count())]
  data=zip(recordA, recordB, values)
  dfLabeled=spark.createDataFrame (data, ['recordA','recordB','Label'])
  dfLabeled.show()  #Note, the 'display()' function in the Dataframe API was overridden by the Ipython.display import in Cmd 17. Need to fix that

# COMMAND ----------

# MAGIC %md
# MAGIC ### Media Imports
# MAGIC [Tutorial source](https://github.com/jupyter-widgets/ipywidgets/blob/master/docs/source/examples/Media%20widgets.ipynb)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Video

# COMMAND ----------

from ipywidgets import Image, Video, Audio
video2 = Video.from_url("https://webrtc.github.io/samples/src/video/chrome.webm", autoplay=False)
video2

# COMMAND ----------

# MAGIC %md
# MAGIC #### Images

# COMMAND ----------

Image.from_file("/dbfs/FileStore/fruit.jpg")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Audio

# COMMAND ----------

Audio.from_url("https://www.barbneal.com/wp-content/uploads/bugs05.mp3", controls=True)

# COMMAND ----------

# MAGIC %md
# MAGIC #### YouTube

# COMMAND ----------

from IPython.display import YouTubeVideo
YouTubeVideo('eVET9IYgbao')

# COMMAND ----------


