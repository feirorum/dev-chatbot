# Funkifier Examples

## Basic Usage

### Simple Text Funkification

```python
from funkifier import GrooveGenerator

groove = GrooveGenerator()
print(groove.get_the_funk("Starting application"))
# Output: "🎵 STARTING APPLICATION - ONE NATION UNDER A GROOVE! 🎵"
```

### Custom Funk Style

```python
from funkifier import GrooveGenerator, FUNK_STYLES

# Use Bootsy Collins style
groove = GrooveGenerator(style=FUNK_STYLES.BOOTSY, intensity=9)
message = groove.get_the_funk("Database connected")
print(message)
# Output: "🌟 DATABASE CONNECTED - STRETCHIN' OUT IN A RUBBER BAND! 🌟"
```

## Advanced Examples

### Error Messages with Funk

```python
from funkifier import BassLineBuilder, GrooveGenerator

def funky_error_handler(error_msg):
    bass = BassLineBuilder(frequency="deep", groove_level=10)
    groove = GrooveGenerator(style="james_brown", intensity=8)

    funkified = groove.get_the_funk(f"Error: {error_msg}")
    return bass.drop_the_bass(funkified)

try:
    risky_operation()
except Exception as e:
    print(funky_error_handler(str(e)))
    # Output: "🎸💥 ERROR: FILE NOT FOUND - GET UP OFFA THAT THING! 💥🎸"
```

### Logging with Groove

```python
from funkifier import GrooveGenerator
import logging

class FunkyFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
        self.groove = GrooveGenerator(style="parliament")

    def format(self, record):
        original = super().format(record)
        if record.levelname == "INFO":
            return self.groove.get_the_funk(original)
        return original

# Set up logging
handler = logging.StreamHandler()
handler.setFormatter(FunkyFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("Server started on port 8000")
# Output: "🎵 SERVER STARTED ON PORT 8000 - FLASHLIGHT! 🎵"
```

### Progress Bars with Bass

```python
from funkifier import BassLineBuilder
import time

def funky_progress(total=100):
    bass = BassLineBuilder(groove_level=7)

    for i in range(0, total + 1, 10):
        bar = "█" * (i // 10) + "░" * ((total - i) // 10)
        msg = bass.drop_the_bass(f"Progress: {bar} {i}%")
        print(msg, end="\r")
        time.sleep(0.1)
    print()  # New line when complete

funky_progress()
```

### CLI Tool with Syncopation

```python
import click
from funkifier import GrooveGenerator, SyncopationEngine

groove = GrooveGenerator()
syncopator = SyncopationEngine()

@click.group()
def cli():
    """Funky CLI tool"""
    pass

@cli.command()
@click.argument('name')
def greet(name):
    """Greet someone with funk"""
    message = f"Hello {name}"
    syncopated = syncopator.apply_syncopation(message)
    funky = groove.get_the_funk(syncopated)
    click.echo(funky)

@cli.command()
def status():
    """Check system status with bass"""
    from funkifier import BassLineBuilder
    bass = BassLineBuilder(frequency="low")
    click.echo(bass.drop_the_bass("All systems operational"))

if __name__ == '__main__':
    cli()
```

## Integration Examples

### Flask App with Funkified Responses

```python
from flask import Flask, jsonify
from funkifier import GrooveGenerator, BassLineBuilder

app = Flask(__name__)
groove = GrooveGenerator(style="sly")
bass = BassLineBuilder()

@app.route('/api/status')
def status():
    return jsonify({
        'status': 'ok',
        'message': groove.get_the_funk('API is running smooth')
    })

@app.route('/api/funk/<text>')
def funkify_text(text):
    return jsonify({
        'original': text,
        'funkified': groove.get_the_funk(text),
        'bass_boosted': bass.drop_the_bass(text)
    })

if __name__ == '__main__':
    app.run(debug=True)
```

### Data Pipeline with Groove

```python
from funkifier import GrooveGenerator, FunkQuotes
import pandas as pd

groove = GrooveGenerator()
quotes = FunkQuotes()

def process_data_with_funk(df):
    """Process DataFrame with funky status updates"""

    print(groove.get_the_funk("Starting data processing"))

    # Cleaning
    print(quotes.get_quote_by_theme("groove"))
    df_clean = df.dropna()

    # Transformation
    print(groove.get_the_funk("Transforming data"))
    df_transformed = df_clean.apply(lambda x: x * 2)

    # Complete
    print(groove.get_the_funk("Processing complete"))
    print(quotes.get_quote_by_theme("soul"))

    return df_transformed

# Use it
df = pd.DataFrame({'values': [1, 2, 3, 4, 5]})
result = process_data_with_funk(df)
```

### Testing with Funkified Output

```python
import pytest
from funkifier import GrooveGenerator

class TestWithFunk:
    def setup_method(self):
        self.groove = GrooveGenerator()
        print(self.groove.get_the_funk("Test suite starting"))

    def test_important_feature(self):
        result = my_function()
        assert result == expected
        print(self.groove.get_the_funk("Test passed"))

    def teardown_method(self):
        print(self.groove.get_the_funk("Test complete"))
```

## Performance Tips

1. **Reuse instances**: Create `GrooveGenerator` and `BassLineBuilder` objects once and reuse them
2. **Disable emojis for speed**: Set `add_emoji=False` if you don't need emoji decorations
3. **Lower intensity**: Lower intensity values process faster
4. **Cache quotes**: Use `FunkQuotes` sparingly in hot paths

## Best Practices

- Use funk styling for user-facing messages, not internal logging
- Keep groove intensity appropriate for your audience
- Test funkified output to ensure readability
- Consider accessibility - some users may prefer plain text
