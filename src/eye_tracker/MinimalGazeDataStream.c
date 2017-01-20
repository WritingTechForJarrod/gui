/*
 * This is an example that demonstrates how to connect to the EyeX Engine and subscribe to the lightly filtered gaze data stream.
 *
 * Copyright 2013-2014 Tobii Technology AB. All rights reserved.
 */
#define _CRT_SECURE_NO_WARNINGS
#define PI 3.141592654
#define PIXEL_OFFSET 100
#define RANDOM_PIXEL_OFFSET 300
// File locations
#define EYESTREAM_LOCATION "../../../../../gui/data/eye_tests/eyeStream.txt" // where we put our eye tracker output
#define CALIBRATION_FLAG "../../../../../gui/src/go.txt" // check if this file exists to begin calibration
#define CALIBRATION_LOG_1 "../../../../../gui/data/eye_tests/calibration_log_1.txt" // calibration log 1 path
#define CALIBRATION_LOG_2 "../../../../../gui/data/eye_tests/calibration_log_2.txt" // calibration log 2 path
#define CALIBRATION_LOG_3 "../../../../../gui/data/eye_tests/calibration_log_3.txt" // calibration log 3 path
#define CALIBRATION_LOG_4 "../../../../../gui/data/eye_tests/calibration_log_4.txt" // calibration log 4 path
#define CALIBRATION_LOG_5 "../../../../../gui/data/eye_tests/calibration_log_5.txt" // calibration log 5 path
#define COMBINED_CALIBRATION "../../../../../gui/data/eye_tests/combined_calibration_log.csv"
// Timing constants
//#define RECORD_TIME 3
#define BUFFER_TIME 2 // defines amount of time on both sides of letter to throw away
//#define NUMBER_LOGS 3 // Temporary variable, will eventually come from go.txt



#include <Windows.h>
#include <stdio.h>
#include <conio.h>
#include <assert.h>
#include <time.h>
#include "eyex/EyeX.h"

#pragma comment (lib, "Tobii.EyeX.Client.lib")
// ID of the global interactor that provides our data stream; must be unique within the application.
static const TX_STRING InteractorId = "Twilight Sparkle";

// global variables
static TX_HANDLE g_hGlobalInteractorSnapshot = TX_EMPTY_HANDLE;
static FILE* current_eye_coords;

// variables for calibration, maximum of 5 logs can be collected
static FILE* g_calibration_log_1;
static FILE* g_calibration_log_2;
static FILE* g_calibration_log_3;
static FILE* g_calibration_log_4;
static FILE* g_calibration_log_5;
static int g_calibration_iteration = 0;
static time_t g_calibration_start_time;
static time_t g_current_time;
static int g_number_logs = 0;
static int g_record_time = 0;

// Noise variables
static double g_positionDependentX; // between -1 and 1
static double g_positionDependentY; // between -1 and 1
static int g_xOffset; // between -PIXELOFFSET and PIXELOFFSET
static int g_yOffset; // between -PIXELOFFSET and PIXELOFFSET

/*
* Takes CSV string with two values and returns array with int form of two strings
*/
void splitString(char* to_split, int arr[]) {
	char c = to_split[0];
	char val1[10] = "";
	char val2[10] = "";
	int i = 0;
	int comma_found = 0;
	int decrement_value = 0;

	while (c != '\0') {
		if (c == ',') {
			comma_found = 1;
			decrement_value = i + 1;
			val1[i] = '\0';
			i++;
			c = to_split[i];
			continue;
		}
		if (comma_found == 0)
			val1[i] = c;
		else
			val2[i-decrement_value] = c;
		i++;
		c = to_split[i];
	}
	val2[i-decrement_value] = '\0';
	arr[0] = atoi(val1);
	arr[1] = atoi(val2);
}
/*
* Check if flag (presence of go.txt) exists, if so, begin calibration
* ../../../../../gui/src/go.txt current position of file we check
*/
int beginCalibration(char* fileName) {
	FILE* testFile = fopen(fileName, "r");
	char str[50];
	int vals[2];
	int python_record_time = 0; // this value comes from the python script
	if (testFile == NULL) {
		return 0;
	}
	else {
		fgets(str, 60, testFile);
		splitString(str, vals);
		g_number_logs = vals[0];
		python_record_time = vals[1];
		g_record_time = python_record_time - 2*BUFFER_TIME; // conversion to "C record time"
		fclose(testFile);
		return 1;
	}
}

