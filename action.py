import krita
import re
import os.path
import configparser

# Change this to action.ini config path.
config_path = "~/action.ini"

def error(text):
    print(f"Error: {text}.")

def error_when_not(condition, text):
    if not condition:
        error(text)
    
    return condition

def raise_when_not_type(name, value, type):
    if not isinstance(value, type):
        raise TypeError(f"{name} should be a {type}")

def raise_when_not_in_enum(name, value, values):
    if value not in values:
        joined = ", ".join(values)
        raise ValueError(f"{name} should be one of {joined}")

def raise_when_not_in_range(name, value, low, high):
    if value < low or value > high:
        raise TypeError(f"{name} should be in [{low} .. {high}]")

class Action:
    def __init__(self, description, include_names, exclude_names, parameters):
        raise_when_not_type("description", description, str)
        raise_when_not_type("include_names", include_names, str)
        raise_when_not_type("exclude_names", exclude_names, str)
        raise_when_not_type("parameters", parameters, dict)

        self._description = description
        self._include_names = include_names
        self._exclude_names = exclude_names
        self._parameters = parameters
    
    def _execute(self, layer):
        pass    
    
    def execute(self, layer):
        name = layer.name()
        is_included = re.search(self._include_names, name)
        is_excluded = re.search(self._exclude_names, name)
        if is_included and not is_excluded:
            print(f"Action '{self._description}' has been executed over '{name}' layer")
            self._execute(layer)

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

def new_action(type, description, include_names, exclude_names, parameters):
    if type == "set_alpha_locked":
        return SetAlphaLockedAction(description, include_names, exclude_names, parameters)
    elif type == "set_blending_mode":
        return SetBlendingModeAction(description, include_names, exclude_names, parameters)
    elif type == "set_collapsed":
        return SetCollapsedAction(description, include_names, exclude_names, parameters)
    elif type == "set_color_label":
        return SetColorLabelAction(description, include_names, exclude_names, parameters)
    elif type == "set_name":
        return SetNameAction(description, include_names, exclude_names, parameters)
    elif type == "set_opacity":
        return SetOpacityAction(description, include_names, exclude_names, parameters)
    elif type == "set_pinned_to_timeline":
        return SetPinnedToTimelineAction(description, include_names, exclude_names, parameters)
    elif type == "set_visible":
        return SetVisibleAction(description, include_names, exclude_names, parameters)
    
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
        type = ""
        try:
            type = config.get(description, "type")
        except configparser.NoOptionError:
            error("type is required")
            return None
        include_names = config.get(description, "include_names", fallback=".*")
        exclude_names = config.get(description, "exclude_names", fallback="^$")
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
        actions.append(new_action(type, description, include_names, exclude_names, parameters))
    
    return actions

def execute_actions(actions, nodes):
    for node in nodes:
        for action in actions:
            action.execute(node)
        children = node.childNodes()
        if children != []:
            execute_actions(actions, children)

def main():
    actions = read_config(config_path)
    if actions is None:
        return
    
    document = krita.Krita.instance().activeDocument()
    if error_when_not(document is not None, "document should be opened"):
        execute_actions(actions, document.topLevelNodes())
