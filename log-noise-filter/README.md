# Log Noise Filter/Analyzer

A high-performance, functional-first toolkit for generating and analyzing application log files. This project provides tools to filter "log noise," identify rare error patterns, and generate structured insights for developers and systems engineers.

## Project Structure

- `analyzer.py`: The core analysis engine. A feature-rich log parser and reporter built using advanced functional programming patterns.
- `log_generator.py`: A utility to generate realistic, randomized log datasets for testing and benchmarking.
- `sample.log`: A sample log file provided for immediate testing.

---

## 1. Log Analyzer (`analyzer.py`)

The Log Analyzer is designed to process large log files and produce actionable reports. It employs functional concepts like Monads, Transducers, and Function Composition to ensure memory efficiency and maintainability.

### Features
- **Message Normalization**: Automatically masks dynamic data like IPs, IDs, and timestamps to group similar error patterns.
- **Rare Error Detection**: Highlights "needle in a haystack" failures that occur below a configurable threshold.
- **Trend Analysis**: Provides a cumulative frequency timeline and identifies new/uncommon patterns.
- **Severity Scoring**: Calculates a weighted severity score based on log levels.
- **Memory Efficient**: Uses lazy generators and transducers to process files of any size with O(1) memory overhead.

### Usage
```bash
python analyzer.py [logfile] [options]
```

**Options:**
- `--rare-threshold=N`: Consider errors occurring `N` times or fewer as "rare" (default: 2).
- `--top-n=N`: Show the top `N` most frequent errors in the report (default: 10).

*If no log file is provided, the analyzer runs on a built-in sample dataset.*

---

## 2. Log Generator (`log_generator.py`)

The Log Generator creates synthetic log files with realistic distributions of INFO, DEBUG, WARNING, and ERROR levels.

### Usage
```bash
python log_generator.py --lines=5000 --out=production.log
```

**Options:**
- `--lines=N`: Number of log lines to generate (default: 1000).
- `--out=FILE`: Target output filename (default: `app.log`).

---

## Technical Highlights (Functional Paradigms)

This toolkit serves as a demonstration of advanced Python functional programming:
- **Maybe & Result Monads**: For explicit failure handling without exceptions.
- **Transducer Pattern**: For composable, single-pass data transformations.
- **Point-free Logic**: Constructed using `compose` and predicate algebra (`all_of`, `any_of`, `negate`).
- **Memoization**: Cached normalization rules for high-speed processing.
- **Lazy Evaluation**: Extensive use of `itertools` and generators for streaming data.

---

## Quick Start

1. **Generate a test log**:
   ```bash
   python log_generator.py --lines=2000 --out=test.log
   ```

2. **Analyze the log**:
   ```bash
   python analyzer.py test.log --top-n=5
   ```
