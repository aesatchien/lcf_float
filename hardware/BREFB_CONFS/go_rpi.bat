@ECHO OFF
REM switch to local control on the br-EFB

if exist %~dp0\rpi_configuration_bankA\*.A00 (
	if exist %~dp0\rpi_configuration_bankA\br-efb.conf (
		ECHO files exist - deleting old files ...
		del br-efb.conf
		del *.A00
		TIMEOUT 2
		ECHO files exist - copying to top ...
		echo F| xcopy /y %~dp0\rpi_configuration_bankA\br-efb.conf %~dp0\br-efb.conf
		xcopy /y %~dp0\rpi_configuration_bankA\*.A00 %~dp0
	)	
) else (
    ECHO files for bank A not present
)

if exist %~dp0\rpi_configuration_bankB\*.A00 (
	if exist %~dp0\rpi_configuration_bankB\br-efb.conf (
		ECHO files exist - deleting old files ...
		del br-efb.conf
		del *.A00
		TIMEOUT 2
		ECHO files exist - copying to top ...
		echo F| xcopy /y %~dp0\rpi_configuration_bankB\br-efb.conf %~dp0\br-efb.conf
		xcopy /y %~dp0\rpi_configuration_bankB\*.A00 %~dp0
	)	
) else (
    ECHO files for bank B not present
)