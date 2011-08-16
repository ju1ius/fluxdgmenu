import gmenu
from . import NONE, TYPE_DIRECTORY, TYPE_ENTRY, TYPE_SEPARATOR

class GmenuAdapter(object):
    def __init__(self):
        pass
    def get_type(self):
        return TYPE_DIRECTORY;

    def get_root_directory(self, menu_file, flags=NONE):
        tree = gmenu.lookup_tree(menu_file, flags)
        return tree.get_root_directory()
