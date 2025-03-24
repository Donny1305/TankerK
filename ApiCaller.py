from SettingsService import SettingsService
import requests
import time

class ApiCaller():
    '''
    Author: Marian Neff
    -------------------
    The ApiCaller is a service that is used to communicate with the Tankerkoenig API. The api returns all the different petrol stations within a chosen radius around the user's location.
    The class constants KEY and URL are used to put together the correct API url.
    -------------------
    '''

    KEY = '1e89035b-ed46-fdc3-4baf-feff2614dc10'
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
        self.__session = requests.Session()

    def getQueriedTankerData(self):
        '''
        Uses the provided location values to query the Tankerkoenig API and get back matching values. The settings and the location values for the API call are loaded through the SettingsService class.
        Retries the API call 3 times in case there is an issue.
        -------------------
        Parameters:
            none
        -------------------
        Returns:
            dictionary
        -------------------
        '''
        attempts = 3

        while attempts is not 0:
            try: 
                settings = self.__settingsService.loadSettings()
                (lat, long) = self.__settingsService.loadLocationSettings()
                url = self.URL + "?lat=" + str(lat) + '&lng=' + str(long) + '&rad=' + str(settings.get('radius')) + '&sort=dist&type=' + settings.get('type') + '&apikey=' + self.KEY
                data = self.__session.get(url, timeout=5)

                return data.json()
            except Exception as error:
                print(f'An error has occurred during the API call, message: {error}')
                attempts -= 1

        return { "stations": [] }