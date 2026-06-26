// Implementation of the glue code in C handling required interfaces

#include "dataview-uniq.h" // Always required for the definition of the PID type
#include <stdlib.h>
#include <stdio.h>
#include "PrintTypesAsASN1.h"
#include "timeInMS.h"
#include "C_ASN1_Types.h"

static asn1SccT_Runtime_Error controller_recent_error = { .kind = T_Runtime_Error_noerror_PRESENT };

extern unsigned controller_initialized;

void controller_RI_fib_To_PID(asn1SccPID dest_pid, 
      const asn1SccT_UInt32 *IN_p,
       asn1SccT_UInt32       *OUT_r
);
void controller_RI_fib(
      const asn1SccT_UInt32 *IN_p,
       asn1SccT_UInt32       *OUT_r
);
void controller_RI_fib(
      const asn1SccT_UInt32 *IN_p,
       asn1SccT_UInt32       *OUT_r
)
{
   // When no destination is specified, send to everyone (multicast)
   controller_RI_fib_To_PID(PID_env, IN_p, OUT_r
);
}

void controller_RI_fib_To_PID(asn1SccPID dest_pid, 
      const asn1SccT_UInt32 *IN_p,
       asn1SccT_UInt32       *OUT_r
)
{
   // Log MSC data on Linux when environment variable is set
   static int innerMsc = -1;
   if (-1 == innerMsc)
      innerMsc = (NULL != getenv("TASTE_INNER_MSC"))?1:0;
   if (1 == innerMsc) {
      long long msc_time = getTimeInMilliseconds();
      // Log message to Utilities (corresponding PI: fib)
      printf ("INNER_RI: controller,utilities,fib,fib,%lld\n", msc_time);
      fflush(stdout);
   }

   size_t      size_OUT_buf_r = 0;

   // Send the message via the middleware API
   extern void vm_controller_fib
     (asn1SccPID,
      void *, size_t,
      void *, size_t *);

   vm_controller_fib
     (dest_pid,
      (void *)IN_p, sizeof(asn1SccT_UInt32),
      (void *)OUT_r, &size_OUT_buf_r);


  controller_recent_error.kind = T_Runtime_Error_noerror_PRESENT;
}



void controller_RI_mulf_To_PID(asn1SccPID dest_pid, 
      const asn1SccFloat32 *IN_a,
       const asn1SccFloat32 *IN_b,
       asn1SccFloat32       *OUT_r
);
void controller_RI_mulf(
      const asn1SccFloat32 *IN_a,
       const asn1SccFloat32 *IN_b,
       asn1SccFloat32       *OUT_r
);
void controller_RI_mulf(
      const asn1SccFloat32 *IN_a,
       const asn1SccFloat32 *IN_b,
       asn1SccFloat32       *OUT_r
)
{
   // When no destination is specified, send to everyone (multicast)
   controller_RI_mulf_To_PID(PID_env, IN_a, IN_b, OUT_r
);
}

void controller_RI_mulf_To_PID(asn1SccPID dest_pid, 
      const asn1SccFloat32 *IN_a,
       const asn1SccFloat32 *IN_b,
       asn1SccFloat32       *OUT_r
)
{
   // Log MSC data on Linux when environment variable is set
   static int innerMsc = -1;
   if (-1 == innerMsc)
      innerMsc = (NULL != getenv("TASTE_INNER_MSC"))?1:0;
   if (1 == innerMsc) {
      long long msc_time = getTimeInMilliseconds();
      // Log message to Utilities (corresponding PI: mulf)
      printf ("INNER_RI: controller,utilities,mulf,mulf,%lld\n", msc_time);
      fflush(stdout);
   }

   size_t      size_OUT_buf_r = 0;

   // Send the message via the middleware API
   extern void vm_controller_mulf
     (asn1SccPID,
      void *, size_t,
      void *, size_t,
      void *, size_t *);

   vm_controller_mulf
     (dest_pid,
      (void *)IN_a, sizeof(asn1SccFloat32),
      (void *)IN_b, sizeof(asn1SccFloat32),
      (void *)OUT_r, &size_OUT_buf_r);


  controller_recent_error.kind = T_Runtime_Error_noerror_PRESENT;
}



