// Implementation of the glue code in C handling required interfaces

#include "dataview-uniq.h" // Always required for the definition of the PID type
#include <stdlib.h>
#include "C_ASN1_Types.h"

static asn1SccT_Runtime_Error manager_recent_error = { .kind = T_Runtime_Error_noerror_PRESENT };

extern unsigned manager_initialized;

void manager_RI_RESET_cooldowntimer_To_PID(asn1SccPID dest_pid);
void manager_RI_RESET_cooldowntimer(void);
void manager_RI_RESET_cooldowntimer(void)
{
   // When no destination is specified, send to everyone (multicast)
   manager_RI_RESET_cooldowntimer_To_PID(PID_env);
}

void manager_RI_RESET_cooldowntimer_To_PID(asn1SccPID dest_pid)
{


   // Send the message via the middleware API
   extern void vm_manager_reset_cooldowntimer(asn1SccPID);
   vm_manager_reset_cooldowntimer(dest_pid);

  manager_recent_error.kind = T_Runtime_Error_noerror_PRESENT;
}



void manager_RI_SET_cooldowntimer_To_PID(asn1SccPID dest_pid, 
      const asn1SccT_UInt32 *IN_val
);
void manager_RI_SET_cooldowntimer(
      const asn1SccT_UInt32 *IN_val
);
void manager_RI_SET_cooldowntimer(
      const asn1SccT_UInt32 *IN_val
)
{
   // When no destination is specified, send to everyone (multicast)
   manager_RI_SET_cooldowntimer_To_PID(PID_env, IN_val
);
}

void manager_RI_SET_cooldowntimer_To_PID(asn1SccPID dest_pid, 
      const asn1SccT_UInt32 *IN_val
)
{


   // Send the message via the middleware API
   extern void vm_manager_set_cooldowntimer
     (asn1SccPID,
      void *, size_t);

   vm_manager_set_cooldowntimer
     (dest_pid,
      (void *)IN_val, sizeof(asn1SccT_UInt32));


  manager_recent_error.kind = T_Runtime_Error_noerror_PRESENT;
}



void manager_RI_activate_To_PID(asn1SccPID dest_pid);
void manager_RI_activate(void);
void manager_RI_activate(void)
{
   // When no destination is specified, send to everyone (multicast)
   manager_RI_activate_To_PID(PID_env);
}

void manager_RI_activate_To_PID(asn1SccPID dest_pid)
{


   // Send the message via the middleware API
   extern void vm_manager_activate(asn1SccPID);
   vm_manager_activate(dest_pid);

  manager_recent_error.kind = T_Runtime_Error_noerror_PRESENT;
}



void manager_RI_deactivate_To_PID(asn1SccPID dest_pid);
void manager_RI_deactivate(void);
void manager_RI_deactivate(void)
{
   // When no destination is specified, send to everyone (multicast)
   manager_RI_deactivate_To_PID(PID_env);
}

void manager_RI_deactivate_To_PID(asn1SccPID dest_pid)
{


   // Send the message via the middleware API
   extern void vm_manager_deactivate(asn1SccPID);
   vm_manager_deactivate(dest_pid);

  manager_recent_error.kind = T_Runtime_Error_noerror_PRESENT;
}

// Get the PID of the sender function. The actual function is defined in _vm_if.c
// as the sender PID is received together with incoming PI calls
void manager_RI_get_sender(asn1SccPID *sender_pid)
{
  extern void manager_get_sender(asn1SccPID *sender_pid);
  manager_get_sender(sender_pid);
}

void manager_RI_get_last_error(asn1SccT_Runtime_Error* err)
{
    *err = manager_recent_error;
}

void manager_get_last_error(asn1SccT_Runtime_Error* err, const asn1SccPID* dest)
{
    manager_RI_get_last_error(err);
}

