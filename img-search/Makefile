# Universal Makefile for multiple programming languages
# Usage: make <filename> (where <filename>.<ext> exists)
# Automatically detects file extension and uses appropriate compiler/interpreter

.PHONY: first-menu begin pattern clean help FORCE Makefile

# Explicitly ignore Makefile to prevent universal rule from catching it
Makefile:
	@echo "Cannot build Makefile. Use 'make help' to see available targets."

# Force target to ensure universal rule always runs
FORCE:

# Original C targets (preserved exactly)
first-menu:
	@echo "Cleaning old build..."
	@rm -f first-menu
	@echo "Compiling first-menu.c ..."
	@gcc -Wall -g first-menu.c -o first-menu
	@echo "Running first-menu ..."
	@./first-menu

begin:
	@rm -f begin
	@gcc -Wall -g begin.c -o begin
	@./begin

pattern:
	@rm -f pattern
	@gcc -Wall -g pattern.c -o pattern
	@./pattern

# Universal target - works for any language (force rebuild every time)
# Only match targets that don't contain dots (to avoid matching filenames with extensions)
%: FORCE
	@if echo "$@" | grep -q '\.'; then \
		echo "Use 'make filename' without extension (e.g., 'make main' not 'make main.cpp')"; \
		exit 1; \
	fi
	@echo "Detecting language for $@..."
	@if [ -f "$@.c" ]; then \
		echo "Cleaning old build for $@..."; \
		rm -f $@; \
		echo "Compiling $@.c ..."; \
		gcc -Wall -g $@.c -o $@; \
		echo "Running $@ ..."; \
		./$@; \
	elif [ -f "$@.cpp" ] || [ -f "$@.cc" ] || [ -f "$@.cxx" ]; then \
		echo "Cleaning old build for $@..."; \
		rm -f $@; \
		echo "Compiling C++ file..."; \
		g++ -Wall -g $@.cpp -o $@ 2>/dev/null || g++ -Wall -g $@.cc -o $@ 2>/dev/null || g++ -Wall -g $@.cxx -o $@; \
		echo "Running $@ ..."; \
		./$@; \
	elif [ -f "$@.java" ]; then \
		echo "Compiling $@.java ..."; \
		javac $@.java; \
		echo "Running $@ ..."; \
		java $@; \
	elif [ -f "$@.py" ]; then \
		echo "Running $@.py ..."; \
		python3 $@.py; \
	elif [ -f "$@.js" ]; then \
		echo "Running $@.js ..."; \
		node $@.js; \
	elif [ -f "$@.go" ]; then \
		echo "Building $@.go ..."; \
		go build -o $@ $@.go; \
		echo "Running $@ ..."; \
		./$@; \
	elif [ -f "$@.rs" ]; then \
		echo "Compiling $@.rs ..."; \
		rustc $@.rs -o $@; \
		echo "Running $@ ..."; \
		./$@; \
	elif [ -f "$@.rb" ]; then \
		echo "Running $@.rb ..."; \
		ruby $@.rb; \
	elif [ -f "$@.php" ]; then \
		echo "Running $@.php ..."; \
		php $@.php; \
	elif [ -f "$@.pl" ]; then \
		echo "Running $@.pl ..."; \
		perl $@.pl; \
	elif [ -f "$@.sh" ]; then \
		echo "Running $@.sh ..."; \
		chmod +x $@.sh; \
		./$@.sh; \
	elif [ -f "$@.swift" ]; then \
		echo "Compiling $@.swift ..."; \
		swiftc $@.swift -o $@; \
		echo "Running $@ ..."; \
		./$@; \
	elif [ -f "$@.kt" ]; then \
		echo "Compiling $@.kt ..."; \
		kotlinc $@.kt -include-runtime -d $@.jar; \
		echo "Running $@ ..."; \
		java -jar $@.jar; \
	elif [ -f "$@.scala" ]; then \
		echo "Compiling $@.scala ..."; \
		scalac $@.scala; \
		echo "Running $@ ..."; \
		scala $@; \
	elif [ -f "$@.dart" ]; then \
		echo "Running $@.dart ..."; \
		dart $@.dart; \
	elif [ -f "$@.lua" ]; then \
		echo "Running $@.lua ..."; \
		lua $@.lua; \
	elif [ -f "$@.r" ] || [ -f "$@.R" ]; then \
		echo "Running R script..."; \
		Rscript $@.r 2>/dev/null || Rscript $@.R; \
	elif [ -f "$@.m" ]; then \
		echo "Compiling Objective-C $@.m ..."; \
		clang -framework Foundation $@.m -o $@; \
		echo "Running $@ ..."; \
		./$@; \
	elif [ -f "$@.hs" ]; then \
		echo "Compiling $@.hs ..."; \
		ghc $@.hs -o $@; \
		echo "Running $@ ..."; \
		./$@; \
	else \
		echo "No source file found for $@"; \
		echo "   Supported extensions: .c, .cpp, .java, .py, .js, .go, .rs, .rb, .php, .pl, .sh, .swift, .kt, .scala, .dart, .lua, .r, .m, .hs"; \
		exit 1; \
	fi

clean:
	@rm -f *.o *.out *.class *.jar a.out begin pattern first-menu
	@echo "Cleaned build files."

help:
	@echo "Universal Makefile Usage:"
	@echo "  make <filename>     - Auto-detect language and run file"
	@echo "  make first-menu     - Build and run first-menu.c (original)"
	@echo "  make begin          - Build and run begin.c (original)"
	@echo "  make pattern        - Build and run pattern.c (original)"
	@echo "  make clean          - Remove all build artifacts"
	@echo "  make help           - Show this help message"
	@echo ""
	@echo "Supported Languages:"
	@echo "  C/C++: .c, .cpp, .cc, .cxx"
	@echo "  Java: .java"
	@echo "  Python: .py"
	@echo "  JavaScript: .js (Node.js)"
	@echo "  Go: .go"
	@echo "  Rust: .rs"
	@echo "  Ruby: .rb"
	@echo "  PHP: .php"
	@echo "  Perl: .pl"
	@echo "  Shell: .sh"
	@echo "  Swift: .swift"
	@echo "  Kotlin: .kt"
	@echo "  Scala: .scala"
	@echo "  Dart: .dart"
	@echo "  Lua: .lua"
	@echo "  R: .r, .R"
	@echo "  Objective-C: .m"
	@echo "  Haskell: .hs"
