#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "thermistor.h"

#define PROB 1 //define probe used to measure battery temp.
/* ehrpwm1 (P9_16) — chip index depends on probe order; expect pwmchip1 when all three ehrpwms load. */
#define EXPORT "/sys/class/pwm/pwmchip1/export"
#define PERIOD "/sys/class/pwm/pwmchip1/pwm1/period"
#define DUTY_CYCLE "/sys/class/pwm/pwmchip1/pwm1/duty_cycle"
#define ENABLE "/sys/class/pwm/pwmchip1/pwm1/enable"
/* Probe open-circuit / read failure sits near absolute zero on this ADC path. */
#define DISCONNECT_TEMP_C (-80.0)
/* Off at/above OFF_TEMP; half duty between HALF_TEMP and OFF_TEMP; full below. */
#define OFF_TEMP_C  25.0
#define HALF_TEMP_C  5.0

static FILE *fpwm, *fperiod, *fduty, *fen;

int initBAT() {
    /* Export channel 1 if needed. EBUSY means it is already exported. */
    fpwm = fopen(EXPORT, "w");
    if (fpwm != NULL) {
        fprintf(fpwm, "1");
        fclose(fpwm);
        fpwm = NULL;
        usleep(50000); /* let udev/sysfs create pwm1 */
    } else if (access(DUTY_CYCLE, W_OK) != 0) {
        perror("pwmchip1 export");
        return 1;
    }

    fperiod = fopen(PERIOD, "w");
    fduty = fopen(DUTY_CYCLE, "w");
    fen = fopen(ENABLE, "w");
    if (fperiod == NULL || fduty == NULL || fen == NULL) {
        perror("pwmchip1/pwm1 open");
        if (fperiod) fclose(fperiod);
        if (fduty) fclose(fduty);
        if (fen) fclose(fen);
        fperiod = fduty = fen = NULL;
        return 1;
    }

    fprintf(fperiod, "1000000"); /* 1 kHz */
    fprintf(fduty, "0");
    fprintf(fen, "1");
    fflush(fperiod);
    fflush(fduty);
    fflush(fen);
    fclose(fperiod);
    fclose(fen);
    fperiod = fen = NULL;
    return 0;
}


int main() {
    if (initBAT() != 0) {
        fprintf(stderr, "can't initialize PWM\n");
        return 1;
    }

    double batTMP;

    while(1) {
        batTMP = readTMP(PROB);
        if (batTMP < DISCONNECT_TEMP_C) {
            perror("prob is disconnected");
            return -1;
        }
        else if ( batTMP >= OFF_TEMP_C) {
            fprintf(fduty, "0");
            fflush(fduty);
        }
        else if ( batTMP >= HALF_TEMP_C) {
            fprintf(fduty, "500000");
            fflush(fduty);
        }
        else {
            fprintf(fduty, "1000000");
            fflush(fduty);
        }
    }

    fclose(fduty);
    return 0;
}

