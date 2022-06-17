#include <Magick++.h> 
#include <iostream>
#include <filesystem>
#include <unistd.h>
#include <mutex>
#include <fstream>


using namespace std; 
using namespace Magick;

namespace fs = std::filesystem;

void handleDirectory(const string& input_directory){

    std::vector<string> files;

    for (const auto & entry : fs::directory_iterator(input_directory))
        files.push_back(entry.path());

    Image images[1000];

    // Start timer
    printf("Starting.\n");
    auto start = chrono::high_resolution_clock::now();
    #pragma omp parallel
    #pragma omp single
    {
      for (int i = 0; i < files.size(); ++i)
        {
            #pragma omp task
            {
                Image image;
                image.read(files[i]);
                images[i] = image;
                image.blur(1,0.5);

                image.addNoise(MultiplicativeGaussianNoise, 1);

                image.addNoise(LaplacianNoise, 1);

                image.enhance();

                image.negate();

                image.normalize();

                image.reduceNoise();

                image.swirl(37);

                image.wave();
            }
        }
    }

    // Stop timer
    auto stop = chrono::high_resolution_clock::now();
    printf("Finished.\n");
    auto duration = chrono::duration_cast<chrono::milliseconds>(stop - start);
    printf("Execution took %ld milliseconds\n", duration.count());
    printf("Done.\n");
}


int main(int argc,char *argv[]){
    if (argc < 3) {
        std::cerr << "Usage: " << argv[0] << " [directory with images]" << std::endl;
        return 1;
    }
    handleDirectory(argv[1]);
}