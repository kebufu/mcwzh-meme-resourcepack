from json import load
from os import listdir
from os.path import exists, isfile, join, split
from sys import stderr


class module_checker(object):
    def __init__(self, module_path: str):
        self.__checked = False
        self.__module_path = module_path
        self.__module_info = {}
        self.__info = []

    @property
    def check_info_list(self):
        return self.__info

    @property
    def module_info(self):
        if not self.__checked:
            self.check_module()
        return self.__module_info

    @property
    def module_path(self):
        return self.__module_path

    @module_path.setter
    def module_path(self, value: str):
        self.__module_path = value

    def clean_status(self):
        self.__checked = False
        self.__module_info = {}
        self.__info = []

    def check_module(self):
        self.clean_status()
        module_info = {
            'path': self.module_path,
            'modules': {
                'language': [],
                'resource': [],
                'mixed': []
            }
        }
        for module in listdir(self.module_path):
            status, info, data = self.__analyze_module(
                join(self.module_path, module))
            if status:
                module_info['modules'][data.pop('type')].append(data)
            else:
                self.__info.append(f"Warning: {info}")
                print(f"\033[33mWarning: {info}\033[0m", file=stderr)
        self.__module_info = module_info
        self.__checked = True

    def __analyze_module(self, path: str):
        manifest = join(path, "manifest.json")
        dir_name = split(path)[1]
        if exists(manifest) and isfile(manifest):
            data = load(open(manifest, 'r', encoding='utf8'))
            for key in ('name', 'type', 'description'):
                if key not in data:
                    return False, f'In path "{dir_name}": Incomplete manifest.json, missing "{key}" field', None
            if data['type'] == 'language':
                if not (exists(join(path, "add.json")) or exists(join(path, "remove.json"))):
                    return False, f'In path "{dir_name}": Expected a language module, but couldn\'t find "add.json" or "remove.json"', None
            elif data['type'] == 'resource':
                if not exists(join(path, "assets")):
                    return False, f'In path "{dir_name}": Expected a resource module, but couldn\'t find "assets" directory', None
            elif data['type'] == 'mixed':
                if not (exists(join(path, "assets")) and (exists(join(path, "add.json")) or exists(join(path, "remove.json")))):
                    return False, f'In path "{dir_name}": Expected a mixed module, but couldn\'t find "assets" directory and either "add.json" or "remove.json"', None
            else:
                return False, f'In path "{dir_name}": Unknown module type "{data["type"]}"', None
            data['dirname'] = dir_name
            return True, None, data
        else:
            return False, f'In path "{dir_name}": No manifest.json', None