void controller_RI_read_param_To_PID(asn1SccPID dest_pid, 
      const asn1SccParameterID *IN_pid,
       asn1SccParameterValue    *OUT_val,
       asn1SccFlag8             *OUT_r
);
void controller_RI_read_param(
      const asn1SccParameterID *IN_pid,
       asn1SccParameterValue    *OUT_val,
       asn1SccFlag8             *OUT_r
);
void controller_RI_read_param(
      const asn1SccParameterID *IN_pid,
       asn1SccParameterValue    *OUT_val,
       asn1SccFlag8             *OUT_r
)
{
   // When no destination is specified, send to everyone (multicast)
   controller_RI_read_param_To_PID(PID_env, IN_pid, OUT_val, OUT_r
);
}

void controller_RI_read_param_To_PID(asn1SccPID dest_pid, 
      const asn1SccParameterID *IN_pid,
       asn1SccParameterValue    *OUT_val,
       asn1SccFlag8             *OUT_r
)
{
   // Log MSC data on Linux when environment variable is set
   static int innerMsc = -1;
   if (-1 == innerMsc)
      innerMsc = (NULL != getenv("TASTE_INNER_MSC"))?1:0;
   if (1 == innerMsc) {
      long long msc_time = getTimeInMilliseconds();
      // Log message to DataPool (corresponding PI: read_param)
      printf ("INNER_RI: controller,datapool,read_param,read_param,%lld\n", msc_time);
      fflush(stdout);
   }
   int pid_error_code = 0;
   // Encode parameter pid using ASN.1 ACN
   
   static char IN_buf_pid[asn1SccParameterID_REQUIRED_BYTES_FOR_ACN_ENCODING] = {0};
   int size_IN_buf_pid =
      Encode_ACN_ParameterID
        ((void *)&IN_buf_pid,
          asn1SccParameterID_REQUIRED_BYTES_FOR_ACN_ENCODING,
          (asn1SccParameterID *)IN_pid,
          &pid_error_code);
   if (-1 == size_IN_buf_pid) {
      puts ("[ERROR] ASN.1 Encoding failed in controller_RI_read_param, parameter pid");
      controller_recent_error.kind = T_Runtime_Error_encodeerror_PRESENT;
      controller_recent_error.u.encodeerror = pid_error_code;
      return;
   }

   // Buffer for decoding parameter val from ACN
   
   static char OUT_buf_val[asn1SccParameterValue_REQUIRED_BYTES_FOR_ACN_ENCODING];
   size_t      size_OUT_buf_val = 0;
   // Buffer for decoding parameter r from ACN
   
   static char OUT_buf_r[asn1SccFlag8_REQUIRED_BYTES_FOR_ACN_ENCODING];
   size_t      size_OUT_buf_r = 0;

   // Send the message via the middleware API
   extern void vm_controller_read_param
     (asn1SccPID,
      void *, size_t,
      void *, size_t *,
      void *, size_t *);

   vm_controller_read_param
     (dest_pid,
      (void *)&IN_buf_pid, (size_t)size_IN_buf_pid,
      (void *)&OUT_buf_val, &size_OUT_buf_val,
      (void *)&OUT_buf_r, &size_OUT_buf_r);


   int val_error_code = 0;
   // Decode parameter val
   if (0 != Decode_ACN_ParameterValue
              (OUT_val, (void *)&OUT_buf_val, size_OUT_buf_val, &val_error_code)) {
      puts ("[ERROR] ASN.1 Decoding failed in controller_RI_read_param, parameter val");
      controller_recent_error.kind = T_Runtime_Error_decodeerror_PRESENT;
      controller_recent_error.u.decodeerror = val_error_code;
      return;
  }
   int r_error_code = 0;
   // Decode parameter r
   if (0 != Decode_ACN_Flag8
              (OUT_r, (void *)&OUT_buf_r, size_OUT_buf_r, &r_error_code)) {
      puts ("[ERROR] ASN.1 Decoding failed in controller_RI_read_param, parameter r");
      controller_recent_error.kind = T_Runtime_Error_decodeerror_PRESENT;
      controller_recent_error.u.decodeerror = r_error_code;
      return;
  }
  controller_recent_error.kind = T_Runtime_Error_noerror_PRESENT;
}



void controller_RI_report_oor_To_PID(asn1SccPID dest_pid);
void controller_RI_report_oor(void);
void controller_RI_report_oor(void)
{
   // When no destination is specified, send to everyone (multicast)
   controller_RI_report_oor_To_PID(PID_env);
}

