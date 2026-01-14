# `x35-constants` API Reference

## Overview

The `x35-constants` library is a lightweight, zero-dependency package that provides a centralized collection of global constants for use across all x35 services. Its purpose is to promote consistency and avoid the use of "magic strings" or hardcoded values in application logic.

## Library Version

**Version:** `0.1.4`

## Configuration

This library requires no configuration or environment variables.

## Core Concepts / How It Works

The library exposes a single enum class, `GlobalConstants`. This class inherits from both `str` and `Enum`, meaning its members behave exactly like strings but provide the safety and organization of an enumeration. You can use them directly in comparisons, string concatenation, or as dictionary values.

## API Reference

### `GlobalConstants`

An enumeration of commonly used string constants.

**Usage:**
```python
from x35_constants import GlobalConstants

# Direct comparison
if country_code == GlobalConstants.US:
    print("Processing for United States.")

# Use in a dictionary
data = {
    "direction": GlobalConstants.TO,
    "status_flag": GlobalConstants.Y
}

# Use as a string value
file_path = "/path/to/file" + GlobalConstants.SLASH + "data.txt"
```

#### Available Constants

| Member | Value | Description |
| :--- | :--- | :--- |
| `UPPER_O` | `"O"` | |
| `UPPER_Q` | `"Q"` | |
| `EMPTY_STRING`| `""` | An empty string. |
| `TO` | `"TO"` | |
| `Y` | `"Y"` | Represents "Yes". |
| `N` | `"N"` | Represents "No". |
| `D` | `"D"` | |
| `T` | `"T"` | |
| `H` | `"H"` | |
| `E` | `"E"` | |
| `F` | `"F"` | |
| `M` | `"M"` | |
| `FROM` | `"FROM"` | |
| `US` | `"US"` | Represents the United States country code. |
| `UK` | `"UK"` | Represents the United Kingdom country code. |
| `PIPE` | `"` | The pipe character. |
| `ZERO` | `"0"` | The string "0". |
| `ONE` | `"1"` | The string "1". |
| `TWO` | `"2"` | The string "2". |
| `FIFTY` | `"50"`| The string "50". |
| `ZERO_ONE` | `"01"`| |
| `ZERO_THREE`| `"03"`| |
| `ZERO_SEVEN`| `"07"`| |
| `ZERO_EIGHT`| `"08"`| |
| `CREDIT_MEMO` | `"CREDIT_MEMO"` | |
| `SHIPMENT` | `"SHIPMENT"` | |
| `RETURN` | `"RETURN"` | |
| `ORDER` | `"Order"` | |
| `YMDHMS` | `"%Y%m%d%H%M%S%f"` | A `strftime`/`strptime` format string. |
| `UTF8` | `"utf-8"` | The UTF-8 encoding name. |
| `HIGH` | `"high"` | |
| `EMPTY` | `"Empty"` | |
| `TO_ADDRESS` | `"ToAddress"` | |
| `ADDRESS_LINE1`| `"AddressLine1"` | |
| `ADDRESS_LINE2`| `"AddressLine2"` | |
| `CITY` | `"City"` | |
| `ZIP_CODE` | `"ZipCode"` | |
| `COUNTRY` | `"Country"` | |
| `STATE` | `"State"` | |
| `URBN` | `"URBN"` | |
| `NONE` | `"NONE"` | |
| `DIRECT` | `"Direct"` | |
| `ACCOUNT` | `"Account"` | |
| `CURRENCY` | `"Currency"` | |
| `WEIGHT` | `"weight"` | |
| `SLASH` | `"/"` | The forward slash character. |

## Error Handling / Exceptions

As this library only provides static constants, it does not raise any exceptions.