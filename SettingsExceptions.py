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
