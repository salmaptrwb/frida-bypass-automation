# **Frida Script Automation for Bypassing Root Detection & SSL Pinning**

This Python script automates the process of bypassing root detection and SSL pinning in mobile applications using Frida. Instead of running each Frida JavaScript (JS) script manually, this automation script will execute them one by one and determine which one successfully bypasses the app's security mechanisms.

## **Features**

- **Automated Execution**: Automatically runs all Frida JS scripts in the current directory against the specified mobile app.
- **Success Detection**: The script detects which JS file successfully bypasses root detection and SSL pinning by monitoring Frida's process activity.
- **Time-Efficient**: If a JS script shows no activity within 10 seconds, the script moves on to the next one. However, if it does show activity for more than 30 seconds, meaning the traffic successfully captured, the script continues to run without cutting it off.
- **User-Friendly**: Simply choose which package name from the list of running processes when prompted, and the script takes care of the rest.

## **Installation & Setup**

1. **Prepare Your JS Scripts**:
Place all the Frida JS scripts you want to test in the same directory as the this Python script.

2. **Install Dependencies**:
Ensure that both adb and frida are installed and accessible from your command line. Oh and also make sure to use python 3, instead of python 2.7.

3. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/frida-bypass-automation.git

## **Usage**
   
1. **Run the Script**:
  ```bash
   cd frida-bypass-automation
   python frida_bypass_automation.py
```

2. **Follow the Prompts**:
   - Enter which number from the list of running processes of the app you want to bypass.
   - The script will automatically test each JS script and indicate the first successful bypass.
     
## **Example**
```
$ python frida_bypass_automation.py
=== Frida Script Executor ===

=== Running Processes ===
1. Example          com.myapp.example (PID: 15770)

Enter the number of the process you want to target: 1

[+] Selected process: Example (PID: 15770)

[+] Found 3 Frida script(s) to test.

[+] Attempting to run script1.js on com.myapp.example...
[-] Script script1.js did not show activity within 10 seconds. Moving on to the next script.

[+] Attempting to run script2.js on com.myapp.example...
[+] Script script2.js is running for more than 30 seconds with activity, letting it continue.

[+] Bypass succeeded with script2.js.
```
