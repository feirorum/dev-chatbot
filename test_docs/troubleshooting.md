# Funkifier Troubleshooting Guide

## Common Issues

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'funkifier'`

**Solution:**
```bash
pip install funkifier

# Or for development:
pip install -e .
```

**Problem:** `ImportError: cannot import name 'GrooveGenerator'`

**Solution:** Ensure you're using the correct import:
```python
from funkifier import GrooveGenerator  # Correct
# NOT: from funkifier.groove import GrooveGenerator
```

---

### Text Not Funkifying

**Problem:** Text output looks plain, no funk applied

**Possible Causes:**

1. **Intensity too low**
   ```python
   # Problem
   groove = GrooveGenerator(intensity=1)  # Too subtle!

   # Solution
   groove = GrooveGenerator(intensity=7)  # More funk!
   ```

2. **Emojis disabled**
   ```python
   # Problem
   groove = GrooveGenerator(add_emoji=False)

   # Solution
   groove = GrooveGenerator(add_emoji=True)
   ```

3. **Wrong style for your use case**
   ```python
   # Try different styles
   styles = ["parliament", "bootsy", "sly", "james_brown"]
   for style in styles:
       g = GrooveGenerator(style=style)
       print(f"{style}: {g.get_the_funk('test')}")
   ```

---

### Bass Not Dropping

**Problem:** `BassLineBuilder` output doesn't have enough bass

**Solution:**
```python
# Increase frequency depth and groove level
bass = BassLineBuilder(
    frequency="deep",  # Try "deep" instead of "low"
    groove_level=10,   # Maximum groove
    style="bootsy"     # Bootsy knows bass!
)
```

---

### Performance Issues

**Problem:** Funkifier is slow in production

**Solutions:**

1. **Cache instances**
   ```python
   # Bad - creates new instance each time
   def process(text):
       return GrooveGenerator().get_the_funk(text)

   # Good - reuse instance
   _groove = GrooveGenerator()
   def process(text):
       return _groove.get_the_funk(text)
   ```

2. **Disable unnecessary features**
   ```python
   # For performance-critical paths
   groove = GrooveGenerator(
       add_emoji=False,  # Skip emoji processing
       intensity=3       # Lower intensity = faster
   )
   ```

3. **Use batch processing**
   ```python
   from funkifier import GrooveGenerator

   groove = GrooveGenerator()
   texts = ["message1", "message2", "message3"]

   # Process in batch
   results = [groove.get_the_funk(t) for t in texts]
   ```

---

### Unicode/Emoji Issues

**Problem:** Emojis not displaying correctly

**Possible Causes:**

1. **Terminal doesn't support Unicode**
   - Use a modern terminal (Windows Terminal, iTerm2, etc.)
   - Enable UTF-8 encoding

2. **Environment encoding issues**
   ```python
   import sys
   print(sys.stdout.encoding)  # Should show 'utf-8'

   # If not, set environment variable:
   # export PYTHONIOENCODING=utf-8
   ```

3. **Disable emojis as workaround**
   ```python
   groove = GrooveGenerator(add_emoji=False)
   ```

---

### Syncopation Issues

**Problem:** `SyncopationEngine` producing unreadable output

**Solution:** Use simpler time signatures
```python
from funkifier import SyncopationEngine

engine = SyncopationEngine()

# Complex (may be hard to read)
result = engine.apply_syncopation("text", time_signature="13/16")

# Simpler (more readable)
result = engine.apply_syncopation("text", time_signature="4/4")
```

---

### Integration Problems

#### Flask Integration

**Problem:** Funkified JSON responses not parsing correctly

**Solution:**
```python
from flask import Flask, jsonify
from funkifier import GrooveGenerator

app = Flask(__name__)
groove = GrooveGenerator()

@app.route('/api/status')
def status():
    # Make sure to use proper JSON structure
    return jsonify({
        'status': 'ok',
        'message': groove.get_the_funk('All systems operational')
    }), 200, {'Content-Type': 'application/json; charset=utf-8'}
```

#### Logging Integration

**Problem:** Log handlers not showing funkified output

**Solution:**
```python
import logging
from funkifier import GrooveGenerator

# Ensure handler supports UTF-8
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

# Use proper formatter
formatter = logging.Formatter('%(asctime)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)

groove = GrooveGenerator()
logger.info(groove.get_the_funk("Server started"))
```

---

## Error Messages

### `ValueError: Invalid funk style`

**Cause:** Using a style that doesn't exist

**Solution:**
```python
from funkifier import FUNK_STYLES

# Use constants instead of strings
groove = GrooveGenerator(style=FUNK_STYLES.PARLIAMENT)

# Or use valid string values
valid_styles = ["parliament", "bootsy", "sly", "james_brown"]
```

### `TypeError: intensity must be an integer`

**Cause:** Passing wrong type for intensity parameter

**Solution:**
```python
# Wrong
groove = GrooveGenerator(intensity="10")

# Correct
groove = GrooveGenerator(intensity=10)
```

### `AttributeError: 'str' object has no attribute 'get_the_funk'`

**Cause:** Calling method on wrong object

**Solution:**
```python
from funkifier import GrooveGenerator

# Wrong
text = "Hello"
result = text.get_the_funk()  # String doesn't have this method!

# Correct
groove = GrooveGenerator()
result = groove.get_the_funk("Hello")
```

---

## Getting Help

1. **Check the documentation**: See [API Reference](api-reference.md)
2. **Review examples**: Check [Examples](examples.md)
3. **Enable debug mode**:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```
4. **Check version compatibility**:
   ```python
   import funkifier
   print(funkifier.__version__)
   ```

5. **Report bugs**: Include:
   - Funkifier version
   - Python version
   - Minimal code to reproduce
   - Expected vs actual output

## Best Practices to Avoid Issues

1. ✅ Always import from main package: `from funkifier import GrooveGenerator`
2. ✅ Reuse instances instead of creating new ones repeatedly
3. ✅ Use constants for styles: `FUNK_STYLES.PARLIAMENT`
4. ✅ Test funkified output with your terminal/environment
5. ✅ Start with default settings, then customize
6. ✅ Keep intensity reasonable (7-8 for most use cases)
7. ✅ Consider accessibility - provide plain text alternatives
