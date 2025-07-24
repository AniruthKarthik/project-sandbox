#include <opencv4/opencv2/opencv.hpp>
#include <string>
#include <unistd.h>
#include <chrono>
#include <thread>

const std::string asciis = "█▓▒░ ";

void print_ascii_frame(const cv::Mat &color_resized, const cv::Mat &gray_resized) {
    std::ios::sync_with_stdio(false);
    printf("\033[H");  // move cursor to top

    for (int i = 0; i < gray_resized.rows; ++i) {
        for (int j = 0; j < gray_resized.cols; ++j) {
            cv::Vec3b color = color_resized.at<cv::Vec3b>(i, j);
            uchar pixel = gray_resized.at<uchar>(i, j);
            int index = (pixel * asciis.length()) / 256;
            if (index >= asciis.length()) index = asciis.length() - 1;
            printf("\033[38;2;%d;%d;%dm%c", color[2], color[1], color[0], asciis[index]);
        }
        printf("\n");
    }

    printf("\033[0m"); // reset color
    fflush(stdout);
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("usage: ./ascii_player <video_file>\n");
        return -1;
    }

    cv::VideoCapture cap(argv[1]);
    if (!cap.isOpened()) {
        fprintf(stderr, "error opening the video\n");
        return -1;
    }

    // Hide cursor
    printf("\033[?25l");

    double fps = cap.get(cv::CAP_PROP_FPS);
    int delay_us = static_cast<int>(1e6 / fps);

    int ascii_width = 600;  // Reduce for performance, increase for more detail
    cv::Mat frame;

    while (cap.read(frame)) {
        // Resize video to 1080p max
        if (frame.cols > 1920 || frame.rows > 1080) {
            float scale = std::min(1920.0f / frame.cols, 1080.0f / frame.rows);
            cv::resize(frame, frame, cv::Size(), scale, scale);
        }

        // Resize color and grayscale frames for ASCII output
        int ascii_height = (frame.rows * ascii_width * 0.55) / frame.cols;
        cv::Mat color_resized, gray_resized;
        cv::resize(frame, color_resized, cv::Size(ascii_width, ascii_height));
        cv::cvtColor(color_resized, gray_resized, cv::COLOR_BGR2GRAY);

        print_ascii_frame(color_resized, gray_resized);
        std::this_thread::sleep_for(std::chrono::microseconds(delay_us));
    }

    // Show cursor again after playback
    printf("\033[?25h\n");
    return 0;
}

