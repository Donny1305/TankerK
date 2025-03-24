from SettingsExceptions import SettingsError, UnallowedRadiusError, UnallowedTypeError
import json
import geocoder

class SettingsService():
    '''
    Author: Marian Neff
    -------------------
    The SettingsService exists in order to save and load the different settings that a user has to provide while using the app.
    They are loaded in order to make API calls with the user's desired fuel type and distance to their location.
    -------------------
    '''    

    FILE_NAME = 'settings.json'
    SETTINGS_FILE_NAME = 'location_settings.json'
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
        If there are no settings created yet, sample settings will be saved so that the functionality of the app is ensured.
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
        except FileNotFoundError as fileNotFoundError:
            self.saveSettings(5.0, 'e10')

            return {'radius': 5.0, 'type': 'e10'}
        except Exception as error:
            print(f'An error has occured while loading the settings, message: {error}')

            return {}
    
    def saveLocationSettings(self, lat, long):
        '''
        Saves the provided location settings into the location_settings.json file.
        -------------------
        Parameters:
            lat: float
            long: float
        -------------------
        Returns:
            boolean
        -------------------
        '''

        jsonSettings = {
            'lat': lat,
            'long': long
        }

        try:
            with open(self.SETTINGS_FILE_NAME, 'w') as jsonFile:
                json.dump(jsonSettings, jsonFile)

            return True
        except Exception as error:
            print(f'An error has occured while saving the settings, message: {error}')

            return False

    def loadLocationSettings(self):
        '''
        Loads the saved location settings directly from the the location_settings.json file. If no settings are provided, it will return the current location based on the geocoder package.
        The returned setting tupel should typically have the "lat" and "long" parameters.
        If there is no file created yet, the method uses the IP adress to fill the values and make a filler file.
        -------------------
        Parameters:
            none
        -------------------
        Returns:
            tupel
        -------------------
        '''
        g = geocoder.ip('me')

        try:
            with open(self.SETTINGS_FILE_NAME, 'r') as jsonFile:
                settings = json.load(jsonFile)
                lat = settings.get('lat', g.latlng[0])
                lon = settings.get('long', g.latlng[1])

            return (lat, lon)
        except FileNotFoundError as fileNotFoundError:
            lat = g.latlng[0]
            lon = g.latlng[1]

            self.saveLocationSettings(lat, lon)
            return (lat, lon)
        except Exception as error:
            print(error)
            print(f'An error has occured while loading the settings, message: {error}')

            return ()