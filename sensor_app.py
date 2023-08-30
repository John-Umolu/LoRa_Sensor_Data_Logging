# Import required Libraries
from tkinter import *
from tkintertable import TableCanvas, TableModel
import serial
import serial.tools.list_ports as ports
import csv
from datetime import datetime
from pathlib import Path
import pandas as pd

# list of column names
field_names = ['Air Quality', 'Temperature', 'Humidity', 'Flame']

# get system data and time
time_now = datetime.now()

# get system date
csv_filename = str(time_now.strftime("%d-%m-%Y")) + '.csv'

# check if CSV file exists
hdp_model = Path(csv_filename)
if not hdp_model.exists():
   df = pd.DataFrame([['', '', '', '']], columns=field_names)
   df.to_csv(csv_filename, index=False)
else:
   df = pd.read_csv(csv_filename)
   if any(df.isnull()):
      df.dropna(inplace=True)
      df.to_csv(csv_filename, index=False)

# Create a GUI app
app = Tk()
app.resizable(False, False)
app.geometry("467x530")
app.configure(bg='brown')
app.title("Autonomous Rescue Robot Sensor Data")

# Bind the app with Escape keyboard to
# quit app whenever pressed
app.bind('<Escape>', lambda e: app.quit())

# variables to store values
warning_alert = ''
max_index = 0

# function to connect to the selected serial port name
def selected_comport(name):
   global arduino, warning_alert
   try:
      arduino = serial.Serial(port=name, baudrate=115200, timeout=.1)
      warning_alert = 'Serial COM port connected: ' + str(name).upper()
   except Exception as e:
      warning_alert = 'could not open serial com port'
   return

# function to update dataframe table
def update_table(input_dict):
   global model, table, max_index
   max_index = max_index + 1
   # get the maximum index value of the read data
   model.addRow(key=str(max_index), **input_dict)
   table.redraw()
   # scroll table to the last position
   table.yview_moveto(max_index)
   return

# function to append new data to the CSV file
def realtime_backup(input_dict):
   global df
   # save realtime data
   df = pd.DataFrame([input_dict])
   df.to_csv(csv_filename, mode='a', index=False, header=False)
   return

# Define function to show frame
def show_window():
   global warning_alert, field_names

   # variables to store the input serial data
   CO_data = '0'
   temp_data = '0'
   hum_data = '0'
   flame_data = '0'

   try:
      # read incoming serial data
      data = arduino.readline()
      # check if read serial date data has double hyphen
      if str(data).count(',') >= 2:
         # convert serial data from unicode to string
         decoded_bytes = str(data[0:len(data)].decode("utf-8"))
         decoded_bytes = decoded_bytes.split(',')[2]

         # check decoded bytes if they are not empty
         if decoded_bytes is not None:
            # check if the decoded bytes has two or more A characters
            if decoded_bytes.count('A') >= 2:
               CO_data = decoded_bytes.strip().split('A')[0]
               temp_data = decoded_bytes.strip().split('A')[1]
               hum_data = decoded_bytes.strip().split('A')[2]
               flame_data = 'Detected' if decoded_bytes.strip().split('A')[3] == '1' else 'Not Detected'

               # Dictionary that we want to add as a new row
               dict_data = {'Air Quality': CO_data.strip(), 'Temperature': temp_data.strip(),
                            'Humidity': hum_data.strip(), 'Flame': flame_data.strip()}

               # calls the funstion to update dataframe table and csv file data
               realtime_backup(dict_data)
               update_table(dict_data)

         # Update preview text
         prev_text.configure(state='normal')
         prev_text.delete("1.0", "end")  # remove the old data
         prev_text.insert('end', 'Flame Status: ' + flame_data +
                          f'\nAir Quality: {CO_data} PPM' + f'\nTemperature Level: {temp_data}\u00b0C' +
                          f'\nHumidity Level: {hum_data}%' +
                          '\n\n' + warning_alert)
         prev_text.configure(state='disabled')

   except Exception as e:
      #print(e)
      warning_alert = 'could not open serial com port'
      prev_text.configure(state='normal')
      prev_text.delete("1.0", "end")  # remove the old data
      prev_text.insert('end', 'Flame Status: ' + flame_data +
                       f'\nAir Quality: {CO_data} PPM' + f'\nTemperature Level: {temp_data}\u00b0C' +
                       f'\nHumidity Level: {hum_data}%' +
                       '\n\n' + warning_alert.capitalize())
      prev_text.configure(state='disabled')

   # Repeat after an 100ms interval
   app.after(100, show_window)


# Draw tkinter table routine
tframe = Frame(app, height=450, width=450, bg="black")
tframe.grid(in_=app, row=1, column=0, columnspan=1, padx=5, pady=5)

# read saved forecast data from CSV and save to dictionary
with open(csv_filename) as f:
   dictreader = csv.DictReader(f)
   dictdata = {}
   count = 0
   for rec in dictreader:
      dictdata[count] = rec
      count = count + 1

# Create table
model = TableModel()
table = TableCanvas(tframe, model=model, editable=False, read_only=True, height=300, width=390)
prev_scrollbar = Scrollbar(app)
prev_scrollbar.config(command=table.yview)
table.config(yscrollcommand=prev_scrollbar.set)

# create the table dataframe
table.createTableFrame()
model = table.model

#can import from a dictionary to populate model
model.importDict(dictdata)

# Create preview text box
prev_text = Text(app, width=30, height=6, bg="light cyan", font=('Helvetica bold', 12))
#prev_text.pack(side=LEFT, fill=BOTH, expand=True)
prev_text.grid(in_=app, row=2, column=0, columnspan=1, padx=5, pady=5)

# Create Dropdown menu
# datatype of menu text
com_ports = list(ports.comports())
comlist = [i.device for i in com_ports]

# defines the variables to be used for the menu
clicked = StringVar()
mystr = StringVar()
var1 = IntVar()
var2 = IntVar()

# initial menu text
clicked.set('Select serial com port')

# creates the tkinter menu with the list of available PC COM ports
drop = OptionMenu(app, clicked, *comlist, command=selected_comport)
drop.config(width=20, fg="black", bg="gainsboro", font=('Times', 12))
drop.grid(in_=app, row=3, column=0, columnspan=1, padx=5, pady=5)

# calls the function to display app
show_window()

app.mainloop()