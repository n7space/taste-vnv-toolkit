Application is implemented in C#, using dotnet core.
Application uses its own configuration file, that captures the current values of all user adjustable values (like tool settings).
GUI is implemented using Avalonia.
GUI presents a list of tools.
Tool definitions are located in tool directory.
Each tool definition is located in its own subdirectory.
Each tool is defined by an XML, which contains at least:
- tool name, 
- tool group, 
- tool hint (shown on mouse hover/tooltip),
- tool desription/help,
- reference (relative path) to python script with code that returns tool status (status script),
- reference (relative path) to python script with code that executes the tool and shows result (tool script),
- reference (relative path) to python script with code that shows tool results (view script),
- list of tool settings:
    - each setting has name and type, which can be string, int or bool, and default value.
Tool settings contained in tool definition provide default values for the settings in application configuration; tool definition shall never be modified by the application.
Toolkit loads all tools at startup by checking the content of the directory
Toolkit presents the tools as a stack of collapsible panels, one for each group, sorted alphabetically; the stack is scrollable.
Each collapsible tool panel contains an entry for each of the tool in the group.
Entry for each of the tool contains (in order, left to right):
- name (hint is presented on mouse hoover), aligned left,
- status icon (one of OK, warning, error, status text is presented on mouse hoover), aligned right
- help button (indicated by icon "?") showing the description/help in a modal dialog,
- configure button (indicated by icon "gear") launching a configuration window,
- view button (indicated by icon "eye" or "looking glass"), showing the results.
- run button (indicated by icon "play" ) executing the tool and showing the results.
Tool confiugration window presents:
- tool name (read-only),
- list of tool settings, with each setting presented as:
    - name (read only),
    - value (read/write), presented using edit box or check box, as appropriatee for the base type.
- Cancel button, closing the window without modifying the settings,
- Save button, closing the window and saving the settings to the application configuration (NOT tool configuration).
Python scripts are executed by:
- loading them from the referenced file (path relative to the tool's directory),
- executing the loaded script using pythonnet.
Each executed script has the following data:
- tool directory,
- TASTE project directory,
- intermediate directory,
- output directory,
- list of tool settings, with each setting being a tuple (name, value), with value converted to the type indicated in the tool configuration.
Status script is executed on tool load, and returns a tuple:
- status, one of OK, warning or error, to drive the tool status icon,
- status text (to be presented as hint on mouse hoover over the status icon).
Tool script is executed on user demand (run button click):
- in addition to the common data, it receives a callback to report progress:
    - if callback is never called, no progress window is shown,
    - if callback is called at least once, the progress window is shown with the current progress (0-100), and automatically closed when the tool returns.
- it returns status, one of OK, warning or error, status text, and show status indication:
    - if show status is true, a dialog presenting the status (via icon and label) along with status text is shown (this is intended for simple tools with minimal feedback, like format code, or create test stubs),
    - if show status is false, a dialog is not presented, it is assumed that the tool will present its own results (this is intended for complex tools, which ee.g., execute tests and launch a web browser which presents statuses and coverage).
View script is eexecuted on user deman (view button click):
- it returns status, one of OK, warning or error, status text, and show status indication:
    - if show status is true, a dialog presenting the status (via icon and label) along with status text is shown (this is intended for showing error, e.g., missing results),
    - if show status is false, a dialog is not presented, it is assumed that the tool will present its own results (this is intended for nominal behaviour).
