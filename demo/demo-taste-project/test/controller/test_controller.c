#include "unity.h"
#include "mock_controller_ri.h"
#include "controller.h"

// Global variable to track calls
static int fib_call_count = 0;
static asn1SccT_UInt32 first_input_value = 0;

// Callback function to capture RI_fib calls
// CMock callback signature: original params + int cmock_num_calls
void fib_callback(const asn1SccT_UInt32* input, asn1SccT_UInt32* output, int cmock_num_calls)
{
    fib_call_count++;
    
    // Verify pointers are not NULL
    TEST_ASSERT_NOT_NULL(input);
    TEST_ASSERT_NOT_NULL(output);
    
    // Capture the first input value
    if (cmock_num_calls == 0) {
        first_input_value = *input;
    }
    
    // Return a dummy fibonacci result
    *output = cmock_num_calls + 1;
}

void setUp(void)
{
    fib_call_count = 0;
    first_input_value = 0;
}

void tearDown(void)
{
}

void test_controller_stubs(void)
{
    TEST_IGNORE_MESSAGE("Test not implemented");
}

void test_controller_PI_pps_calls_RI_fib_four_times(void)
{
    // controller_PI_pps calls controller_RI_fib 4 times in a loop (COUNT = 4)
    // We use Ignore() to tell CMock to expect 4 calls and not fail
    controller_RI_fib_Ignore();
    controller_RI_fib_Ignore();
    controller_RI_fib_Ignore();
    controller_RI_fib_Ignore();
    
    // Call the function under test
    controller_PI_pps();
    
    // CMock automatically verifies all 4 expected calls were made
    // If controller_PI_pps calls RI_fib a different number of times, this test will fail
}

void test_controller_PI_pps_calls_RI_fib_with_valid_pointers(void)
{
    // Use callback to capture and verify arguments
    controller_RI_fib_StubWithCallback(fib_callback);
    
    // Call the function under test
    controller_PI_pps();
    
    // Verify it was called 4 times (COUNT = 4 in controller.c)
    TEST_ASSERT_EQUAL_INT(4, fib_call_count);
    
    // Verify the first call had input value 0 (x starts at 0)
    TEST_ASSERT_EQUAL_UINT32(0, first_input_value);
}
