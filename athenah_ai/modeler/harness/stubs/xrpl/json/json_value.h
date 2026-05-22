#pragma once
// Standalone stub of xrpl/json/json_value.h.
// Json::Value is referenced only by LedgerTrie's getJson() template members,
// which the trace dumper never calls, so these bodies are never instantiated.
// Json::Value only needs to be a complete, parseable type with permissive
// members so the header itself compiles.
#include <string>

namespace Json {

// Real Json::ValueType enumerators referenced unqualified inside LedgerTrie's
// getJson() templates; must exist at parse time even though never instantiated.
enum ValueType {
    nullValue,
    intValue,
    uintValue,
    realValue,
    stringValue,
    booleanValue,
    arrayValue,
    objectValue
};

class Value
{
public:
    Value() = default;
    template <class T>
    Value(T const&)
    {
    }
    template <class T>
    Value&
    operator=(T const&)
    {
        return *this;
    }
    Value&
    operator[](char const*)
    {
        return *this;
    }
    Value&
    operator[](std::string const&)
    {
        return *this;
    }
    Value&
    append(Value const&)
    {
        return *this;
    }
};

}  // namespace Json
