class ListOfTab:
    # Необходимо для управления вкладками
    def __init__(self):
        self.__list_of_tab = []

    def add_tab(self, tab):
        self.__list_of_tab.append(tab)

    def remove_tab(self, tab):
        self.__list_of_tab.remove(tab)

    def get_all_tab(self):
        return self.__list_of_tab


list_of_tab = ListOfTab()
