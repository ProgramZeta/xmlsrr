class Match(object):
    def __init__(self):
        self.elementList = []
        self.classList = []
        self.idList = []
        self.attributeList = []
        self.subMatch = None


    def addElement(self, elementName):
        self.elementList.append(elementName)

    def addClass(self, className):
        self.classList.append(className)

    def addId(self, idName):
        self.classList.append(idName)

    def addAttribute(self, attributeName, value=None):
        self.attributeList.append({ attributeName: value})

    def addSubMatch(self, match):
        self.subMatch = match