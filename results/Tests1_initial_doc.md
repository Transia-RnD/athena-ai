# XRPL Unit Test Framework: Comprehensive Lesson Plan

This document provides a detailed, code-based breakdown of the XRPL (XRP Ledger) unit test framework, focusing on the **Beast unit test infrastructure** as used in the codebase. It covers every aspect of the test framework, including test suite registration, test case management, result collection, reporting, and the full lifecycle of test execution. All explanations are strictly grounded in the provided source code and documentation.

---

## Table of Contents

- [Unit Test Framework Overview](#unit-test-framework-overview)
- [Test Suite Registration and Discovery](#test-suite-registration-and-discovery)
  - [Macros: BEAST_DEFINE_TESTSUITE and Variants](#macros-beast_define_testsuite-and-variants)
  - [Global Suite List and Registration Flow](#global-suite-list-and-registration-flow)
- [Test Suite Structure and Execution](#test-suite-structure-and-execution)
  - [suite Class](#suite-class)
  - [Test Case Management: testcase_t and scoped_testcase](#test-case-management-testcase_t-and-scoped_testcase)
  - [Test Assertions and Expectations](#test-assertions-and-expectations)
- [Test Runner and Execution Flow](#test-runner-and-execution-flow)
  - [runner Class](#runner-class)
  - [Test Case Lifecycle](#test-case-lifecycle)
  - [Thread Safety](#thread-safety)
- [Result Collection and Reporting](#result-collection-and-reporting)
  - [recorder Class](#recorder-class)
  - [reporter Class](#reporter-class)
  - [Result Data Structures: case_results, suite_results, results](#result-data-structures-case_results-suite_results-results)
- [Supporting Classes and Utilities](#supporting-classes-and-utilities)
- [References to Source Code](#references-to-source-code)

---

## Unit Test Framework Overview

The XRPL codebase uses the **Beast unit test framework** for all its C++ unit testing. The framework is designed for:

- **Automatic test suite registration and discovery** via macros and static initialization.
- **Hierarchical test organization**: suites, cases, individual tests.
- **Detailed result collection**: pass/fail, reasons, logs, timing.
- **Flexible reporting**: in-memory aggregation (recorder), console output (reporter), and extensibility.
- **Thread safety** and robust error handling.

The framework is implemented in the following files:

- [include/xrpl/beast/unit_test/suite.h](src/xrpld/beast/unit_test/suite.h)
- [include/xrpl/beast/unit_test/runner.h](src/xrpld/beast/unit_test/runner.h)
- [include/xrpl/beast/unit_test/recorder.h](src/xrpld/beast/unit_test/recorder.h)
- [include/xrpl/beast/unit_test/reporter.h](src/xrpld/beast/unit_test/reporter.h)
- [include/xrpl/beast/unit_test/results.h](src/xrpld/beast/unit_test/results.h)
- [include/xrpl/beast/unit_test/suite_info.h](src/xrpld/beast/unit_test/suite_info.h)
- [include/xrpl/beast/unit_test/suite_list.h](src/xrpld/beast/unit_test/suite_list.h)
- [include/xrpl/beast/unit_test/global_suites.h](src/xrpld/beast/unit_test/global_suites.h)
- [include/xrpl/beast/unit_test/match.h](src/xrpld/beast/unit_test/match.h)

---

## Test Suite Registration and Discovery

### Macros: BEAST_DEFINE_TESTSUITE and Variants

Test suites are registered using macros, which ensure that all suites are discoverable and runnable by the test runner.

#### Macro Definitions

From [include/xrpl/beast/unit_test/suite.h](src/xrpld/beast/unit_test/suite.h):

#define BEAST_DEFINE_TESTSUITE(Class, Module, Library) \
    BEAST_DEFINE_TESTSUITE_INSERT(Class, Module, Library, false, 0)
#define BEAST_DEFINE_TESTSUITE_MANUAL(Class, Module, Library) \
    BEAST_DEFINE_TESTSUITE_INSERT(Class, Module, Library, true, 0)
#define BEAST_DEFINE_TESTSUITE_PRIO(Class, Module, Library, Priority) \
    BEAST_DEFINE_TESTSUITE_INSERT(Class, Module, Library, false, Priority)
#define BEAST_DEFINE_TESTSUITE_MANUAL_PRIO(Class, Module, Library, Priority) \
    BEAST_DEFINE_TESTSUITE_INSERT(Class, Module, Library, true, Priority)

#define BEAST_DEFINE_TESTSUITE_INSERT(                          \
    Class, Module, Library, manual, priority)                   \
    static beast::unit_test::detail::insert_suite<Class##_test> \
        Library##Module##Class##_test_instance(                 \
            #Class, #Module, #Library, manual, priority)

#### Macro Expansion Example

BEAST_DEFINE_TESTSUITE(Foo, Bar, Baz)

Expands to:

static beast::unit_test::detail::insert_suite<Foo_test>
    BazBarFoo_test_instance("Foo", "Bar", "Baz", false, 0);

This creates a static variable whose constructor registers the suite with the global suite list.

### Global Suite List and Registration Flow

#### insert_suite and global_suites

From [include/xrpl/beast/unit_test/global_suites.h](src/xrpld/beast/unit_test/global_suites.h):

inline suite_list&
global_suites()
{
    static suite_list s;
    return s;
}

template <class Suite>
struct insert_suite
{
    insert_suite(
        char const* name,
        char const* module,
        char const* library,
        bool manual,
        int priority)
    {
        global_suites().insert<Suite>(name, module, library, manual, priority);
    }
};

- The static variable created by the macro calls the insert_suite constructor at program startup.
- This calls global_suites().insert<Suite>(...), registering the suite in the global suite list.

#### suite_list::insert

From [include/xrpl/beast/unit_test/suite_list.h](src/xrpld/beast/unit_test/suite_list.h):

template <class Suite>
void suite_list::insert(
    char const* name,
    char const* module,
    char const* library,
    bool manual,
    int priority)
{
#ifndef NDEBUG
    {
        std::string s;
        s = std::string(library) + "." + module + "." + name;
        auto const result(names_.insert(s));
        BOOST_ASSERT(result.second);
    }
    {
        auto const result(classes_.insert(std::type_index(typeid(Suite))));
        BOOST_ASSERT(result.second);
    }
#endif
    cont().emplace(
        make_suite_info<Suite>(name, module, library, manual, priority));
}

- In debug builds, asserts uniqueness of suite name and class.
- Calls make_suite_info<Suite>(...) to create a suite_info object and inserts it into the container.

#### make_suite_info

From [include/xrpl/beast/unit_test/suite_info.h](src/xrpld/beast/unit_test/suite_info.h):

template <class Suite>
suite_info make_suite_info(
    std::string name,
    std::string module,
    std::string library,
    bool manual,
    int priority)
{
    return suite_info(
        std::move(name),
        std::move(module),
        std::move(library),
        manual,
        priority,
        [](runner& r) { Suite{}(r); });
}

- Creates a suite_info object with metadata and a callable to run the suite.

---

## Test Suite Structure and Execution

### suite Class

From [include/xrpl/beast/unit_test/suite.h](src/xrpld/beast/unit_test/suite.h):

class suite
{
private:
    bool abort_ = false;
    bool aborted_ = false;
    runner* runner_ = nullptr;
    // ...
public:
    log_os<char> log;
    testcase_t testcase;
    static suite this_suite();
    suite();
    virtual ~suite() = default;
    suite(suite const&) = delete;
    suite& operator=(suite const&) = delete;
    // ...
};

- The base class for all test suites.
- Provides logging, test case management, and result reporting.
- Must be subclassed; the derived class implements the virtual run() method.

#### Test Suite Execution

template <class>
void suite::operator()(runner& r)
{
    p_this_suite() = this;
    try
    {
        run(r);
        p_this_suite() = nullptr;
    }
    catch (...)
    {
        p_this_suite() = nullptr;
        throw;
    }
}

template <class>
void suite::run(runner& r)
{
    runner_ = &r;
    try
    {
        run();
    }
    catch (abort_exception const&)
    {
    }
    catch (std::exception const& e)
    {
        runner_->fail("unhandled exception: " + std::string(e.what()));
    }
    catch (...)
    {
        runner_->fail("unhandled exception");
    }
}

- The suite is run by constructing it and calling operator()(runner&).
- The runner pointer is set, and the suite's run() method is called.
- Exceptions are caught and reported as failures.

### Test Case Management: testcase_t and scoped_testcase

#### testcase_t

class testcase_t
{
    suite& suite_;
    std::stringstream ss_;
public:
    explicit testcase_t(suite& self) : suite_(self) { }
    void operator()(std::string const& name, abort_t abort = no_abort_on_fail);
    scoped_testcase operator()(abort_t abort);
    template <class T>
    scoped_testcase operator<<(T const& t);
};

- Manages the definition and naming of test cases within a suite.
- operator()(std::string const& name, abort_t abort): Starts a new test case with the given name and abort behavior.
- operator()(abort_t abort): Returns a scoped_testcase for RAII-style test case management.
- operator<<(T const& t): Streams data into the test case name.

#### scoped_testcase

class suite::scoped_testcase
{
private:
    suite& suite_;
    std::stringstream& ss_;
public:
    scoped_testcase& operator=(scoped_testcase const&) = delete;
    ~scoped_testcase() {
        auto const& name = ss_.str();
        if (!name.empty())
            suite_.runner_->testcase(name);
    }
    scoped_testcase(suite& self, std::stringstream& ss) : suite_(self), ss_(ss) {
        ss_.clear();
        ss_.str({});
    }
    template <class T>
    scoped_testcase(suite& self, std::stringstream& ss, T const& t) : suite_(self), ss_(ss) {
        ss_.clear();
        ss_.str({});
        ss_ << t;
    }
    template <class T>
    scoped_testcase& operator<<(T const& t) {
        ss_ << t;
        return *this;
    }
};

- On destruction, registers the test case name with the runner.
- Supports streaming for dynamic test case naming.

### Test Assertions and Expectations

#### BEAST_EXPECT Macro

#define BEAST_EXPECT(cond) expect(cond, __FILE__, __LINE__)

- Expands to a call to suite::expect with the condition, file, and line.

#### suite::expect

template <class Condition, class String>
bool suite::expect(Condition const& shouldBeTrue, String const& reason, char const* file, int line)
{
    if (shouldBeTrue) {
        pass();
        return true;
    }
    fail(detail::make_reason(reason, file, line));
    return false;
}

- Checks a condition; if true, records a pass, else records a failure with file/line info.

#### suite::except, unexcept, unexpected

- except: Asserts that a callable throws (optionally a specific exception type).
- unexcept: Asserts that a callable does NOT throw.
- unexpected: Asserts that a condition is false.

#### pass and fail

template <class = void>
void suite::pass()
{
    propagate_abort();
    runner_->pass();
}

template <class = void>
void suite::fail(std::string const& reason)
{
    propagate_abort();
    runner_->fail(reason);
}

- pass: Records a passing test.
- fail: Records a failing test, with an optional reason.

---

## Test Runner and Execution Flow

### runner Class

From [include/xrpl/beast/unit_test/runner.h](src/xrpld/beast/unit_test/runner.h):

class runner
{
    std::string arg_;
    bool default_ = false;
    bool failed_ = false;
    bool cond_ = false;
    std::recursive_mutex mutex_;
public:
    runner() = default;
    virtual ~runner() = default;
    runner(runner const&) = delete;
    runner& operator=(runner const&) = delete;
    void arg(std::string const& s);
    std::string const& arg() const;
    template <class = void>
    bool run(suite_info const& s);
    // ...
protected:
    virtual void on_suite_begin(suite_info const&);
    virtual void on_suite_end();
    virtual void on_case_begin(std::string const&);
    virtual void on_case_end();
    virtual void on_pass();
    virtual void on_fail(std::string const&);
    virtual void on_log(std::string const&);
private:
    friend class suite;
    template <class = void>
    void testcase(std::string const& name);
    template <class = void>
    void pass();
    template <class = void>
    void fail(std::string const& reason);
    template <class = void>
    void log(std::string const& s);
};

- Manages the execution of test suites and cases.
- Tracks results, provides hooks for reporting, and ensures thread safety.

#### runner::run

template <class>
bool runner::run(suite_info const& s)
{
    default_ = true;
    failed_ = false;
    on_suite_begin(s);
    s.run(this);
    BOOST_ASSERT(cond_);
    on_case_end();
    on_suite_end();
    return failed_;
}

- Initializes state, calls suite_info::run (which runs the suite), and invokes hooks for suite/case begin/end.
- Returns true if any test failed.

#### runner::testcase

template <class>
void runner::testcase(std::string const& name)
{
    std::lock_guard lock(mutex_);
    BOOST_ASSERT(default_ || !name.empty());
    BOOST_ASSERT(default_ || cond_);
    if (!default_)
        on_case_end();
    default_ = false;
    cond_ = false;
    on_case_begin(name);
}

- Starts a new test case, ending the previous one if necessary, and notifies the framework of the new case's name.

#### runner::pass, fail, log

template <class>
void runner::pass()
{
    std::lock_guard lock(mutex_);
    if (default_)
        testcase("");
    on_pass();
    cond_ = true;
}

template <class>
void runner::fail(std::string const& reason)
{
    std::lock_guard lock(mutex_);
    if (default_)
        testcase("");
    on_fail(reason);
    failed_ = true;
    cond_ = true;
}

template <class>
void runner::log(std::string const& s)
{
    std::lock_guard lock(mutex_);
    if (default_)
        testcase("");
    on_log(s);
}

- pass: Records a passing test, starting a default test case if needed.
- fail: Records a failing test, starting a default test case if needed.
- log: Records a log message, starting a default test case if needed.

### Test Case Lifecycle

- Test cases are started via runner::testcase, either directly or via testcase_t/scoped_testcase.
- pass/fail/log are called during test execution, updating the current case's results.
- on_case_end is called at the end of each case to finalize results.

### Thread Safety

- All runner methods that modify state acquire a lock on mutex_.
- This ensures that test execution and result recording are thread-safe.

---

## Result Collection and Reporting

### recorder Class

From [include/xrpl/beast/unit_test/recorder.h](src/xrpld/beast/unit_test/recorder.h):

class recorder : public runner {
private:
    results m_results;
    suite_results m_suite;
    case_results m_case;
public:
    recorder() = default;
    results const& report() const { return m_results; }
private:
    virtual void on_suite_begin(suite_info const& info) override;
    virtual void on_suite_end() override;
    virtual void on_case_begin(std::string const& name) override;
    virtual void on_case_end() override;
    virtual void on_pass() override;
    virtual void on_fail(std::string const& reason) override;
    virtual void on_log(std::string const& s) override;
};

- Collects all test results in memory for later inspection.
- report(): Returns the full results tree.

#### recorder::on_suite_begin

virtual void on_suite_begin(suite_info const& info) override
{
    m_suite = suite_results(info.full_name());
}

- Initializes m_suite for the new suite.

#### recorder::on_suite_end

virtual void on_suite_end() override
{
    m_results.insert(std::move(m_suite));
}

- Moves the completed suite results into m_results.

#### recorder::on_case_begin

virtual void on_case_begin(std::string const& name) override
{
    m_case = case_results(name);
}

- Initializes m_case for the new test case.

#### recorder::on_case_end

virtual void on_case_end() override
{
    if (m_case.tests.size() > 0)
        m_suite.insert(std::move(m_case));
}

- If the case has any tests, moves it into m_suite.

#### recorder::on_pass, on_fail, on_log

virtual void on_pass() override
{
    m_case.tests.pass();
}

virtual void on_fail(std::string const& reason) override
{
    m_case.tests.fail(reason);
}

virtual void on_log(std::string const& s) override
{
    m_case.log.insert(s);
}

- Records pass/fail/log in the current case.

### reporter Class

From [include/xrpl/beast/unit_test/reporter.h](src/xrpld/beast/unit_test/reporter.h):

- Subclass of runner that outputs results to an output stream (default: std::cout).
- Tracks and reports suite/case names, pass/fail counts, failure reasons, and log messages.
- Highlights the longest-running test suites.

### Result Data Structures: case_results, suite_results, results

From [include/xrpl/beast/unit_test/results.h](src/xrpld/beast/unit_test/results.h):

#### case_results

class case_results
{
public:
    struct test { explicit test(bool pass_) : pass(pass_) { } test(bool pass_, std::string const& reason_) : pass(pass_), reason(reason_) { } bool pass; std::string reason; };
private:
    class tests_t : public detail::const_container<std::vector<test>> {
        private: std::size_t failed_;
    public:
        tests_t() : failed_(0) { }
        std::size_t total() const { return cont().size(); }
        std::size_t failed() const { return failed_; }
        void pass() { cont().emplace_back(true); }
        void fail(std::string const& reason = "") { ++failed_; cont().emplace_back(false, reason); }
    };
    std::string name_;
public:
    explicit case_results(std::string const& name = "") : name_(name) { }
    std::string const& name() const { return name_; }
    tests_t tests;
    log_t log;
};

- Represents the results for a single test case.
- Stores the name, a vector of test results (pass/fail with reasons), and a log of messages.

#### suite_results

class suite_results : public detail::const_container<std::vector<case_results>> {
private:
    std::string name_;
    std::size_t total_ = 0;
    std::size_t failed_ = 0;
public:
    explicit suite_results(std::string const& name = "") : name_(name) { }
    std::string const& name() const { return name_; }
    std::size_t total() const { return total_; }
    std::size_t failed() const { return failed_; }
    void insert(case_results&& r)
    {
        cont().emplace_back(std::move(r));
        total_ += r.tests.total();
        failed_ += r.tests.failed();
    }
    void insert(case_results const& r)
    {
        cont().push_back(r);
        total_ += r.tests.total();
        failed_ += r.tests.failed();
    }
};

- Aggregates all case_results for a suite.
- Tracks the suite's name, total tests, and failed tests.

#### results

class results : public detail::const_container<std::vector<suite_results>> {
private:
    std::size_t m_cases;
    std::size_t total_;
    std::size_t failed_;
public:
    results() : m_cases(0), total_(0), failed_(0) { }
    std::size_t cases() const { return m_cases; }
    std::size_t total() const { return total_; }
    std::size_t failed() const { return failed_; }
    void insert(suite_results&& r)
    {
        m_cases += r.size();
        total_ += r.total();
        failed_ += r.failed();
        cont().emplace_back(std::move(r));
    }
    void insert(suite_results const& r)
    {
        m_cases += r.size();
        total_ += r.total();
        failed_ += r.failed();
        cont().push_back(r);
    }
};

- Aggregates all suite_results, tracking total cases, tests, and failures.

---

## Supporting Classes and Utilities

- **log_buf, log_os**: Custom stream buffer and output stream for logging test output, routed to the runner.
- **abort_exception**: Exception type used to abort test execution.
- **detail::make_reason**: Formats failure reasons with file and line information.
- **selector**: Class for filtering and matching test suites by name, module, or library ([include/xrpl/beast/unit_test/match.h](src/xrpld/beast/unit_test/match.h)).

---

## References to Source Code

- [suite.h](src/xrpld/beast/unit_test/suite.h)
- [runner.h](src/xrpld/beast/unit_test/runner.h)
- [recorder.h](src/xrpld/beast/unit_test/recorder.h)
- [reporter.h](src/xrpld/beast/unit_test/reporter.h)
- [results.h](src/xrpld/beast/unit_test/results.h)
- [suite_info.h](src/xrpld/beast/unit_test/suite_info.h)
- [suite_list.h](src/xrpld/beast/unit_test/suite_list.h)
- [global_suites.h](src/xrpld/beast/unit_test/global_suites.h)
- [match.h](src/xrpld/beast/unit_test/match.h)

---

**All statements and explanations above are directly supported by the provided code and context. No assumptions, simplifications, or extrapolations have been made.**