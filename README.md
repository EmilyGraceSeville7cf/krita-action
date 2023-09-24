# Krita action

Config for Krita script which allows perform batch actions over layers. Uses
builtin [Python INI file parser][parser] for `~/action.ini` config.
Interpolation is allowed via `%(value)s`.

[parser]: https://docs.python.org/3/library/configparser.html

# How to use

Copy `action.py` contents to builtin Krita Python editor accessible via
*Tools -> Scripts -> Scripter* and run it.

## General keys

Each section name is a user friendly description of your action shown
while executing script. Each action has the following the following keys:

- key `type` (required): action type  
  type: str  
  value: set_alpha_locked | set_blending_mode | set_collapsed |
    set_color_label | set_name | set_opacity |
    set_pinned_to_timeline | set_visible  
- key `include_names`: Python regex for filtering layers by name affected by
    action  
  type: str  
  default: .*
- key `exclude_names`: Python regex for filtering layers by name not affected
    by action  
  type: str  
  default: None  
  note: this key filters out layers matched by include_names
- key `value`: value to set layer property like transparency to  
  type (depends on action type): bool | int | float | str

## Action specific keys

Action "set_alpha_locked" has the following the following keys:

- key `value`: whether to lock alpha  
  value: true | false  
  type: bool  
  note: when omitting value it defaults to false

Action "set_blending_mode" has the following the following keys:

- key `value`: set blending mode  
  value: addition | burn | color | color_dodge |
    darken | divide | erase | lighten | luminosity | multiply | normal |
    overlay | saturation | screen | soft_light
  type: str  
  note: when omitting value it defaults to normal

Action "set_collapsed" has the following the following keys:

- key `value`: whether to collapse layer  
  value: true | false  
  type: bool  
  note: when omitting value it defaults to false

Action "set_color_label" has the following the following keys:

- key `value`: set color label  
  value: transparent | cyan | green | yellow | orange | brown | red |
    purple | gray
  type: str  
  note: when omitting value it defaults to transparent

Action "set_name" has the following the following keys:

- key `value`: set layer name  
  type: str  
  note: when omitting value it defaults to current layer name

Action "set_opacity" has the following the following keys:

- key `value`: set layer set_opacity  
  type: float [0.0 .. 1.0]  
  note: when omitting value it defaults to current layer opacity

Action "set_pinned_to_timeline" has the following the following keys:

- key `value`: whether to pin layer to timeline  
  value: true | false  
  type: bool  
  note: when omitting value it defaults to false

Action "set_visible" has the following the following keys:

- key `value`: whether to make layer visible  
  value: true | false  
  type: bool  
  note: when omitting value it defaults to true

## Examples

```ini
[Change color labels to red for all layers with "red" word inside them]
type=set_color_label
include_names=red
value=%(include_names)s
```