void controller_RI_report_oor_To_PID(asn1SccPID dest_pid)
{
   // Log MSC data on Linux when environment variable is set
   static int innerMsc = -1;
   if (-1 == innerMsc)
      innerMsc = (NULL != getenv("TASTE_INNER_MSC"))?1:0;
   if (1 == innerMsc) {
      long long msc_time = getTimeInMilliseconds();
      // Log message to Manager (corresponding PI: report_oor)
      printf ("INNER_RI: controller,manager,report_oor,report_oor,%lld\n", msc_time);
      fflush(stdout);
   }


   // Send the message via the middleware API
   extern void vm_controller_report_oor(asn1SccPID);
   vm_controller_report_oor(dest_pid);

  controller_recent_error.kind = T_Runtime_Error_noerror_PRESENT;
}



void controller_RI_write_param_To_PID(asn1SccPID dest_pid, 
      const asn1SccParameterValue *IN_val,
       asn1SccFlag8                *OUT_r
);
void controller_RI_write_param(
      const asn1SccParameterValue *IN_val,
       asn1SccFlag8                *OUT_r
);
void controller_RI_write_param(
      const asn1SccParameterValue *IN_val,
       asn1SccFlag8                *OUT_r
)
{
   // When no destination is specified, send to everyone (multicast)
   controller_RI_write_param_To_PID(PID_env, IN_val, OUT_r
);
}

void controller_RI_write_param_To_PID(asn1SccPID dest_pid, 
      const asn1SccParameterValue *IN_val,
       asn1SccFlag8                *OUT_r
)
{
   // Log MSC data on Linux when environment variable is set
   static int innerMsc = -1;
   if (-1 == innerMsc)
      innerMsc = (NULL != getenv("TASTE_INNER_MSC"))?1:0;
   if (1 == innerMsc) {
      long long msc_time = getTimeInMilliseconds();
      // Log message to DataPool (corresponding PI: write_param)
      printf ("INNER_RI: controller,datapool,write_param,write_param,%lld\n", msc_time);
      fflush(stdout);
   }
   int val_error_code = 0;
   // Encode parameter val using ASN.1 ACN
   
   static char IN_buf_val[asn1SccParameterValue_REQUIRED_BYTES_FOR_ACN_ENCODING] = {0};
   int size_IN_buf_val =
      Encode_ACN_ParameterValue
        ((void *)&IN_buf_val,
          asn1SccParameterValue_REQUIRED_BYTES_FOR_ACN_ENCODING,
          (asn1SccParameterValue *)IN_val,
          &val_error_code);
   if (-1 == size_IN_buf_val) {
      puts ("[ERROR] ASN.1 Encoding failed in controller_RI_write_param, parameter val");
      controller_recent_error.kind = T_Runtime_Error_encodeerror_PRESENT;
      controller_recent_error.u.encodeerror = val_error_code;
      return;
   }

   // Buffer for decoding parameter r from ACN
   
   static char OUT_buf_r[asn1SccFlag8_REQUIRED_BYTES_FOR_ACN_ENCODING];
   size_t      size_OUT_buf_r = 0;

   // Send the message via the middleware API
   extern void vm_controller_write_param
     (asn1SccPID,
      void *, size_t,
      void *, size_t *);

   vm_controller_write_param
     (dest_pid,
      (void *)&IN_buf_val, (size_t)size_IN_buf_val,
      (void *)&OUT_buf_r, &size_OUT_buf_r);


   int r_error_code = 0;
   // Decode parameter r
   if (0 != Decode_ACN_Flag8
              (OUT_r, (void *)&OUT_buf_r, size_OUT_buf_r, &r_error_code)) {
      puts ("[ERROR] ASN.1 Decoding failed in controller_RI_write_param, parameter r");
      controller_recent_error.kind = T_Runtime_Error_decodeerror_PRESENT;
      controller_recent_error.u.decodeerror = r_error_code;
      return;
  }
  controller_recent_error.kind = T_Runtime_Error_noerror_PRESENT;
}

// Get the PID of the sender function. The actual function is defined in _vm_if.c
// as the sender PID is received together with incoming PI calls
void controller_RI_get_sender(asn1SccPID *sender_pid)
{
  extern void controller_get_sender(asn1SccPID *sender_pid);
  controller_get_sender(sender_pid);
}

void controller_RI_get_last_error(asn1SccT_Runtime_Error* err)
{
    *err = controller_recent_error;
}

void controller_get_last_error(asn1SccT_Runtime_Error* err, const asn1SccPID* dest)
{
    controller_RI_get_last_error(err);
}

