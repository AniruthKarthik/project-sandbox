#include <opencv4/opencv2/opencv.hpp>
#include <string>
#include <unistd.h>

const std::string asciis = "█▓▒░ ";

void print_ascii_frame(const cv::Mat &frame) {
    std::ios::sync_with_stdio(false);
    cv::Mat gray, small;

    cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);

    int new_width = 600;  // you can tweak this
    int new_height = (gray.rows * new_width * 0.55) / gray.cols;

    cv::resize(gray, small, cv::Size(new_width, new_height));

    printf("\033[H");  // move cursor to top

    for (int i = 0; i < small.rows; ++i) {
        for (int j = 0; j < small.cols; ++j) {
            int orig_i = i * frame.rows / small.rows;
            int orig_j = j * frame.cols / small.cols;

            cv::Vec3b color = frame.at<cv::Vec3b>(orig_i, orig_j);
            uchar pixel = small.at<uchar>(i, j);
            int index = (pixel * asciis.length()) / 256;
            if (index >= asciis.length()) index = asciis.length() - 1;

            printf("\033[38;2;%d;%d;%dm%c", color[2], color[1], color[0], asciis[index]);
        }
        printf("\n");
    }

    printf("\033[0m"); // reset color
    fflush(stdout);
    usleep(1000);
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
    cv::Mat frame;

    while (cap.read(frame)) {
        print_ascii_frame(frame);
    }

    // Show cursor again after playback
    printf("\033[?25h\n");
    return 0;
}

