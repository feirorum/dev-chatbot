# Funkifier API Reference

## Core Classes

### GrooveGenerator

The `GrooveGenerator` class creates funky text transformations with various groove intensities.

#### Constructor

```python
GrooveGenerator(style="parliament", intensity=7, add_emoji=True)
```

**Parameters:**
- `style` (str): The funk style - "parliament", "bootsy", "sly", or "james_brown". Default: "parliament"
- `intensity` (int): Groove intensity from 1-10. Default: 7
- `add_emoji` (bool): Whether to add musical emojis. Default: True

#### Methods

##### get_the_funk(text, capitalize=True)

Applies funk transformation to the input text.

**Parameters:**
- `text` (str): The text to funkify
- `capitalize` (bool): Whether to capitalize the output. Default: True

**Returns:** str - The funkified text

**Example:**
```python
groove = GrooveGenerator(style="bootsy", intensity=10)
result = groove.get_the_funk("Deploy the code")
# Result: "🌟 DEPLOY THE CODE - STRETCHIN' OUT IN A RUBBER BAND! 🌟"
```

##### add_syncopation(text, pattern="standard")

Adds rhythmic syncopation markers to text.

**Parameters:**
- `text` (str): Input text
- `pattern` (str): Rhythm pattern - "standard", "offbeat", or "polyrhythm"

**Returns:** str - Text with syncopation markers

---

### BassLineBuilder

Creates bass-heavy text transformations with low-end emphasis.

#### Constructor

```python
BassLineBuilder(frequency="low", groove_level=8, style="thundercat")
```

**Parameters:**
- `frequency` (str): Bass frequency - "low", "sub", or "deep". Default: "low"
- `groove_level` (int): How groovy (1-10). Default: 8
- `style` (str): Bass style - "thundercat", "bootsy", or "larry_graham"

#### Methods

##### drop_the_bass(message, emphasis=True)

Wraps message with bass-heavy styling.

**Parameters:**
- `message` (str): The message to enhance
- `emphasis` (bool): Add extra bass emphasis

**Returns:** str - Bass-enhanced message

**Example:**
```python
bass = BassLineBuilder(frequency="deep", groove_level=10)
output = bass.drop_the_bass("System initialized")
# Output: "🎸💥 SYSTEM INITIALIZED 💥🎸"
```

---

### FunkQuotes

Provides access to funk-inspired quotes and wisdom.

#### Methods

##### get_random_quote()

Returns a random funk-inspired quote.

**Returns:** str - A funky quote

**Example:**
```python
from funkifier import FunkQuotes

quotes = FunkQuotes()
print(quotes.get_random_quote())
# Output: "Free your mind and your code will follow"
```

##### get_quote_by_theme(theme)

Get a quote by theme.

**Parameters:**
- `theme` (str): Theme like "groove", "funk", "soul", "bass", or "rhythm"

**Returns:** str - A themed quote

---

### SyncopationEngine

Advanced rhythmic text manipulation.

#### Methods

##### apply_syncopation(text, time_signature="4/4")

Applies syncopated rhythm to text structure.

**Parameters:**
- `text` (str): Input text
- `time_signature` (str): Musical time signature. Default: "4/4"

**Returns:** str - Syncopated text

**Example:**
```python
from funkifier import SyncopationEngine

engine = SyncopationEngine()
result = engine.apply_syncopation("Error in module", time_signature="7/8")
# Output: "Er-ror • in • mo-dule •"
```

---

## Constants

### FUNK_STYLES

Available funk styles:
- `PARLIAMENT`: Parliament-Funkadelic inspired
- `BOOTSY`: Bootsy Collins style
- `SLY_STONE`: Sly & The Family Stone
- `JAMES_BROWN`: Godfather of Soul style

### GROOVE_LEVELS

Predefined groove intensity levels:
- `MINIMAL` = 2
- `MODERATE` = 5
- `HEAVY` = 8
- `MAXIMUM` = 10

### BASS_FREQUENCIES

Bass frequency ranges:
- `LOW`: 60-250 Hz equivalent
- `SUB`: 20-60 Hz equivalent
- `DEEP`: < 20 Hz equivalent
