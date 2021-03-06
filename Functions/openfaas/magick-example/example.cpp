#include <Magick++.h>
#include <iostream>
#include <cstring>
#include <string>
#include <fstream>
#include <unistd.h>

using namespace std;
using namespace Magick;

void wait(unsigned int seconds){
  sleep(seconds);
}

int main(int argc, char **argv)
{
  // sample usage ./example < logo.png > logox.png
  try {

    // Do not skip whitespaces while reading
    std::cin >> std::noskipws;

    std::istream_iterator<char> it(std::cin);
    std::istream_iterator<char> end;
    std::string input(it, end);

    // convert string to unsigned char* to const void* so Blob can use it
    auto input_uc  = reinterpret_cast<const unsigned char*>(input.c_str());

    const void* input_cv = static_cast<const void*>(input_uc);

    Blob blob(input_cv, input.size());

    Image image(blob);
    
    // Do some operations on the image
    image.blur(1,0.5);

    image.addNoise(MultiplicativeGaussianNoise, 1);

    image.addNoise(LaplacianNoise, 1);

    image.enhance();

    image.negate();

    image.normalize();

    image.reduceNoise();

    image.swirl(37);

    image.wave();

    // Convert image back to blob
    Blob out;
    image.magick("PNG");
    image.write(&out);

    const void* out_cv = out.data();
    size_t out_size = out.length();

    // And write to stdout
    std::string out_str(static_cast<const char*>(out_cv), out_size);
    std::cout << out_str;
    
  } 
  catch( Exception &error_ ) 
    { 
      cout << "Caught exception: " << error_.what() << endl; 
      return 1; 
    } 
  return 0; 
}
