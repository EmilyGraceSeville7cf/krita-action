import krita
import re
import os.path
import configparser

# Change this to action.ini config path.
config_path = "~/action.ini"

def info(text):
    print(f"Info: {text}.")

def error(text):
    print(f"Error: {text}.")

def error_when_not(condition, text):
    if not condition:
        error(text)
    
    return condition

def raise_when_not_type(name, value, type):
    if not isinstance(value, type):
        raise TypeError(f"{name} should be a {type}.")

def raise_when_not_in_enum(name, value, values):
    if value not in values:
        joined = ", ".join(values)
        raise ValueError(f"{name} should be one of {joined}.")

def raise_when_not_in_range(name, value, low, high):
    if value < low or value > high:
        raise TypeError(f"{name} should be in [{low} .. {high}].")

layer_types = {
    "paint": "paintlayer",
    "vector": "vectorlayer",
    "group": "grouplayer",
    "clone": "clonelayer",
    "filter": "filterlayer",
    "fill": "fillayer",
    "file": "fileayer",
}

combiners = {
    "and": all,
    "or": any
}

class Action:
    def __init__(self, description, influence_parameters, parameters):
        raise_when_not_type('description', description, str)
        raise_when_not_type('influence_parameters["include_names"]', influence_parameters["include_names"], str)
        raise_when_not_type('influence_parameters["exclude_names"]', influence_parameters["exclude_names"], str)
        raise_when_not_type('influence_parameters["include_types"]', influence_parameters["include_types"], list)
        raise_when_not_type('influence_parameters["exclude_types"]', influence_parameters["exclude_types"], list)
        raise_when_not_type('influence_parameters["combiner"]', influence_parameters["combiner"], str)
        raise_when_not_type("parameters", parameters, dict)
        
        includes = influence_parameters["include_types"]
        excludes = influence_parameters["exclude_types"]
        for index in range(len(includes)):
            raise_when_not_in_enum(f'influence_parameters["include_types"][{index}]', includes[index], layer_types.keys())
        for index in range(len(excludes)):
            raise_when_not_in_enum(f'influence_parameters["exclude_types"][{index}]', excludes[index], layer_types.keys())        
        
        raise_when_not_in_enum('influence_parameters["combiner"]', influence_parameters["combiner"], combiners.keys())

        self._description = description
        self._include_names = influence_parameters["include_names"]
        self._exclude_names = influence_parameters["exclude_names"]
        self._include_types = includes
        self._exclude_types = excludes
        self._combiner = combiners[influence_parameters["combiner"]]
        self._parameters = parameters
    
    def _execute(self, layer):
        pass    
    
    def execute(self, layer):
        name = layer.name()
        type = layer.type().replace("layer", "")
        
        is_included_by_name = re.search(self._include_names, name)
        is_excluded_by_name = re.search(self._exclude_names, name)
        is_included_by_type = type in self._include_types
        is_excluded_by_type = type in self._exclude_types
        
        is_included_by_name = is_included_by_name and not is_excluded_by_name
        is_included_by_name = is_included_by_type and not is_excluded_by_type
        
        if self._combiner([is_included_by_name, is_included_by_type]):
            info(f"action '{self._description}' has been executed over '{name}' layer")
            self._execute(layer)
        else:
            info(f"action '{self._description}' has been skipped for '{name}' layer because: is included by name = {is_included_by_name}, is included by type = {is_included_by_type}")

class SetAlphaLockedAction(Action):
    def _execute(self, layer):
        value = False if "value" not in self._parameters else self._parameters["value"]
        raise_when_not_type("value", value, bool)
        layer.setAlphaLocked(value)
    
class SetBlendingModeAction(Action):
    def _execute(self, layer):
        value = "normal" if "value" not in self._parameters else self._parameters["value"]
        raise_when_not_type("value", value, str)
        
        modes = {
            "addition": "add",
            "+": "add", # alias
            "burn": "burn",
            "color": "color",
            "color_dodge": "dodge",
            "darken": "darken",
            "divide": "divide",
            "/": "divide", # alias
            "erase": "erase",
            "lighten": "lighten",
            "luminosity": "luminize",
            "multiply": "multiply",
            "*": "multiply", # alias
            "normal": "normal",
            "overlay": "overlay",
            "saturation": "saturation",
            "screen": "screen",
            "soft_light": "soft_light_svg"
        }
        
        raise_when_not_in_enum("value", value, modes.keys())
        layer.setBlendingMode(modes[value])

class SetCollapsedAction(Action):
    def _execute(self, layer):
        value = False if "value" not in self._parameters else self._parameters["value"]
        raise_when_not_type("value", value, bool)
        layer.setCollapsed(value)
    
class SetColorLabelAction(Action):
    def _execute(self, layer):
        value = "normal" if "value" not in self._parameters else self._parameters["value"]
        raise_when_not_type("value", value, str)
        
        colors = {
            "transparent": 0,
            "cyan": 1,
            "green": 2,
            "yellow": 3,
            "orange": 4,
            "brown": 5,
            "red": 6,
            "purple": 7,
            "gray": 8
        }
        
        raise_when_not_in_enum("value", value, colors.keys())
        layer.setColorLabel(colors[value])

