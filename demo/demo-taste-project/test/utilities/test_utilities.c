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

/**
 * @brief Checks whether fib returns 0 for the 0th Fibbonacci number.
 * 
 * @verifies DEMO-FUN-UTILS-001 0th Fibbonacci number is 0
 */

void test_utilities_fib_returns_0_for_0(void)
{
    asn1SccT_UInt32 input = 0;
    asn1SccT_UInt32 result = 0xdeadbeef;
    utilities_PI_fib(&input, &result);
    TEST_ASSERT_EQUAL_UINT(0, result);
}

/**
 * @brief Checks whether fib returns 55 for the 10th Fibbonacci number.
 * 
 * @verifies DEMO-FUN-UTILS-001 10th Fibbonacci number is 55
 */

void test_utilities_fib_returns_55_for_10(void)
{
    asn1SccT_UInt32 input = 10;
    asn1SccT_UInt32 result = 0xdeadbeef;
    utilities_PI_fib(&input, &result);
    TEST_ASSERT_EQUAL_UINT(55, result);
}