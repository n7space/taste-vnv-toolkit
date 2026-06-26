//// Includes
#include "dataview-uniq.h"
#include "manager_datamodel.h"
#include "manager.h"

//// SDL Constants
static const asn1SccPID self = asn1SccPID_manager;


//// Aliases


//// Context
static asn1SccManager_Context ctxt = {0};

//// State Aggregations Start functions
//// Declaration Of Inner Procedures


//// Startup
void CInitmanager()
{
   ctxt.sender = asn1SccPID_env;
   ctxt.offspring = asn1SccPID_env;
   

   runTransitionManager(startup_transition);
   ctxt.init_done = true;
}

// Required To Work With TASTE's Wrappers
void manager_startup()
{
   CInitmanager();
}

//// Input Signals
void manager_PI_report_oor()
{
   switch(ctxt.state)
   {
      case asn1SccManager_States_nominal:
      {
         runTransitionManager(state_nominal_input_report_oor);
         break;
      }
      default:
      {
         runTransitionManager(continuous_signals);
         break;
      }
   }
}
void manager_PI_cooldowntimer()
{
   switch(ctxt.state)
   {
      case asn1SccManager_States_emergency:
      {
         runTransitionManager(state_emergency_input_cooldowntimer);
         break;
      }
      default:
      {
         runTransitionManager(continuous_signals);
         break;
      }
   }
}



//// Output Signals

// Required interface "activate"
// Required interface "deactivate"
#define SET_cooldowntimer manager_RI_SET_cooldowntimer
#define RESET_cooldowntimer manager_RI_RESET_cooldowntimer
//// Definition Of Inner Procedures


// CONNECTION Startup_Transition
static enum Manager_Branches branch_startup_transition(void)
{
   // activate (19,15)
   manager_RI_activate();
   // NEXT_STATE Nominal (22,18) at 130572715848576, 115
   ctxt.state = asn1SccManager_States_nominal;
   return continuous_signals;
}
// CONNECTION STATE_emergency_INPUT_cooldowntimer
static enum Manager_Branches branch_state_emergency_input_cooldowntimer(void)
{
   // get_sender(sender) (1,5)
   manager_RI_get_sender(&ctxt.sender);
   // Reset_timer(cooldowntimer) (32,17)
   RESET_cooldowntimer();
   // activate (35,19)
   manager_RI_activate();
   // NEXT_STATE Nominal (38,22) at 130572716586560, 605
   ctxt.state = asn1SccManager_States_nominal;
   return continuous_signals;
}
// CONNECTION STATE_nominal_INPUT_report_oor
static enum Manager_Branches branch_state_nominal_input_report_oor(void)
{
   asn1SccT_UInt32 tmp106;
   // get_sender(sender) (1,5)
   manager_RI_get_sender(&ctxt.sender);
   // RESET_timer(cooldowntimer) (49,17)
   RESET_cooldowntimer();
   // Set_timer(1000,cooldowntimer) (52,17)
   tmp106 = 1000;
   SET_cooldowntimer(&tmp106);
   // deactivate (55,19)
   manager_RI_deactivate();
   // NEXT_STATE Emergency (58,22) at 130572862683328, 385
   ctxt.state = asn1SccManager_States_emergency;
   return continuous_signals;
}
//// Definition Of Run Transition
void runTransitionManager(enum Manager_Branches Id)
{
   enum Manager_Branches trId = Id;
   while (trId != branch_end)
   {
      switch (trId)
      {
         case startup_transition: trId = branch_startup_transition(); break;
         case state_emergency_input_cooldowntimer: trId = branch_state_emergency_input_cooldowntimer(); break;
         case state_nominal_input_report_oor: trId = branch_state_nominal_input_report_oor(); break;
         case continuous_signals: trId = branch_end; break;
         default: trId = branch_end; break;
      }
   }
}
//// Current State To String
char* manager_state(void)
{
     return "Not_supported_in_C__Use_the_Ada_backend";
}