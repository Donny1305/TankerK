try:
    from kivymd.app import MDApp
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.lang import Builder
    from kivy_garden.mapview import MapView, MapMarker, MapMarkerPopup
    from kivy.app import App
    import requests
    import random
    import ssl
    import json
except BaseException as e:
    open("/error_log.txt", "w").write(e)

class MapViewTanker(FloatLayout):
    def __init__(self, **kwargs):
        ssl._create_default_https_context = ssl._create_stdlib_context
        super().__init__(**kwargs)
        lat = 48.47728212579956
        lon = 7.955887812049504
        self.map = self.ids.tankerMap
        assert isinstance(self.map, MapView)
        self.map.center_on(lat, lon)
        self.map.zoom = 20
        rad = 5
        type = 'e5'

        """
        key = '1e89035b-ed46-fdc3-4baf-feff2614dc10'
        url = 'https://creativecommons.tankerkoenig.de/json/list.php?lat=' + str(lat) + '&lng=' + str(lon) + '&rad=' + str(rad) + '&sort=dist&type=' + type + '&apikey=' + key
        data = requests.get(url)
        print(data)"
        """

        with open('data.json') as file:
            data = json.load(file)

            for dataSet in data.get('stations'):
                stationLat = dataSet.get('lat')
                stationLon = dataSet.get('lng')
                title = dataSet.get('brand')
                price = str(dataSet.get('price')) + "€"
                street = dataSet.get('street') + " " + str(dataSet.get('houseNumber'))
                location = str(dataSet.get('postCode')) + " " + dataSet.get('place')
                address = street
                address += "\n" + location
                address += "\n" + title
                address += "\n" + price
                marker = MapMarkerPopup(lat=stationLat, lon=stationLon, source='32marker.png')
                labelPrice = Label(text=price)
                labelTitle = Label(text=title)
                label = Label(text=address)
                
                label.font_size = 24
                label.color = 1,0,0,1   

                marker.popup_size = 100, 100

                marker.add_widget(label)
                
                self.map.add_marker(marker)
    
    def randomZoom(self):
        lat = random.randint(-90, 90)
        lon = random.randint(-180, 180)
        
        self.map.center_on(lat, lon)
        self.map.zoom = random.randint(5, 10)

class TankerApp(MDApp):
    def build(self):
        Builder.load_file("map.kv")
        return MapViewTanker()
    
if __name__ == '__main__':
    TankerApp().run()

