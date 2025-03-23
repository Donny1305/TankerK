from kivymd.app import MDApp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.menu import MDDropdownMenu
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
import json
import geocoder

class ApiCaller():
    def __init__(self):
        with open('settings.json', 'r') as openfile:
            json_object = json.load(openfile)
        
        self.__radius = json_object["radius"]
        self.__fuel = json_object["fuel"]
        self.__key = '97770f93-f9eb-d7d5-45d1-14c52f6817fc'
        self.__url = 'https://creativecommons.tankerkoenig.de/json/list.php'

    def getQueriedTankerData(self):
        try:
            g = geocoder.ip('me')
            print(g.latlng[0])
            url = self.__url + "?lat=" + str(g.latlng[0]) + '&lng=' + str(g.latlng[1]) + '&rad=' + str(self.__radius) + '&sort=dist&type=' + self.__fuel + '&apikey=' + self.__key
            data = requests.get(url)

            return data.json()
        except Exception as error:
            print(f'an error occurred, message: {error}')

            return { "stations": [] }
    
class MapViewTanker(FloatLayout):
    def __init__(self, **kwargs):
        ssl._create_default_https_context = ssl._create_stdlib_context
        super().__init__(**kwargs)
        g = geocoder.ip('me')

        lat = g.latlng[0]
        lon = g.latlng[1]

        self.map = self.ids.tankerMap
        self.map.center_on(lat, lon)
        self.map.zoom = 15
        assert isinstance(self.map, MapView)

        apiCaller = ApiCaller()
        data = apiCaller.getQueriedTankerData()

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
            return 'images/green32.png'
        
        if (self.lowestPrice * 1.02 >= price):
            return 'images/yellow32.png'
        
        return 'images/red32.png'

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

        apiCaller = ApiCaller()
        data = apiCaller.getQueriedTankerData()
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

        self.add_widget(self.data_tables)#

class SettingsLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__radius = 5
        self.__fuel = 'e5'

    def fuelDropdown(self):
        self.menu_list = [
            {
                "viewclass": "OneLineListItem",
                "text": "E5",
                "on_release": lambda x=f"e5": self.fuel_menu_callback(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "E10",
                "on_release": lambda x=f"e10": self.fuel_menu_callback(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Diesel",
                "on_release": lambda x=f"diesel": self.fuel_menu_callback(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Alle",
                "on_release": lambda x=f"all": self.fuel_menu_callback(x),
            }
        ]
        self.menu = MDDropdownMenu(
            caller = self.ids.fuelMenu,
            items = self.menu_list
        )
        self.menu.open()

    def radiusDropdown(self):
        self.menu_list = [
            {
                "viewclass": "OneLineListItem",
                "text": "5km",
                "on_release": lambda x=5: self.radius_menu_callback(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "10km",
                "on_release": lambda x=10: self.radius_menu_callback(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "15km",
                "on_release": lambda x=15: self.radius_menu_callback(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "25km",
                "on_release": lambda x=25: self.radius_menu_callback(x),
            }
        ]
        self.menu = MDDropdownMenu(
            caller = self.ids.radiusMenu,
            items = self.menu_list
        )
        self.menu.open()
    
    def fuel_menu_callback(self, text_item):
        self.__fuel = str(text_item)
        self.ids.fuelMenu.text = str(text_item)
        self.menu.dismiss()
    
    def radius_menu_callback(self, text_item):
        self.__radius = float(text_item)
        self.ids.radiusMenu.text = str(text_item) + "km"
        self.menu.dismiss()
    
    def saveSettings(self):
        settings = {
            "radius": self.__radius,
            "fuel": self.__fuel
        }
        
        with open("settings.json", "w") as outfile:
            json.dump(settings, outfile)
                
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
                'widget': SettingsLayout(),
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
