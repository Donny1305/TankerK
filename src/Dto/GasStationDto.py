class GasStationDto():
    def __init__(self, jsonData):
        self.__lon = jsonData.get('lng')
        self.__lat = jsonData.get('lat')
        self.__price = jsonData.get('price')
        self.__brand = jsonData.get('brand')
        self.__name = jsonData.get('name')

    def getLon(self):
        return self.__lon
    
    def getLat(self):
        return self.__lat
    
    def getPrice(self):
        return self.__price
    
    def getBrand(self):
        return self.__brand
    
    def getName(self):
        return self.__name