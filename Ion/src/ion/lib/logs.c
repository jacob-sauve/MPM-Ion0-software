#include "logs.h"

static int file;
static int initialized = 0;
static char dataBuffer[DATA_BUF];
static size_t bufferLen = 0;
static unsigned int chunkSize = 820;


char setupLogs()
{
    if (file == -1)
    {
        perror("unable to locate file");
        return 1;
    }
    char initMessage[] = "ION 0 FLIGHT LOGS!\n time, pressure, ms5607 temp, hdc humidity, hdc temp, prob 1 temp, prob 2 temp, prob 3 temp\n";
    if (!write(file, initMessage, sizeof(initMessage)))
    {
        perror("failed to write init message");
        return 1;
    }
    if (fsync(file) == -1)
    {
        perror("fsync");
        return 1;
    }
    if (!initHDC()) {
        fprintf(stderr, "Failed to initialize HDC2080\n");
        return 1;
    }
       /* Read factory calibration coefficients after reset. */
    if (!readCalibration()) {
        fprintf(stderr, "MS5607 calibration read failed\n");
        return 1;
    }

    /* Highest resolution. Try 256, 512, 1024, 2048, or 4096. */
    setOSR(4096);

    initialized = 1;
    return 0;
}

char createFile()
{
    int num = 1;
    char abspath[1024];
    while (1)
    {
        snprintf(abspath, sizeof(abspath), "%sion%03d.csv", DIR_PATH, num);
        file = open(abspath, O_RDONLY);
        if (file == -1)
        {
            if (errno == ENOENT) break;
            perror("unable to open exitsting files");
            return 0;
        }
        num++;
        close(file);
    }
    file = open(abspath, O_WRONLY | O_CREAT | O_EXCL, 0644);
    if (file == -1)
    {
        perror("failed to create file");
        return 0;
    }

    return 1;
}


char logData()
{
    if (!initialized)
    {
        perror("a file was not initialized");
        return 1;
    }
    time_t t = time(NULL);
    struct tm *tm_info = localtime(&t);

    float pressure, msTemp, humidity, hdcTemp, prob1, prob2, prob3, current;

    //initialize all sensors
    if (!readDigitalValue())
    {
        perror("MS5607 measurement failed");
        return 1;
    }


    pressure = getPressure();
    msTemp = getTemperature();

    if (!startMeasurementHDC()) {
        fprintf(stderr, "measurement failed\n");
        sleep(1);
    }

    humidity = readHumidity();
    hdcTemp = readTempHDC();
    prob1 = readTMP(0);
    prob2 = readTMP(1);
    prob3 = readTMP(2);
    current = readCurrent();

    char log_message[256];
    snprintf(log_message, sizeof(log_message), "%02d:%02d:%02d,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f, %.2f\n",
            tm_info->tm_hour, 
            tm_info->tm_min, 
            tm_info->tm_sec,
            pressure,
            msTemp,
            humidity,
            hdcTemp,
            prob1,
            prob2,
            prob3,
            current);
    memcpy(dataBuffer + bufferLen, log_message, strlen(log_message));
    bufferLen += strlen(log_message);
    if (bufferLen >= chunkSize)
    {
        int bytesWritten = write(file, dataBuffer, bufferLen);
        if (bytesWritten <= 0)
        {
            return 1;
        }
        fsync(file);
        bufferLen = 0;
    }
    return 0;
}

    
char logMessage(const char* message)
{
    if (!initialized)
    {
        perror("a file was not initialized");
        return 1;
    }
    time_t t = time(NULL);
    struct tm *tm_info = localtime(&t);

    char log_message[256];
    snprintf(log_message, sizeof(log_message), "[%02d:%02d:%02d] %s\n",
            tm_info->tm_hour, 
            tm_info->tm_min, 
            tm_info->tm_sec,
            message);

    memcpy(dataBuffer + bufferLen, log_message, strlen(log_message));
    bufferLen += strlen(log_message);
    if (bufferLen >= chunkSize)
    {
        int bytesWritten = write(file, dataBuffer, bufferLen);
        if (bytesWritten <= 0)
        {
            return 1;
        }
        fsync(file);
        bufferLen = 0;
    }
    return 0;
}

char flushBuffer()
{
    if (!initialized || bufferLen == 0) return 0;
    int bytesWritten = write(file, dataBuffer, bufferLen);
    if (bytesWritten > 0)
    {
        fsync(file);
    }
    else{
        return 1;
    }
    bufferLen = 0;
    return 0;
}

void flushClose()
{
    flushBuffer();
    close(file);
}
