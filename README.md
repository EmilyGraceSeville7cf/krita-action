# Krita action

Config for Krita script which allows perform batch actions over layers. Uses
builtin [Python INI file parser][parser] for `~/action.ini` config.
Interpolation is allowed via `%(value)s`.

[parser]: https://docs.python.org/3/library/configparser.html

## How to use

Copy `action.py` contents to builtin Krita Python editor accessible via
*Tools -> Scripts -> Scripter* and run it.

It's possible to write config in YAML and [convert][converter] it to INI.
The benefit is to have IntelliSence enabled from [JSON schema][schema].
To be able to use IntelliSence hints in YAML add
`# yaml-language-server: $schema=https://raw.githubusercontent.com/EmilyGraceSeville7cf/krita-action/main/action.json`
as the first string and install [YAML][yaml] extension.

![image](https://github.com/EmilyGraceSeville7cf/krita-action/assets/42812113/1dd7b82b-0a4a-4c24-82c6-b8a5be54112b)

[converter]: https://marketplace.visualstudio.com/items?itemName=petli-full.json-to-yaml-and-more
[schema]: https://github.com/EmilyGraceSeville7cf/krita-action/blob/main/action.json
[yaml]: https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml

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

Action "remove" has the following the following keys:

- key `value`: whether to remove layer  
  value: true | false  
  type: bool  
  note: when omitting value it defaults to false

Action "set_position" has the following the following keys:

- key `value`: set layer position  
  type: str  
  note: when omitting value it defaults to 0,0

Action "add_position" has the following the following keys:

- key `value`: add layer position  
  type: str  
  note: when omitting value it defaults to 0,0

Action "multiply_position" has the following the following keys:

- key `value`: multiply layer position  
  type: str  
  note: when omitting value it defaults to 0,0

Action "add_rotation" has the following the following keys:

- key `value`: add layer rotation  
  type: float  
  note: when omitting value it defaults to 0.0

Action "toggle_alpha_locked" has no keys

Action "toggle_collapsed" has no keys

Action "toggle_opacity" has no keys

Action "toggle_pinned_to_timeline" has no keys

Action "toggle_visible" has no keys

## Examples

## Change color labels

```ini
[Change color labels to red for all layers with "red" word inside them]
type=set_color_label
include_names=red
value=%(include_names)s
```

The same code can be represented in YAML:

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/EmilyGraceSeville7cf/krita-action/main/action.json
Change color labels to red for all layers with "red" word inside them:
  type: set_color_label
  include_names: red
  value: "%(include_names)s"
```

Note that script doesn't read YAML config, so you must convert it back to INI
to make it readable.

## Remove vector layers

```ini
[Remove all vector layers]
type=remove
include_types=vector
```

The same code can be represented in YAML:

```yaml
# yaml-language-server: $schema=https://raw.githubusercontent.com/EmilyGraceSeville7cf/krita-action/main/action.json
Remove all vector layers:
  type: remove
  include_types: vector
```
