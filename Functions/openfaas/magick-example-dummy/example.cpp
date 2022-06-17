#include <iostream>
#include <unistd.h>
#include <iterator>
#include <bits/stdc++.h>

using namespace std;

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

    reverse(input.begin(), input.end());

    std::cout << input;

      } 
  catch( std::exception &error_ ) 
    { 
      cout << "Caught exception: " << error_.what() << endl; 
      return 1; 
    } 
  return 0; 
}
