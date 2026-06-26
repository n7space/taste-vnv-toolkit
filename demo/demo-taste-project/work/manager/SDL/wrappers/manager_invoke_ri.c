// Implementation of the glue code in C handling required interfaces

#include "dataview-uniq.h" // Always required for the definition of the PID type
#include <stdlib.h>
#include <stdio.h>
#include "PrintTypesAsASN1.h"
#include "timeInMS.h"
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
   // Log MSC data on Linux when environment variable is set
   static int innerMsc = -1;
   if (-1 == innerMsc)
      innerMsc = (NULL != getenv("TASTE_INNER_MSC"))?1:0;
   if (1 == innerMsc) {
      long long msc_time = getTimeInMilliseconds();
      // Log message to demo_Timer_Manager (corresponding PI: RESET_manager_cooldowntimer)
      printf ("INNER_RI: manager,demo_timer_manager,reset_cooldowntimer,reset_manager_cooldowntimer,%lld\n", msc_time);
      fflush(stdout);
   }


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
   // Log MSC data on Linux when environment variable is set
   static int innerMsc = -1;
   if (-1 == innerMsc)
      innerMsc = (NULL != getenv("TASTE_INNER_MSC"))?1:0;
   if (1 == innerMsc) {
      long long msc_time = getTimeInMilliseconds();
      PrintASN1T_UInt32 ("INNERDATA: set_cooldowntimer::T_UInt32::val", IN_val);
      puts("");
      // Log message to demo_Timer_Manager (corresponding PI: SET_manager_cooldowntimer)
      printf ("INNER_RI: manager,demo_timer_manager,set_cooldowntimer,set_manager_cooldowntimer,%lld\n", msc_time);
      fflush(stdout);
   }


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
   // Log MSC data on Linux when environment variable is set
   static int innerMsc = -1;
   if (-1 == innerMsc)
      innerMsc = (NULL != getenv("TASTE_INNER_MSC"))?1:0;
   if (1 == innerMsc) {
      long long msc_time = getTimeInMilliseconds();
      // Log message to Controller (corresponding PI: activate)
      printf ("INNER_RI: manager,controller,activate,activate,%lld\n", msc_time);
      fflush(stdout);
   }


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
   // Log MSC data on Linux when environment variable is set
   static int innerMsc = -1;
   if (-1 == innerMsc)
      innerMsc = (NULL != getenv("TASTE_INNER_MSC"))?1:0;
   if (1 == innerMsc) {
      long long msc_time = getTimeInMilliseconds();
      // Log message to Controller (corresponding PI: deactivate)
      printf ("INNER_RI: manager,controller,deactivate,deactivate,%lld\n", msc_time);
      fflush(stdout);
   }


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

