
import os
import re
import csv
import time
import json
import random
import requests
from tqdm import tqdm

# ADD TYPING TO THIS (pydantic, otherwise?)

class ForeFlightBase(object):
    def __init__(self, username, password, dir='tracklogs'):

        self.session = requests.Session()
        paylod = {"username": username, "password": password}

        res = self.session.post('https://plan.foreflight.com/', json=paylod)
        print(f'Login response: {res.content}')

        self.logs = []
        self.dir = dir  #NOTE - move this to download_tracklogs

    def get(self, url, delay=None, **kwargs):
        """
        If delay is None (default), will randomly pick a delay betwen 0.5 and 1.5 seconds
        If delay (int >= 0) is specificed then uses that time.  Delay applied after request.
        """

        resp = self.session.get(url, **kwargs)
        time.sleep(1 + random.uniform(-.5, .5))

        return resp

        # Should I make this a superclass for requests (images) outside of FF?

    def logout(self):
        print('Loging out')
        resp = self.session.get('https://plan.foreflight.com/auth/logout')


class ForeFlightTrackLogs(ForeFlightBase):

    def get_log_uuids(self):

        page, done = 0, False
        pbar, total = None, 0

        while page == 0 or not done:
            resp = self.session.get('https://plan.foreflight.com/api/tracklogs', params={'page': page})
            self.logs += resp.json().get('tracklogs')

            if pbar is None:
                total = resp.json().get('totalTracklogs')
                pbar = tqdm(total=total, desc="Loading tracklog uuid's")
            pbar.update(len(resp.json().get('tracklogs')))
            page += 1

            done = (len(self.logs) == total)
            time.sleep(0.6)

    def load_track(self, uuid):
        """
        dict_keys(['accountUuid', 'objectId', 'trackUuid', 'name', 'derivedOrigin', 'derivedDestination', 
        'timestampStart', 'totalDurationSeconds', 'totalDistanceNm', 'avgGndspd', 'username', 
        'tailNumber', 'pilotName', 'recordingDevice', 'importedFromDevice', 'initialGpsSource', 
        'metadata', 'accuracy', 'coordinates', 'markedPositions', 'totalDuration'])
        """

        resp = self.session.get(f'https://plan.foreflight.com/api/tracks/{uuid}')
        return resp.json().get('track')

    
    def download_track(self, uuid):

        r = self.session.get(f'https://plan.foreflight.com/tracklogs/export/{uuid}/kml')
        with open(f'tracklogs/kml/{uuid}.kml', 'wb') as fp: #NOTE - ignores directory
            fp.write(r.content)

        time.sleep(0.2)

    def download_all(self, download_kml=False):

        raw_data, meta_data = [], []

        for entry in tqdm(self.logs, desc='Downloading logs'):
            uuid = entry['trackUuid']
            track = self.load_track(uuid)
            raw_data.append(track)
            meta_data.append(track['metadata'])
            if download_kml:
                self.download_track(uuid)

        with open(f'{self.dir}/raw_data.json', 'w') as fp:
            json.dump(raw_data, fp)
        
        header = list(meta_data[0].keys())
        with open(f'{self.dir}/meta_data.csv', 'w') as fp:
            writer = csv.DictWriter(fp, fieldnames=header)
            writer.writeheader()
            writer.writerows(meta_data)

    def run(self, download_kml=False):
        self.get_log_uuids()
        self.download_all(download_kml)
        self.logout()

class ForeFlightLogs(ForeFlightBase):

    def download_images(self, uuid):
        """ loads images for log uuid """

        image_dir = f'images/{uuid}'
        os.mkdir(image_dir)
        r = self.session.get(f'https://plan.foreflight.com/api/1/logbook/entryImages/{uuid}')

        for image in tqdm(r.json()['result'], desc=f'Downloading {uuid} images', leave=False):
            image_url = image['image']['link']
            image_name = re.findall(r'images/(.*)\?', image_url)[0]
            image = requests.get(image_url)


            with open(f'{image_dir}/{image_name}', 'wb') as fp:
                fp.write(image.content)

            time.sleep(1.2)

    def get_logbook_page(self, page=0, size=50, search='', draft=False):

        url = 'https://plan.foreflight.com/logbook/api/entries'
        payload = {'mode': 'paginated', 'page': page, 'size': size,
                   'search': search, 'draft': draft}

        # https://plan.foreflight.com/logbook/api/entries?mode=paginated&page=2&size=50&search=&drafts=false
        req = self.session.get(url, params=payload) #NOTE - what's diff beween json and payload?

        len(req.json()['result']['content'])

        return req.json()['result']

    def get_num_drafts(self):

        url = 'https://plan.foreflight.com/logbook/api/drafts/count'
        req = self.session.get(url)

        return req.json()['result']

    def get_logbook(self):

        done = False
        page = 0
        pbar = None
        
        self.logs = []

        while not done:
            result = self.get_logbook_page(page=page)
            if pbar is None:
                total = result['totalElements']
                pbar = tqdm(total=total, desc="Loading logbook uuid's")
            self.logs += result['content']

            done = result['empty']
            page += 1
            pbar.update(result['numberOfElements'])
            time.sleep(0.76)

        with open('logbook.json', 'w') as fp:
            json.dump(self.logs, fp, indent=4)

    def get_pics(self):

        has_images = [i['objectId'] for i in self.logs if i['imageCount']]

        for entry_uuid in tqdm(has_images, desc='Logs with pics'):
            self.download_images(entry_uuid)
            time.sleep(0.34)

    def run(self):

        self.get_logbook()
        self.get_pics()
        self.logout()


class ForeFlightUserWaypoints(ForeFlightBase):

    def get_waypoints(self):
        url = 'https://plan.foreflight.com/api/1/performance/user-waypoints/'
        req = self.get(url)

        self.waypoints = req.json()['waypoints']

    def run(self):

        self.get_waypoints()
        with open('waypoints.json', 'w') as fp:
            json.dump(self.waypoints, fp, indent=4)
        self.logout()
