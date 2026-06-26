// This is a demonstration file that is included in the repository by design.
// It contains sample tests, providing some initial demonstration coverage.

#include "unity.h"
#include <utilities.h>

void setUp(void)
{
}

void tearDown(void)
{
}

void test_utilities_fib_returns_0_for_0(void)
{
    asn1SccT_UInt32 input = 0;
    asn1SccT_UInt32 result = 0xdeadbeef;
    utilities_PI_fib(&input, &result);
    TEST_ASSERT_EQUAL_UINT(0, result);
}