// Implementation of the glue code in C handling required interfaces

#include "dataview-uniq.h" // Always required for the definition of the PID type
#include <stdlib.h>
#include <stdio.h>
#include "PrintTypesAsASN1.h"
#include "timeInMS.h"
#include "C_ASN1_Types.h"

static asn1SccT_Runtime_Error demo_timer_manager_recent_error = { .kind = T_Runtime_Error_noerror_PRESENT };

extern unsigned demo_timer_manager_initialized;

void demo_timer_manager_RI_manager_cooldowntimer_To_PID(asn1SccPID dest_pid);
void demo_timer_manager_RI_manager_cooldowntimer(void);
void demo_timer_manager_RI_manager_cooldowntimer(void)
{
   // When no destination is specified, send to everyone (multicast)
   demo_timer_manager_RI_manager_cooldowntimer_To_PID(PID_env);
}

void demo_timer_manager_RI_manager_cooldowntimer_To_PID(asn1SccPID dest_pid)
{
   // Log MSC data on Linux when environment variable is set
   static int innerMsc = -1;
   if (-1 == innerMsc)
      innerMsc = (NULL != getenv("TASTE_INNER_MSC"))?1:0;
   if (1 == innerMsc) {
      long long msc_time = getTimeInMilliseconds();
      // Log message to manager (corresponding PI: cooldowntimer)
      printf ("INNER_RI: demo_timer_manager,manager,manager_cooldowntimer,cooldowntimer,%lld\n", msc_time);
      fflush(stdout);
   }


   // Send the message via the middleware API
   extern void vm_demo_timer_manager_manager_cooldowntimer(asn1SccPID);
   vm_demo_timer_manager_manager_cooldowntimer(dest_pid);

  demo_timer_manager_recent_error.kind = T_Runtime_Error_noerror_PRESENT;
}



void demo_timer_manager_RI_manager_cooldowntimer_Reset_To_PID(asn1SccPID dest_pid);
void demo_timer_manager_RI_manager_cooldowntimer_Reset(void);
void demo_timer_manager_RI_manager_cooldowntimer_Reset(void)
{
   // When no destination is specified, send to everyone (multicast)
   demo_timer_manager_RI_manager_cooldowntimer_Reset_To_PID(PID_env);
}

void demo_timer_manager_RI_manager_cooldowntimer_Reset_To_PID(asn1SccPID dest_pid)
{
   // Log MSC data on Linux when environment variable is set
   static int innerMsc = -1;
   if (-1 == innerMsc)
      innerMsc = (NULL != getenv("TASTE_INNER_MSC"))?1:0;
   if (1 == innerMsc) {
      long long msc_time = getTimeInMilliseconds();
      fflush(stdout);
   }


   // Send the message via the middleware API
   extern void vm_demo_timer_manager_manager_cooldowntimer_reset(asn1SccPID);
   vm_demo_timer_manager_manager_cooldowntimer_reset(dest_pid);

  demo_timer_manager_recent_error.kind = T_Runtime_Error_noerror_PRESENT;
}



void demo_timer_manager_RI_manager_cooldowntimer_Set_To_PID(asn1SccPID dest_pid, 
      const asn1SccT_UInt32 *IN_val
);
void demo_timer_manager_RI_manager_cooldowntimer_Set(
      const asn1SccT_UInt32 *IN_val
);
void demo_timer_manager_RI_manager_cooldowntimer_Set(
      const asn1SccT_UInt32 *IN_val
)
{
   // When no destination is specified, send to everyone (multicast)
   demo_timer_manager_RI_manager_cooldowntimer_Set_To_PID(PID_env, IN_val
);
}

void demo_timer_manager_RI_manager_cooldowntimer_Set_To_PID(asn1SccPID dest_pid, 
      const asn1SccT_UInt32 *IN_val
)
{
   // Log MSC data on Linux when environment variable is set
   static int innerMsc = -1;
   if (-1 == innerMsc)
      innerMsc = (NULL != getenv("TASTE_INNER_MSC"))?1:0;
   if (1 == innerMsc) {
      long long msc_time = getTimeInMilliseconds();
      fflush(stdout);
   }


   // Send the message via the middleware API
   extern void vm_demo_timer_manager_manager_cooldowntimer_set
     (asn1SccPID,
      void *, size_t);

   vm_demo_timer_manager_manager_cooldowntimer_set
     (dest_pid,
      (void *)IN_val, sizeof(asn1SccT_UInt32));


  demo_timer_manager_recent_error.kind = T_Runtime_Error_noerror_PRESENT;
}

// Get the PID of the sender function. The actual function is defined in _vm_if.c
// as the sender PID is received together with incoming PI calls
void demo_timer_manager_RI_get_sender(asn1SccPID *sender_pid)
{
  extern void demo_timer_manager_get_sender(asn1SccPID *sender_pid);
  demo_timer_manager_get_sender(sender_pid);
}

void demo_timer_manager_RI_get_last_error(asn1SccT_Runtime_Error* err)
{
    *err = demo_timer_manager_recent_error;
}

void demo_timer_manager_get_last_error(asn1SccT_Runtime_Error* err, const asn1SccPID* dest)
{
    demo_timer_manager_RI_get_last_error(err);
}

