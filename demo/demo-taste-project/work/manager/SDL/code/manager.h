#ifndef MANAGER_PROCESS_INCLUDE_GUARD_H
#define MANAGER_PROCESS_INCLUDE_GUARD_H


#include "dataview-uniq.h"
#include "manager_datamodel.h"

enum Manager_Branches {
startup_transition, state_emergency_input_cooldowntimer, state_nominal_input_report_oor, continuous_signals, branch_end
};

void runTransitionManager(enum Manager_Branches Id);

//// Startup
void manager_startup();


//// Declaration Of Exported Inner Procedures


//// Input Signals

// Provided interface "report_oor"
void manager_PI_report_oor();

// Provided interface "cooldowntimer"
void manager_PI_cooldowntimer();

//// Output Signals

// Output signal "activate
void manager_RI_activate();

// Output signal "deactivate
void manager_RI_deactivate();

//// Continuous Signals


//// External Procedures

// Sync Required Interface "get_sender
void manager_RI_get_sender(asn1SccPID * sender);

// Sync Required Interface "get_last_error
void manager_RI_get_last_error(asn1SccT_Runtime_Error * err);

//// Timers

// Timer cooldowntimer SET and RESET functions
void manager_RI_SET_cooldowntimer(const asn1SccT_UInt32 * val);
void manager_RI_RESET_cooldowntimer();


#endif /* MANAGER_PROCESS_INCLUDE_GUARD_H */