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
from kivy.properties import NumericProperty, StringProperty
import ssl
from ApiCaller import ApiCaller
from SettingsService import SettingsService
import geocoder
from geopy.geocoders import Nominatim

class MapViewTanker(FloatLayout):
    '''
    Author: Marian Neff
    -------------------
    The MapViewTanker class uses the MapView class from kivy_garden.mapview to provide the different map capabilities of the application.
    The main purpose is to display an OpenStreetMap and fill it with different markers for petrol stations around the user's location.
    The MapView gets arranged into a FloatLayout to allow easy control of the map space.
    -------------------
    '''  

    lat = NumericProperty()
    lon = NumericProperty()
    zoom = NumericProperty()

    def __init__(self, **kwargs):
        '''
        Initialises the class with all the different needed values. It generates initial markers for the different petrol stations returned from the TankerKoenig API.
        -------------------
        Parameters:
            none
        -------------------
        Returns:
            void
        -------------------
        '''

        ssl._create_default_https_context = ssl._create_stdlib_context
        super().__init__(**kwargs)
        settingsService = SettingsService()
        locationSettings = settingsService.loadLocationSettings()
        self.lat = locationSettings.get('lat')
        self.lon = locationSettings.get('long')

        self.__map = self.ids.tankerMap

        self.zoom = 20

        assert isinstance(self.__map, MapView)

        apiCaller = ApiCaller(settingsService)
        data = apiCaller.getQueriedTankerData()

        self.__setLowestAndHighestPrice(data)
        self.generateMarkersForData(data)

    def generateMarkersForData(self, data):
        '''
        Uses the provided dataset to generate according MapMarkerPopups on the MapView element. This will be visible in the UI so that the user can see where each station is and what the prices are like.
        -------------------
        Parameters:
            data: dictionary
        -------------------
        Returns:
            void
        -------------------
        '''

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

            self.__map.add_marker(marker)

    def getMarkerSourceForPrice(self, price):
        '''
        Checks the provided price to see if it is a bad, mediocre or good price compared to the highest and lowest price of the queried dataset.
        Stations with prices equal to the best price are marked in green.
        Stations with prices within 20% of the best prices are marked in yellow.
        Any other station is marked in red.
        -------------------
        Parameters:
            price: float
        -------------------
        Returns:
            string
        -------------------
        '''
            
        if (self.__lowestPrice == price):
            return 'images/green32.png'
        
        if (self.__lowestPrice * 1.02 >= price):
            return 'images/yellow32.png'
        
        return 'images/red32.png'

    def __setLowestAndHighestPrice(self, data):
        '''
        Sets the lowest and highest price based off of the dataset.
        -------------------
        Parameters:
            data: dictionary
        -------------------
        Returns:
            void
        -------------------
        '''

        self.__highestPrice = 0
        self.__lowestPrice = 5

        for dataSet in data.get('stations'):
            price = dataSet.get('price')
            if (dataSet.get('price')) > self.__highestPrice:
                self.__highestPrice = price
                continue

            if (dataSet.get('price')) < self.__lowestPrice:
                self.__lowestPrice = price

class TableView(AnchorLayout):
    '''
    Author: Alexander Gajer
    -------------------
    The TableView extends the AnchorLayout to allow easy positioning to the different cardinal directions. It provides the table widget that allows the user to display all the different petrol station data.
    -------------------
    ''' 

    def __init__(self, **kwargs):
        '''
        Initializes the TableView and fills it with queried data from the Tankerkoenig API. It uses the settings from the SettingsService to determine which data to query for when calling the API.
        The TableView displays rows for the name, distance and price of each petrol station.
        -------------------
        Parameters:
            price: float
        -------------------
        Returns:
            string
        -------------------
        '''
                
        super().__init__(**kwargs)

        settingsService = SettingsService()
        apiCaller = ApiCaller(settingsService)
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

        self.add_widget(self.data_tables)

class SettingsLayout(BoxLayout):
    '''
    Author: Marc Lepold
    -------------------
    The SettingsLayout extends the BoxLayout to arrange children in a vertical or horizontal box. It provides the settings widget that allows the user to change the fuel type and the radius.
    -------------------
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__radius = 5
        self.__type = 'e5'

    def typeDropdown(self):
        self.menu_list = [
            {
                "viewclass": "OneLineListItem",
                "text": "E5",
                "on_release": lambda x=f"e5": self.type_menu_callback(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "E10",
                "on_release": lambda x=f"e10": self.type_menu_callback(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Diesel",
                "on_release": lambda x=f"diesel": self.type_menu_callback(x),
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Alle",
                "on_release": lambda x=f"all": self.type_menu_callback(x),
            }
        ]
        self.menu = MDDropdownMenu(
            caller = self.ids.typeMenu,
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
    
    def type_menu_callback(self, text_item):
        self.__type = str(text_item)
        self.ids.typeMenu.text = str(text_item)
        self.menu.dismiss()
    
    def radius_menu_callback(self, text_item):
        self.__radius = float(text_item)
        self.ids.radiusMenu.text = str(text_item) + "km"
        self.menu.dismiss()
    
    def saveSettings(self):
        location = self.ids.plzInput.text
        print(location)
        loc = Nominatim(user_agent="Geopy Library")
        getLoc = loc.geocode(location)

        settingsService = SettingsService()
        settingsService.saveSettings(self.__radius, self.__type)
        settingsService.saveLocationSettings(getLoc.latitude, getLoc.longitude)
                
class TankerApp(MDApp):
    '''
    Author: Marian Neff (MapView), Alexander Gajer (Bottom Navigation and Icons, Widgets for TableView and Settings)
    -------------------
    The TankerApp extends the MDApp and is the main application used to display all the different functionalities.
    It loads the navigation, table view and map view so that the user has access to these types of displays.
    -------------------
    ''' 

    def build(self):
        '''
        Builds all the different UI elements needed for the application. The different views get created and are then loaded into the Bottom Navigation to allow easy cycling.
        -------------------
        Parameters:
            none
        -------------------
        Returns:
            MDBottomNavigation
        -------------------
        '''

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