class SetNameAction(Action):
    def _execute(self, layer):
        value = layer.name() if "value" not in self._parameters else self._parameters["value"]
        raise_when_not_type("value", value, str)
        layer.setName(value)

class SetOpacityAction(Action):
    def _execute(self, layer):
        value = layer.opacity() if "value" not in self._parameters else self._parameters["value"]
        raise_when_not_type("value", value, float)
        raise_when_not_in_range("value", value, 0, 1)
        layer.setOpacity(int(value * 255))

class SetPinnedToTimelineAction(Action):
    def _execute(self, layer):
        value = False if "value" not in self._parameters else self._parameters["value"]
        raise_when_not_type("value", value, bool)
        layer.setPinnedToTimeline(value)

class SetVisibleAction(Action):
    def _execute(self, layer):
        value = True if "value" not in self._parameters else self._parameters["value"]
        raise_when_not_type("value", value, bool)
        layer.setVisible(value)

def new_action(type, description, influence_parameters, parameters):
    if type == "set_alpha_locked":
        return SetAlphaLockedAction(description, influence_parameters, parameters)
    elif type == "set_blending_mode":
        return SetBlendingModeAction(description, influence_parameters, parameters)
    elif type == "set_collapsed":
        return SetCollapsedAction(description, influence_parameters, parameters)
    elif type == "set_color_label":
        return SetColorLabelAction(description, influence_parameters, parameters)
    elif type == "set_name":
        return SetNameAction(description, influence_parameters, parameters)
    elif type == "set_opacity":
        return SetOpacityAction(description, influence_parameters, parameters)
    elif type == "set_pinned_to_timeline":
        return SetPinnedToTimelineAction(description, influence_parameters, parameters)
    elif type == "set_visible":
        return SetVisibleAction(description, influence_parameters, parameters)
    
    raise ValueError("action name should be valid")

def append_not_none(dictionary, key, value):
    if value is not None:
        return {**dictionary, **{ key: value }}
    return dictionary

def read_config(config_path):
    actions = []
    print(f"Trying to read {config_path}")
    full_config_path = os.path.expanduser(config_path)
    
    config = configparser.ConfigParser()
    if config.read(full_config_path) == []:
        raise ValueError("config file should exist and be readable")
    
    for description in config.sections():
        info(f"action description is {description}")
        
        type = ""
        try:
            type = config.get(description, "type")
        except configparser.NoOptionError:
            error("type is required")
            return None
        include_names = config.get(description, "include_names", fallback=".*")
        exclude_names = config.get(description, "exclude_names", fallback="^$")
        include_types = config.get(description, "include_types", fallback=",".join(layer_types))
        exclude_types = config.get(description, "exclude_types", fallback="")
        combiner = config.get(description, "combiner", fallback=list(combiners.keys())[0])
        
        type_filter = lambda item: item != ""
        
        include_types = list(filter(type_filter, include_types.split(",")))
        exclude_types = list(filter(type_filter, exclude_types.split(",")))
        
        info(f"action include_names is {include_names}")
        info(f"action exclude_names is {exclude_names}")
        info(f"action include_types is {', '.join(include_types)}")
        info(f"action exclude_types is {', '.join(exclude_types)}")
        info(f"action combiner is {combiner}")
        
        value = ""
        
        try:
            if type == "set_alpha_locked":
                value = config.getboolean(description, "value", fallback=None)
            elif type == "set_blending_mode":
                value = config.get(description, "value", fallback=None)
            elif type == "set_collapsed":
                value = config.getboolean(description, "value", fallback=None)
            elif type == "set_color_label":
                value = config.get(description, "value", fallback=None)
            elif type == "set_name":
                value = config.get(description, "value", fallback=None)
            elif type == "set_opacity":
                value = config.getfloat(description, "value", fallback=None)
            elif type == "set_pinned_to_timeline":
                value = config.getboolean(description, "value", fallback=None)
            elif type == "set_visible":
                value = config.getboolean(description, "value", fallback=None)
        except ValueError:
            error("value should be valid")
            return
        except configparser.InterpolationSyntaxError:
            error("interpolation should be valid")
            return

        parameters = append_not_none({}, "value", value)
        influence_parameters = {
            "include_names": include_names,
            "exclude_names": exclude_names,
            "include_types": list(include_types),
            "exclude_types": list(exclude_types),
            "combiner": combiner
        }
        
        actions.append(new_action(type, description, influence_parameters, parameters))
    
    return actions

def execute_actions(actions, nodes):
    for node in nodes:
        for action in actions:
            action.execute(node)
        children = node.childNodes()
        if children != []:
            execute_actions(actions, children)

def main():
    document = krita.Krita.instance().activeDocument()
    if error_when_not(document is not None, "document should be opened"):
        actions = read_config(config_path)
        if actions is None:
            return
        execute_actions(actions, document.topLevelNodes())
