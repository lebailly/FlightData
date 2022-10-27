import yaml
from fore_flight import *

with open('credentials.yml') as fp:
    creds = yaml.safe_load(fp)['ForeFlight']

fore_flight_waypoints = ForeFlightUserWaypoints(**creds)
fore_flight_waypoints.run()

fore_flight_tracklogs = ForeFlightTrackLogs(**creds)
fore_flight_tracklogs.run(download_kml=True)

fore_flight_log_pics = ForeFlightLogs(**creds)
fore_flight_log_pics.run()
