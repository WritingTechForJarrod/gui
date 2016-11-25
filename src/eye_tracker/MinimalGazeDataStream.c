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
#define COMBINED_CALIBRATION "../../../../../gui/data/eye_tests/combined_calibration_log.txt"
// Timing constants
#define RECORD_TIME 16
#define BUFFER_TIME 2 // defines amount of time on both sides of letter to throw away



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

// variables for calibration
static FILE* g_calibration_log_1;
static FILE* g_calibration_log_2;
static FILE* g_calibration_log_3;
static FILE* g_calibration_log_4;
static int g_calibration_iteration = 0;
static time_t g_calibration_start_time;
static time_t g_current_time;

// Noise variables
static double g_positionDependentX; // between -1 and 1
static double g_positionDependentY; // between -1 and 1
static int g_xOffset; // between -PIXELOFFSET and PIXELOFFSET
static int g_yOffset; // between -PIXELOFFSET and PIXELOFFSET

/*
* Check if flag (presence of go.txt) exists, if so, begin calibration
* ../../../../../gui/src/go.txt current position of file we check
*/
int beginCalibration(char* fileName) {
	FILE* testFile = fopen(fileName, "r");
	if (testFile == NULL) {
		return 0;
	}
	else {
		fclose(testFile);
		return 1;
	}
}

