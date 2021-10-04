import sys
import tarfile
import re
import subprocess

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

import h5py

from sqlalchemy import create_engine

from urllib.parse import quote_plus

#connect the database
engine = create_engine('mysql://root:' + quote_plus('1Step@ATime!') + '@localhost/PSWS_database')

class UploadEvent(PatternMatchingEventHandler):
    def __init__(self, patterns=None):
        super(UploadEvent, self).__init__(patterns=patterns)

    def on_created(self, event):
        #Begin by locating the path of the event
        path = event.src_path
        #Request ID will be at the end of the path, findall returns a list so need to take the first 
        #(and ideally only) match before stripping the newline
        rID = re.findall("d[0-9]+", path)[0][1:]
        print("Directory Created with ID of " + rID)

        #Now need to grab the location of the tarfile
        datapath = '/' + event.src_path.rsplit('/')[1] + '/' + event.src_path.rsplit('/')[2] + '/tangerine_data/'
        print('datapath:'+datapath)
        #Grep for upload in the folder using the stripped rID
        rawfile = subprocess.check_output('ls ' + datapath + ' | grep d' + rID + '.tar', shell=True)
        #Decode output from bytestring and strip newline
        tar_file = rawfile.decode()[:-1]
        print('tarfile:'+tar_file)
        
        #Now need to set up the tar file
        data = tarfile.open(datapath + tar_file)

        #Take time to calculate size for later before extracting
        size = 0
        for mem in data.getmembers():
            size = size + mem.size

        #Finish extracting tarfile
        data.extractall(path=event.src_path) #Extracts to the d# directory
        data.close()

        #Scrape the metadata from the properties files
        fp = h5py.File(event.src_path + '/drf_properties.h5')
        afp = h5py.File(event.src_path + '/aux_drf_properties.h5')

        #All needed fields for insertion
        dataRate = fp.attrs.get('sample_rate_numerator')
        centerFrequency = 0 #How to calculate?
        size = size #Calculated earlier
        fileName = tar_file
        path = event.src_path
        station_id = event.src_path.rsplit('/')[2]
        ### Patch for demo
        station_id = station_id[-1]

        #Finally, we can insert into the db
        conn = engine.connect()
        statement_prefix = 'INSERT INTO observations_observation '
        statement_cols = '(dataRate, centerFrequency, size, fileName, path, station_id)'
        statement_vals_tuple = dataRate, centerFrequency, size, fileName, path, station_id
        statement_vals = str(statement_vals_tuple)
        statement = statement_prefix + statement_cols + ' VALUES ' + statement_vals + ';'
        print(statement)
        conn.execute(statement)
        conn.close()

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '/home'
    event_handler = UploadEvent(patterns=["N*/d*"])
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while observer.isAlive():
            observer.join(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join() 

