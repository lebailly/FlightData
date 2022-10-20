import yaml
from fore_flight import ForeFlightUserWaypoints

with open('credentials.yml') as fp:
    creds = yaml.safe_load(fp)

fore_flight_logs = ForeFlightUserWaypoints(**creds)
fore_flight_logs.run()
#fore_flight.download_tracklog_data(download_kml=True) # took only 4:35 to run 