/*
* Given four file pointers, append in the order given
* returns 1 on success and 0 on failure
*/
int appendFiles(char* fileName1, char* fileName2, char* fileName3, char* fileName4, char* fileName5) {
	FILE* file1 = fopen(fileName1,"r");
	FILE* file2 = fopen(fileName2, "r");
	FILE* file3 = fopen(fileName3,"r");
	FILE* file4 = fopen(fileName4,"r");
	FILE* file5 = fopen(fileName5,"r");
	FILE* combined = fopen(COMBINED_CALIBRATION, "w");
	char str[50];

	if (file1 == NULL || file2 == NULL || file3 == NULL || file4 == NULL || file5 == NULL || combined == NULL) {
		if (file1 != NULL)
			fclose(file1);
		if (file2 != NULL)
			fclose(file2);
		if (file3 != NULL)
			fclose(file3);
		if (file4 != NULL)
			fclose(file4);
		if (file5 != NULL)
			fclose(file5);
		if (combined != NULL)
			fclose(combined);
		return 0;
	}

	fprintf(combined, "1,2,3,4\n");
	// all 6 logs opened successfully
	while (fgets(str, 60, file1) != NULL) {
		fprintf(combined, str);
	}
	if (g_number_logs > 1) {
		while (fgets(str, 60, file2) != NULL) {
			fprintf(combined, str);
		}
	}
	if (g_number_logs > 2) {
		while (fgets(str, 60, file3) != NULL) {
			fprintf(combined, str);
		}
	}
	if (g_number_logs > 3) {
		while (fgets(str, 60, file4) != NULL) {
			fprintf(combined, str);
		}
	}
	if (g_number_logs > 4) {
		while (fgets(str, 60, file5) != NULL) {
			fprintf(combined, str);
		}
	}
	// done writing
	fclose(file1);
	fclose(file2);
	fclose(file3);
	fclose(file4);
	fclose(file5);
	fclose(combined);
	return 1;
}

/*
* Completes calibration process: closes logs, resets flags, removes go.txt file (used to start calibration) and appends logs
*/
void completeCalibration() {
	int calibration_result = 0;
	g_calibration_iteration = 0; // reset flag to zero in case we want to calibrate again.
	remove(CALIBRATION_FLAG); // removes go.txt file
	fclose(g_calibration_log_1);
	fclose(g_calibration_log_2);
	fclose(g_calibration_log_3);
	fclose(g_calibration_log_4);
	fclose(g_calibration_log_5);
	calibration_result = appendFiles(CALIBRATION_LOG_1, CALIBRATION_LOG_2, CALIBRATION_LOG_3, CALIBRATION_LOG_4, CALIBRATION_LOG_5);
	if (calibration_result == 0) {
		printf("error");
		exit(1);
	}
	printf("done\n");
}

/*
* Generate noise to simulate Jarrod's vision
*/
double generateRandom() {
	int random = rand();
	double return_val;
	random = random % 200;
	if (random > 100) {
		random = -1*(200 - random);
	}
	return_val = (double)random;
	return return_val/100;
}

/*
 * Initializes g_hGlobalInteractorSnapshot with an interactor that has the Gaze Point behavior.
 */
BOOL InitializeGlobalInteractorSnapshot(TX_CONTEXTHANDLE hContext)
{
	TX_HANDLE hInteractor = TX_EMPTY_HANDLE;
	TX_GAZEPOINTDATAPARAMS params = { TX_GAZEPOINTDATAMODE_LIGHTLYFILTERED };
	BOOL success;

	success = txCreateGlobalInteractorSnapshot(
		hContext,
		InteractorId,
		&g_hGlobalInteractorSnapshot,
		&hInteractor) == TX_RESULT_OK;
	success &= txCreateGazePointDataBehavior(hInteractor, &params) == TX_RESULT_OK;

	txReleaseObject(&hInteractor);

	return success;
}

/*
 * Callback function invoked when a snapshot has been committed.
 */
void TX_CALLCONVENTION OnSnapshotCommitted(TX_CONSTHANDLE hAsyncData, TX_USERPARAM param)
{
	// check the result code using an assertion.
	// this will catch validation errors and runtime errors in debug builds. in release builds it won't do anything.

	TX_RESULT result = TX_RESULT_UNKNOWN;
	txGetAsyncDataResultCode(hAsyncData, &result);
	assert(result == TX_RESULT_OK || result == TX_RESULT_CANCELLED);
}

/*
 * Callback function invoked when the status of the connection to the EyeX Engine has changed.
 */
