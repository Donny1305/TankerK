from kivymd.app import MDApp
from kivy.uix.floatlayout import FloatLayout
from kivy.core.audio import SoundLoader
from kivy.lang import Builder
from kivy_garden.mapview import MapView
from kivy.app import App
import requests
from src.Dto.GasStationDto import GasStationDto
import json

class MapViewTanker(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        lat = 48.47728212579956
        lon = 7.955887812049504
        self.map = self.ids.tankerMap
        assert isinstance(self.map, MapView)
        self.map.center_on(lat, lon)
        self.map.zoom = 19
        """
        rad = 5
        type = 'e5'
        key = '1e89035b-ed46-fdc3-4baf-feff2614dc10'
        url = 'https://creativecommons.tankerkoenig.de/json/list.php?lat=' + str(lat) + '&lng=' + str(lon) + '&rad=' + str(rad) + '&sort=dist&type=' + type + '&apikey=' + key
        data = requests.get(url)
        data = data.json()
        """

        with open('data.json', 'r') as jsonFile:
            data = json.load(jsonFile)

        gasStationList = []
        for data in data.get('stations'):
            gasStationList.append(GasStationDto(data))

class TankerApp(MDApp):
    def build(self):
        Builder.load_file("map.kv")
        return MapViewTanker()
    
if __name__ == '__main__':
    TankerApp().run()

