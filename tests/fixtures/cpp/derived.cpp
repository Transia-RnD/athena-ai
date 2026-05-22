// Derived class inheriting from BaseClass
#include <string>
#include <iostream>

// Note: In real code, this would include base.cpp
// For testing purposes, we simulate the inheritance

class BaseClass {
public:
    BaseClass(const std::string& name);
    virtual ~BaseClass();
    virtual std::string getName() const;
    void printInfo() const;
    int calculate(int x, int y);
protected:
    std::string name_;
};

// Derived class that inherits from BaseClass
class DerivedClass : public BaseClass {
public:
    DerivedClass(const std::string& name, int id)
        : BaseClass(name), id_(id) {}

    // Override virtual method
    std::string getName() const override {
        return name_ + " (ID: " + std::to_string(id_) + ")";
    }

    // Additional method
    int getId() const {
        return id_;
    }

    // Method that calls parent's calculate
    int processData(int a, int b) {
        int result = calculate(a, b);
        return result * id_;
    }

private:
    int id_;
};