/*
* Given four file pointers, append in the order given
* returns 1 on success and 0 on failure
*/
int appendFiles(char* fileName1, char* fileName2, char* fileName3, char* fileName4) {
	FILE* file1 = fopen(fileName1,"r");
	FILE* file2 = fopen(fileName2,"r");
	FILE* file3 = fopen(fileName3,"r");
	FILE* file4 = fopen(fileName4,"r");
	FILE* combined = fopen(COMBINED_CALIBRATION, "w");
	char str[50];
	if (file1 == NULL) {
		return 0;
	}
	if (file2 == NULL) {
		fclose(file1);
		return 0;
	}
	if (file3 == NULL) {
		fclose(file1);
		fclose(file2);
		return 0;
	}
	if (file4 == NULL) {
		fclose(file1);
		fclose(file2);
		fclose(file3);
		return 0;
	}
	if (combined == NULL) {
		fclose(file1);
		fclose(file2);
		fclose(file3);
		fclose(file4);
		return 0;
	}
	// all 5 logs opened successfully
	while (fgets(str, 60, file1) != NULL) {
		fprintf(combined, str);
	}
	while (fgets(str, 60, file2) != NULL) {
		fprintf(combined, str);
	}
	while (fgets(str, 60, file3) != NULL) {
		fprintf(combined, str);
	}
	while (fgets(str, 60, file4) != NULL) {
		fprintf(combined, str);
	}
	// done writing
	fclose(file1);
	fclose(file2);
	fclose(file3);
	fclose(file4);
	fclose(combined);
	return 1;
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
* Generate standard normal distributed numbers
*/
/*
double generateRandom() {
	int var1_interim = rand()%100;
	double var1 = var1_interim / 100;
}*/

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
	float eye_x; // used for noise generation, otherwise replace with eventParams.X
	float eye_y; // used for noise generation, otherwise replace with eventParams.Y
	if (txGetGazePointDataEventParams(hGazeDataBehavior, &eventParams) == TX_RESULT_OK) {
		eye_x = eventParams.X*(1+g_positionDependentX)+g_xOffset+RANDOM_PIXEL_OFFSET*generateRandom();
		eye_y = eventParams.Y*(1+g_positionDependentY)+g_yOffset+RANDOM_PIXEL_OFFSET*generateRandom();
		if (beginCalibration(CALIBRATION_FLAG)) {
			if (g_calibration_iteration == 0) { // indicates first time going through process
				// open calibration logs
				g_calibration_log_1 = fopen(CALIBRATION_LOG_1, "w");
				g_calibration_log_2 = fopen(CALIBRATION_LOG_2, "w");
				g_calibration_log_3 = fopen(CALIBRATION_LOG_3, "w");
				g_calibration_log_4 = fopen(CALIBRATION_LOG_4, "w");
				
				g_calibration_start_time = time(NULL);
				printf("\nCalibration started at: %ld\n", g_calibration_start_time);

				g_calibration_iteration = 1; // set flag to 1 so that we don't initialize calibration again
			}

			if (g_current_time > g_calibration_start_time + 7*BUFFER_TIME + 4*RECORD_TIME) {
				// calibration done
				g_calibration_iteration = 0; // reset flag to zero in case we want to calibrate again.
				remove(CALIBRATION_FLAG); // removes go.txt file
				fclose(g_calibration_log_1);
				fclose(g_calibration_log_2);
				fclose(g_calibration_log_3);
				fclose(g_calibration_log_4);
				appendFiles(CALIBRATION_LOG_1, CALIBRATION_LOG_2, CALIBRATION_LOG_3, CALIBRATION_LOG_4);
				printf("                                        \r");
				printf("done\n");

			}
			else if (g_current_time > g_calibration_start_time + 7*BUFFER_TIME + 3*RECORD_TIME) {
				fprintf(g_calibration_log_4, "%5.1f,%5.1f,%.0f,4\n", eventParams.X, eventParams.Y, eventParams.Timestamp);
				//fprintf(g_calibration_log_4, "%5.1f,%5.1f,%.0f\n", eye_x, eye_y, eventParams.Timestamp);
			}
			else if (g_current_time > g_calibration_start_time + 5*BUFFER_TIME + 3*RECORD_TIME) {
				// do nothing for 4 seconds
			}
			else if (g_current_time > g_calibration_start_time + 5*BUFFER_TIME + 2*RECORD_TIME) {
				fprintf(g_calibration_log_3, "%5.1f,%5.1f,%.0f,3\n", eventParams.X, eventParams.Y, eventParams.Timestamp);
				//fprintf(g_calibration_log_3, "%5.1f,%5.1f,%.0f\n", eye_x, eye_y, eventParams.Timestamp);
			}
			else if (g_current_time > g_calibration_start_time + 3*BUFFER_TIME + 2*RECORD_TIME) {
				// do nothing for 4 seconds
			}
			else if (g_current_time > g_calibration_start_time + 3*BUFFER_TIME + RECORD_TIME) {
				fprintf(g_calibration_log_2, "%5.1f,%5.1f,%.0f,2\n", eventParams.X, eventParams.Y, eventParams.Timestamp);
				//fprintf(g_calibration_log_2, "%5.1f,%5.1f,%.0f\n", eye_x, eye_y, eventParams.Timestamp);
			}
			else if (g_current_time > g_calibration_start_time + BUFFER_TIME + RECORD_TIME) {
				// do nothing for 4 seconds
			}
			else if (g_current_time > g_calibration_start_time + BUFFER_TIME) {
				fprintf(g_calibration_log_1, "%5.1f,%5.1f,%.0f,1\n", eventParams.X, eventParams.Y, eventParams.Timestamp);
				//fprintf(g_calibration_log_1, "%5.1f,%5.1f,%.0f\n", eye_x, eye_y, eventParams.Timestamp);
			}
			g_current_time = time(NULL);
		}
		//printf("\rGaze Data: (%5.1f, %5.1f) timestamp %.0f ms", eventParams.X, eventParams.Y, eventParams.Timestamp);
		fprintf(current_eye_coords, "%5.1f, %5.1f", eventParams.X, eventParams.Y);
		//fprintf(current_eye_coords, "%5.1f, %5.1f", eye_x, eye_y);

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

	current_eye_coords= fopen(EYESTREAM_LOCATION, "w");
	g_current_time = time(NULL); // initialize system time

	g_positionDependentX = generateRandom();
	g_positionDependentY = generateRandom();
	g_xOffset = (int)(generateRandom()*PIXEL_OFFSET);
	g_yOffset = (int)(generateRandom()*PIXEL_OFFSET);

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