void TX_CALLCONVENTION OnEngineConnectionStateChanged(TX_CONNECTIONSTATE connectionState, TX_USERPARAM userParam)
{
	switch (connectionState) {
	case TX_CONNECTIONSTATE_CONNECTED: {
			BOOL success;
			printf("The connection state is now CONNECTED (We are connected to the EyeX Engine)\n");
			// commit the snapshot with the global interactor as soon as the connection to the engine is established.
			// (it cannot be done earlier because committing means "send to the engine".)
			success = txCommitSnapshotAsync(g_hGlobalInteractorSnapshot, OnSnapshotCommitted, NULL) == TX_RESULT_OK;
			if (!success) {
				printf("Failed to initialize the data stream.\n");
			}
			else {
				printf("Waiting for gaze data to start streaming...\n");
			}
		}
		break;

	case TX_CONNECTIONSTATE_DISCONNECTED:
		printf("The connection state is now DISCONNECTED (We are disconnected from the EyeX Engine)\n");
		break;

	case TX_CONNECTIONSTATE_TRYINGTOCONNECT:
		printf("The connection state is now TRYINGTOCONNECT (We are trying to connect to the EyeX Engine)\n");
		break;

	case TX_CONNECTIONSTATE_SERVERVERSIONTOOLOW:
		printf("The connection state is now SERVER_VERSION_TOO_LOW: this application requires a more recent version of the EyeX Engine to run.\n");
		break;

	case TX_CONNECTIONSTATE_SERVERVERSIONTOOHIGH:
		printf("The connection state is now SERVER_VERSION_TOO_HIGH: this application requires an older version of the EyeX Engine to run.\n");
		break;
	}
}

/*
 * Handles an event from the Gaze Point data stream.
 */
void OnGazeDataEvent(TX_HANDLE hGazeDataBehavior)
{
	TX_GAZEPOINTDATAEVENTPARAMS eventParams;
	if (txGetGazePointDataEventParams(hGazeDataBehavior, &eventParams) == TX_RESULT_OK) {
		if (beginCalibration(CALIBRATION_FLAG)) {
			if (g_calibration_iteration == 0) { // indicates first time going through process
				// open calibration logs (minimum 1, maximum 5)
				g_calibration_log_1 = fopen(CALIBRATION_LOG_1, "w");
				g_calibration_log_2 = fopen(CALIBRATION_LOG_2, "w");
				g_calibration_log_3 = fopen(CALIBRATION_LOG_3, "w");
				g_calibration_log_4 = fopen(CALIBRATION_LOG_4, "w");
				g_calibration_log_5 = fopen(CALIBRATION_LOG_5, "w");

				g_calibration_start_time = time(NULL);
				printf("\nCalibration started at: %ld\n", g_calibration_start_time);

				g_calibration_iteration = 1; // set flag to 1 so that we don't initialize calibration again
			}

			if (g_current_time > g_calibration_start_time + g_number_logs*g_record_time + 2*g_number_logs*BUFFER_TIME) {
				// calibration done
				printf(" done recording ");
				completeCalibration();
			}
			else if (g_current_time > g_calibration_start_time + 9*BUFFER_TIME + 5*g_record_time) {
				// do nothing for BUFFER_TIME seconds
				printf("\rpn, %ld", g_current_time);
			}
			else if (g_current_time > g_calibration_start_time + 9*BUFFER_TIME + 4*g_record_time) {
				// write log 5
				fprintf(g_calibration_log_5, "%5.1f,%5.1f,%.0f,5\n", eventParams.X, eventParams.Y, eventParams.Timestamp);
				printf("\rp5, %ld", g_current_time);
			}
			else if (g_current_time > g_calibration_start_time + 7*BUFFER_TIME + 4*g_record_time) {
				// do nothing for 2*BUFFER_TIME seconds
				printf("\rpn, %ld", g_current_time);
			}
			else if (g_current_time > g_calibration_start_time + 7*BUFFER_TIME + 3*g_record_time) {
				// write log 4
				fprintf(g_calibration_log_4, "%5.1f,%5.1f,%.0f,4\n", eventParams.X, eventParams.Y, eventParams.Timestamp);
				printf("\rp4, %ld", g_current_time);
			}
			else if (g_current_time > g_calibration_start_time + 5*BUFFER_TIME + 3*g_record_time) {
				// do nothing for 2*BUFFER_TIME seconds
				printf("\rpn, %ld", g_current_time);
			}
			else if (g_current_time > g_calibration_start_time + 5*BUFFER_TIME + 2*g_record_time) {
				// write log 3
				fprintf(g_calibration_log_3, "%5.1f,%5.1f,%.0f,3\n", eventParams.X, eventParams.Y, eventParams.Timestamp);
				printf("\rp3, %ld", g_current_time);
			}
			else if (g_current_time > g_calibration_start_time + 3*BUFFER_TIME + 2*g_record_time) {
				// do nothing for 2*BUFFER_TIME seconds
				printf("\rpn, %ld", g_current_time);
			}
			else if (g_current_time > g_calibration_start_time + 3*BUFFER_TIME + g_record_time) {
				// write log 2 for RECORD_TIME seconds
				fprintf(g_calibration_log_2, "%5.1f,%5.1f,%.0f,2\n", eventParams.X, eventParams.Y, eventParams.Timestamp);
				printf("\rp2, %ld", g_current_time);
			}
			else if (g_current_time > g_calibration_start_time + BUFFER_TIME + g_record_time) {
				// do nothing for 2*BUFFER_TIME seconds after 1*BUFFER_TIME + 1*RECORD_TIME seconds
				printf("\rpn, %ld", g_current_time);
			}
			else if (g_current_time > g_calibration_start_time + BUFFER_TIME) {
				// write log 1 for RECORD_TIME seconds after 1*BUFFER_TIME seconds of waiting
				fprintf(g_calibration_log_1, "%5.1f,%5.1f,%.0f,1\n", eventParams.X, eventParams.Y, eventParams.Timestamp);
				printf("\rp1, %ld", g_current_time);
			}
			g_current_time = time(NULL);
		}
		//printf("/rGaze Data: (%5.1f, %5.1f) timestamp %.0f ms", eventParams.X, eventParams.Y, eventParams.Timestamp);
		fprintf(current_eye_coords, "%5.1f, %5.1f", eventParams.X, eventParams.Y);

		fseek(current_eye_coords,0,SEEK_SET);
	} else {
	  printf("Failed to interpret gaze data event packet.");
	}
}

