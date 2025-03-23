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
import json
import requests
import ssl

class ApiCaller():
    '''
    Author: Marian Neff
    -------------------
    The ApiCaller is a service that is used to communicate with the Tankerkoenig API. The api returns all the different petrol stations within a chosen radius around the user's location.
    The class constants KEY and URL are used to put together the correct API url.
    -------------------
    '''

    KEY = '97770f93-f9eb-d7d5-45d1-14c52f6817fc'
    URL = 'https://creativecommons.tankerkoenig.de/json/list.php'

    def __init__(self, settingsService):
        '''
        Sets the required dependencies for the class
        -------------------
        Parameters:
            settingsService: SettingsService, 
        -------------------
        Returns:
            void
        -------------------
        '''

        assert isinstance(settingsService, SettingsService)
        self.__settingsService = settingsService

    def getQueriedTankerData(self, lat, lon):
        '''
        Uses the provided location values to query the Tankerkoenig API and get back matching values. The settings for the API call are loaded through the SettingsService class.
        -------------------
        Parameters:
            lat: float, 
            lon: float
        -------------------
        Returns:
            dictionary
        -------------------
        '''

        try:
            #@TODO: Until the setting UI is implemented, the setting is hardcoded here. 
            self.__settingsService.saveSettings(5, 'e5')
            settings = self.__settingsService.loadSettings()
            url = self.URL + "?lat=" + str(lat) + '&lng=' + str(lon) + '&rad=' + str(settings.get('radius')) + '&sort=dist&type=' + settings.get('type') + '&apikey=' + self.KEY
            data = requests.get(url)

            return data.json()
        except Exception as error:
            print(f'An error has occurred during the API call, message: {error}')

            return { "stations": [] }
        

class SettingsService():
    '''
    Author: Marian Neff
    -------------------
    The SettingsService exists in order to save and load the different settings that a user has to provide while using the app.
    They are loaded in order to make API calls with the user's desired fuel type and distance to their location.
    -------------------
    '''    

    FILE_NAME = 'settings.json'
    ALLOWED_TYPES = ['e5', 'e10', 'diesel', 'all']

    def validateSettingParameters(self, radius, type):
        '''
        Validates the provided settings so that no false values are saved into the settings file.
        -------------------
        Parameters:
            radius: float, range 1 - 25
            type: string, ["e5", "e10", "diesel", "all"]
        -------------------
        Returns:
            void
        -------------------
        Raises:
            UnallowedRadiusError
            UnallowedTypeError
        -------------------
        '''

        if (radius < 1 or radius > 25):
            raise UnallowedRadiusError('The provided radius of ' + str(radius) + ' km has to be between 1-25 km.')

        if (type not in self.ALLOWED_TYPES):
            raise UnallowedTypeError('The provided type "' + str(type) + '" does not match one of the allowed values.')       

    def saveSettings(self, radius, type):
        '''
        Saves the provided settings into the settings.json file if they are valid.
        -------------------
        Parameters:
            radius: float, range 1 - 25
            type: string, ["e5", "e10", "diesel", "all"]
        -------------------
        Returns:
            boolean
        -------------------
        '''
                
        try:
            self.validateSettingParameters(radius, type)
        except SettingsError as error:
            print(f'An error has occured while saving the settings, details: {error}')

            return False

        jsonSettings = {
            'radius': radius,
            'type': type
        }

        try:
            with open(self.FILE_NAME, 'w') as jsonFile:
                json.dump(jsonSettings, jsonFile)

            return True
        except Exception as error:
            print(f'An error has occured while saving the settings, message: {error}')

            return False

    def loadSettings(self):
        '''
        Loads the saved settings directly from the the settings.json file. If no settings are provided, it will return an empty dictionary instead of the settings.
        The returned setting dictionary should typically have the "radius" and "type" parameters.
        -------------------
        Parameters:
            none
        -------------------
        Returns:
            dictionary
        -------------------
        '''

        try:
            with open(self.FILE_NAME, 'r') as jsonFile:
                settings = json.load(jsonFile)

            return settings
        except Exception as error:
            print(f'An error has occured while loading the settings, message: {error}')

            return {}

class SettingsError(Exception):
    '''
    Author: Marian Neff
    -------------------
    The SettingsError is an exception that is raised whenever an error occurs during the saving of settings within the SettingsService class.
    It serves as a foundation for further inheritance to define more precise errors and inherits from the default Exception.
    -------------------
    '''  
        
    def __init__(self, message):
        super().__init__(self, message)

class UnallowedRadiusError(SettingsError):
        '''
        Author: Marian Neff
        -------------------
        The UnallowedRadiusError is an exception that is raised when the provided radius within the SettingsService class exceeds the allowed values (1-25).
        It inherits the SettingsError.
        -------------------
        '''  

        def __init__(self, message):
            super().__init__(self, message)


class UnallowedTypeError(SettingsError):
        '''
        Author: Marian Neff
        -------------------
        The UnallowedTypeError is an exception that is raised when the provided type within the SettingsService class does not match one of the allowed values (["e5", "e10", "diesel", "all"]).
        It inherits the SettingsError.
        -------------------
        '''  
                
        def __init__(self, message):
            super().__init__(self, message)


class MapViewTanker(FloatLayout):
    '''
    Author: Marian Neff
    -------------------
    The MapViewTanker class uses the MapView class from kivy_garden.mapview to provide the different map capabilities of the application.
    The main purpose is to display an OpenStreetMap and fill it with different markers for petrol stations around the user's location.
    The MapView gets arranged into a FloatLayout to allow easy control of the map space.
    -------------------
    '''  
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

        #@TODO: Until the setting UI is implemented, some of the functionality is statically coded here. Once the setting functionality is implemented, the API calls will be extracted and the map will be controlled dynamically to the request. 
        ssl._create_default_https_context = ssl._create_stdlib_context
        super().__init__(**kwargs)

        lat = 48.47728212579956
        lon = 7.955887812049504

        self.map = self.ids.tankerMap

        self.map.center_on(lat, lon)
        self.map.zoom = 20

        assert isinstance(self.map, MapView)

        settingsService = SettingsService()
        apiCaller = ApiCaller(settingsService)
        data = apiCaller.getQueriedTankerData(lat, lon)

        self.setLowestAndHighestPrice(data)
        self.generateMarkersForData(data)
    
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
    def getMarkerSourceForPrice(self, price):
        if (self.lowestPrice == price):
            return 'green32.png'
        
        if (self.lowestPrice * 1.02 >= price):
            return 'yellow32.png'
        
        return 'red32.png'

    def setLowestAndHighestPrice(self, data):
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

        settingsService = SettingsService()
        apiCaller = ApiCaller(settingsService)
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
    '''
    Author: Marian Neff, Alexander Gajer
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
