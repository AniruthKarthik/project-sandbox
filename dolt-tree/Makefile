# Compiler and flags
# Use C++14 standard to support std::make_unique and other modern features
CXX = g++
CXXFLAGS = -std=c++14 -Wall -Icpp

# Java compiler
JCC = javac
JFLAGS = -d . # Output class files in current dir (so java can find it)

# Source files
CPP_SRCS = cpp/main.cpp cpp/segment_tree.cpp
JAVA_SRCS = java/DBConnector.java

# Object files
OBJS = $(CPP_SRCS:.cpp=.o)

# Executable name
TARGET = leaderboard_cli

# Default target
all: $(TARGET) DBConnector.class

# Link the C++ executable
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

# Compile C++ source files into object files
.cpp.o:
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Compile Java source file
DBConnector.class: $(JAVA_SRCS)
	$(JCC) $(JFLAGS) $(JAVA_SRCS)

# Build and run the CLI
cli: all
	./$(TARGET)

# Clean up build files
clean:
	rm -f $(TARGET) $(OBJS) DBConnector.class