/*
 * Callback function invoked when an event has been received from the EyeX Engine.
 */
void TX_CALLCONVENTION HandleEvent(TX_CONSTHANDLE hAsyncData, TX_USERPARAM userParam)
{
	TX_HANDLE hEvent = TX_EMPTY_HANDLE;
	TX_HANDLE hBehavior = TX_EMPTY_HANDLE;

	txGetAsyncDataContent(hAsyncData, &hEvent);

	// NOTE. Uncomment the following line of code to view the event object. The same function can be used with any interaction object.
	//OutputDebugStringA(txDebugObject(hEvent));

	if (txGetEventBehavior(hEvent, &hBehavior, TX_BEHAVIORTYPE_GAZEPOINTDATA) == TX_RESULT_OK) {
 		OnGazeDataEvent(hBehavior);
		txReleaseObject(&hBehavior);
	}

	// NOTE since this is a very simple application with a single interactor and a single data stream, 
	// our event handling code can be very simple too. A more complex application would typically have to 
	// check for multiple behaviors and route events based on interactor IDs.

	txReleaseObject(&hEvent);
}

/*
 * Application entry point.
 */
int main(int argc, char* argv[])
{
	TX_CONTEXTHANDLE hContext = TX_EMPTY_HANDLE;
	TX_TICKET hConnectionStateChangedTicket = TX_INVALID_TICKET;
	TX_TICKET hEventHandlerTicket = TX_INVALID_TICKET;
	BOOL success;
	int arr[2];

	current_eye_coords= fopen(EYESTREAM_LOCATION, "w");
	g_current_time = time(NULL); // initialize system time

	// initialize and enable the context that is our link to the EyeX Engine.
	success = txInitializeEyeX(TX_EYEXCOMPONENTOVERRIDEFLAG_NONE, NULL, NULL, NULL, NULL) == TX_RESULT_OK;
	success &= txCreateContext(&hContext, TX_FALSE) == TX_RESULT_OK;
	success &= InitializeGlobalInteractorSnapshot(hContext);
	success &= txRegisterConnectionStateChangedHandler(hContext, &hConnectionStateChangedTicket, OnEngineConnectionStateChanged, NULL) == TX_RESULT_OK;
	success &= txRegisterEventHandler(hContext, &hEventHandlerTicket, HandleEvent, NULL) == TX_RESULT_OK;
	// enables connection to EyeX Engine, connection alive
	// until it is desabled or context is destroyed
	success &= txEnableConnection(hContext) == TX_RESULT_OK;

	// let the events flow until a key is pressed.
	if (success) {
		printf("Initialization was successful.\n");
	} else {
		printf("Initialization failed.\n");
	}
	printf("Press any key to exit...\n");
	_getch();
	printf("Exiting.\n");

	// disable and delete the context.
	txDisableConnection(hContext);
	txReleaseObject(&g_hGlobalInteractorSnapshot);
	success = txShutdownContext(hContext, TX_CLEANUPTIMEOUT_DEFAULT, TX_FALSE) == TX_RESULT_OK;
	success &= txReleaseContext(&hContext) == TX_RESULT_OK;
	success &= txUninitializeEyeX() == TX_RESULT_OK;
	if (!success) {
		printf("EyeX could not be shut down cleanly. Did you remember to release all handles?\n");
	}

	fclose(current_eye_coords);
	return 0;
}
