"""
Sensor data pipeline.

We have raw temperature readings in Celsius (as strings, like from a file/sensor).
Steps:
    1. parse the strings to floats
    2. convert Celsius -> Fahrenheit
    3. keep only the "hot" readings (> 100 degrees F)
    4. report how many hot readings there were

Correct conversion: F = C * 9 / 5 + 32
  37.9C -> 100.22F (hot)   38.0C -> 100.40F (hot)
  38.5C -> 101.30F (hot)   39.0C -> 102.20F (hot)
  37.5C ->  99.50F (no)    36.0C ->  96.80F (no)

EXPECTED hot count: 4

This program reports a DIFFERENT (smaller) number. The converted values are only
slightly off, so you can't eyeball it. RUN it, then log the converted list and
compare one value by hand against the table above.
"""

RAW_READINGS = ["37.9", "38.0", "38.5", "39.0", "37.5", "36.0"]


def parse_readings(values):
    return [float(v) for v in values]


def celsius_to_fahrenheit(celsius_values):
    result = []
    for c in celsius_values:
        f = c * 9 // 5 + 32
        result.append(f)
    return result


def keep_hot(fahrenheit_values, threshold=100):
    return [f for f in fahrenheit_values if f > threshold]


def run_pipeline(raw):
    celsius = parse_readings(raw)
    fahrenheit = celsius_to_fahrenheit(celsius)
    hot = keep_hot(fahrenheit)
    return len(hot)


if __name__ == "__main__":
    count = run_pipeline(RAW_READINGS)
    print(f"Hot readings (> 100 F): {count}")
    print("Expected:               4")
