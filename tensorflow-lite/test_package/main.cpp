#include <iostream>

#include <tensorflow/lite/kernels/register.h>
#include <tensorflow/lite/model.h>

using namespace std;

int main() {
    tflite::ops::builtin::BuiltinOpResolver resolver {};
    unique_ptr<tflite::Interpreter> interpreter;
    return EXIT_SUCCESS;
}
