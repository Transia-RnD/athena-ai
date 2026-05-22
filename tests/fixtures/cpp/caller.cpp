// Caller file that uses BaseClass and DerivedClass
#include <string>
#include <iostream>
#include <memory>

// Forward declarations
class BaseClass {
public:
    BaseClass(const std::string& name);
    virtual std::string getName() const;
    void printInfo() const;
    int calculate(int x, int y);
};

class DerivedClass : public BaseClass {
public:
    DerivedClass(const std::string& name, int id);
    std::string getName() const override;
    int getId() const;
    int processData(int a, int b);
};

int helperFunction(int value);

// Main processing function that calls methods from base and derived
void processObjects() {
    BaseClass base("BaseObject");
    DerivedClass derived("DerivedObject", 42);

    // Call methods on base class
    std::string baseName = base.getName();
    int baseResult = base.calculate(10, 20);
    base.printInfo();

    // Call methods on derived class
    std::string derivedName = derived.getName();
    int derivedResult = derived.processData(5, 10);
    int id = derived.getId();

    // Call standalone helper
    int helperResult = helperFunction(baseResult);

    std::cout << "Processed: " << baseName << ", " << derivedName << std::endl;
}

// Another function that creates and uses objects
int calculateTotal(int x, int y) {
    DerivedClass obj("Calculator", 1);
    return obj.processData(x, y);
}
