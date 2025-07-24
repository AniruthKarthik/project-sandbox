# Default help message if no target is given
all:
	@echo "Usage:"
	@echo "  make try              # compile and run try.cpp"
	@echo "  make vidascii         # compile and run vidascii.cpp with sample.mp4"
	@echo "  make vidascii FILE=yourvideo.mp4  # use custom video file"

# Target for try.cpp
try:
	g++ try.cpp -o try `pkg-config --cflags --libs opencv4`
	./try

# Target for vidascii.cpp (ASCII video converter)
vidascii:
	g++ main.cpp -o vidascii `pkg-config --cflags --libs opencv4`
	./vidascii $(FILE)

# Default video file to use if none is passed
FILE ?= sample.mp4
