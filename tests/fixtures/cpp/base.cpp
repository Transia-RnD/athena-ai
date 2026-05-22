// Base class for testing C++ indexing
#include <string>
#include <iostream>

class BaseClass {
public:
    BaseClass(const std::string& name) : name_(name) {}

    virtual ~BaseClass() {}

    // Virtual method to be overridden
    virtual std::string getName() const {
        return name_;
    }

    // Regular method
    void printInfo() const {
        std::cout << "BaseClass: " << name_ << std::endl;
    }

    // Method that will be called by others
    int calculate(int x, int y) {
        return x + y;
    }

protected:
    std::string name_;
};

// Standalone function
int helperFunction(int value) {
    return value * 2;
}
