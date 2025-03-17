from kivymd.app import MDApp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy_garden.mapview import MapView, MapMarkerPopup
from kivymd.uix.bottomnavigation.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.label import MDLabel
from kivymd.uix.datatables import MDDataTable
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.metrics import dp
import requests
import ssl

class ApiCaller():
    def __init__(self):
        self.__rad = 5
        self.__type = 'e5'
        self.__key = '97770f93-f9eb-d7d5-45d1-14c52f6817fc'
        self.__url = 'https://creativecommons.tankerkoenig.de/json/list.php'

    def getQueriedTankerData(self, lat, lon):
        try:
            url = self.__url + "?lat=" + str(lat) + '&lng=' + str(lon) + '&rad=' + str(self.__rad) + '&sort=dist&type=' + self.__type + '&apikey=' + self.__key
            data = requests.get(url)

            return data.json()
        except Exception as error:
            print(f'an error occurred, message: {error}')

            return { "stations": [] }
    
class MapViewTanker(FloatLayout):
    def __init__(self, **kwargs):
        ssl._create_default_https_context = ssl._create_stdlib_context
        super().__init__(**kwargs)

        lat = 48.47728212579956
        lon = 7.955887812049504

        self.map = self.ids.tankerMap
        self.map.center_on(lat, lon)
        self.map.zoom = 20
        assert isinstance(self.map, MapView)

        apiCaller = ApiCaller()
        data = apiCaller.getQueriedTankerData(lat, lon)

        self.setLowestAndHighestPrice(data)
        self.generateMarkersForData(data)
    
    def generateMarkersForData(self, data):
        for dataSet in data.get('stations'):
            stationLat = dataSet.get('lat')
            stationLon = dataSet.get('lng')
            title = dataSet.get('brand')
            price = dataSet.get('price')
            street = dataSet.get('street') + " " + str(dataSet.get('houseNumber'))
            location = str(dataSet.get('postCode')) + " " + dataSet.get('place')

            address = street
            address += "\n" + location
            address += "\n" + title
            address += "\n" + str(price) + "€"

            markerSource = self.getMarkerSourceForPrice(price)
            marker = MapMarkerPopup(lat=stationLat, lon=stationLon, source=markerSource)

            label = Label(text=address)
            label.font_size = 32
            label.color = 1,0.64,0,1   
            label.outline_color = 0,0,0,1
            label.outline_width = 4
            marker.popup_size = 100, 100
            marker.add_widget(label)

            self.map.add_marker(marker)

    def getMarkerSourceForPrice(self, price):
        if (self.lowestPrice == price):
            return 'green32.png'
        
        if (self.lowestPrice * 1.02 >= price):
            return 'yellow32.png'
        
        return 'red32.png'

    def setLowestAndHighestPrice(self, data):
        self.highestPrice = 0
        self.lowestPrice = 5

        for dataSet in data.get('stations'):
            price = dataSet.get('price')
            if (dataSet.get('price')) > self.highestPrice:
                self.highestPrice = price
                continue

            if (dataSet.get('price')) < self.lowestPrice:
                self.lowestPrice = price

class TableView(AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        lat = 48.47728212579956
        lon = 7.955887812049504

        apiCaller = ApiCaller()
        data = apiCaller.getQueriedTankerData(lat, lon)
        stationData = data['stations']

        row_data = [
            (station['name'], station['dist'], station['price'])
            for station in stationData
        ]

        self.data_tables = MDDataTable(
            size_hint = (0.95, 0.8),
            elevation = 2,
            rows_num = len(row_data),
            column_data = [
                ("Name", dp(70)),
                ("Distanz", dp(30)),
                ("Preis", dp(30))
            ],
            row_data = row_data
        )

        self.add_widget(self.data_tables)

                
class TankerApp(MDApp):
    def build(self):
        Builder.load_file("map.kv")

        nav_items_config = [
            {
                'name': 'map_screen',
                'icon': 'map',
                'widget': MapViewTanker(),
            },
            {
                'name': 'home_screen',
                'icon': 'home',
                'widget': MDLabel(text='SETTINGS', halign='center'),
                'label': 'SETTINGS',
            },
            {
                'name': 'table_screen',
                'icon': 'table',
                'widget': TableView(),
            }
        ]

        layout = MDBottomNavigation()

        for nav_item in nav_items_config:
            item = MDBottomNavigationItem(name=nav_item['name'], icon=nav_item['icon'])
            item.add_widget(nav_item['widget'])
            layout.add_widget(item)

        return layout
    
if __name__ == '__main__':
    TankerApp().run()
