try:
    from kivymd.app import MDApp
    from kivy.uix.floatlayout import FloatLayout
    from kivy.core.audio import SoundLoader
    from kivy.lang import Builder
    from kivy_garden.mapview import MapView
    from kivy.app import App
    import requests
    import random
    import ssl
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
        self.map.zoom = 5
        rad = 5
        type = 'e5'
        key = '1e89035b-ed46-fdc3-4baf-feff2614dc10'
        url = 'https://creativecommons.tankerkoenig.de/json/list.php?lat=' + str(lat) + '&lng=' + str(lon) + '&rad=' + str(rad) + '&sort=dist&type=' + type + '&apikey=' + key
        data = requests.get(url)
        print(data)

    
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

