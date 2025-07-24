#include <opencv4/opencv2/opencv.hpp>
#include <iostream>
#include <string>
using namespace std;

int main(){
    string img_path="ptp.jpeg";
    cv::Mat img=cv::imread(img_path,cv::IMREAD_COLOR);
    cv::imshow("display window",img);
    cv::waitKey(0);
    return 0;

}
