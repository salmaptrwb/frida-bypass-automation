import subprocess
import os
import sys
import time
import threading

def get_frida_scripts():
    """Retrieve all .js Frida scripts in the current directory."""
    scripts = [f for f in os.listdir('.') if f.endswith('.js')]
    return scripts

def list_running_processes():
    """List all running processes using the 'frida-ps -aU' command."""
    try:
        cmd = ['frida-ps', '-aU']
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0 or not result.stdout.strip():
            print("[-] Failed to retrieve running processes. Ensure that Frida is installed and a device is connected.")
            sys.exit(1)

        processes = result.stdout.splitlines()[1:]  # Skip the header
        processes_info = []
        for process in processes:
            parts = process.split()
            pid = parts[0]
            package_name = parts[-1]
            process_name = ' '.join(parts[1:-1])

            # Skip entries that are just placeholders (e.g., '------------------------')
            if len(process_name.strip('-')) == 0:
                continue

            processes_info.append((pid, process_name, package_name))

        return processes_info

    except FileNotFoundError:
        print("[-] Ensure that 'frida-ps' is installed and accessible from the command line.")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Unexpected error listing running processes: {e}")
        sys.exit(1)

def choose_process(processes):
    """Allow the user to choose a process by number."""
    print("\n=== Running Processes ===")
    max_name_length = max(len(name) for _, name, _ in processes)

    for i, (pid, process_name, package_name) in enumerate(processes):
        aligned_process_name = process_name.ljust(max_name_length)
        print(f"{i + 1}. {aligned_process_name}\t{package_name} (PID: {pid})")

    while True:
        try:
            choice = int(input("\nEnter the number of the process you want to target: "))
            if 1 <= choice <= len(processes):
                return processes[choice - 1]
            else:
                print("[-] Invalid number, please choose a valid process number.")
        except ValueError:
            print("[-] Please enter a valid number.")

def run_frida_script(script, package_name):
    """
    Execute a Frida script by spawning the specified package.
    Returns True if successful, False otherwise.
    """
    try:
        print(f"\n[+] Attempting to spawn {package_name} and run {script}...")

        # Spawn the app with the Frida script
        frida_cmd = ['frida', '-U', '-f', package_name, '-l', script]
        proc = subprocess.Popen(frida_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        success = False
        start_time = time.time()
        last_output_time = time.time()

        def read_output(pipe):
            nonlocal success, last_output_time
            for line in iter(pipe.readline, ''):
                print(line, end='')  # Print each line of stdout in real-time
                last_output_time = time.time()
                if 'success' in line.lower():
                    success = True

        stdout_thread = threading.Thread(target=read_output, args=(proc.stdout,))
        stderr_thread = threading.Thread(target=read_output, args=(proc.stderr,))

        stdout_thread.start()
        stderr_thread.start()

        # Monitor the process
        while stdout_thread.is_alive() or stderr_thread.is_alive():
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)

            current_time = time.time()

            # Check if there's no activity for 10 seconds (failure criteria)
            if current_time - last_output_time > 10:
                print(f"[-] No activity detected from {script} for 10 seconds, moving to the next script.")
                proc.terminate()
                proc.wait()
                return False

            # If the script runs for more than 30 seconds with activity, consider it successful and let it run
            if current_time - start_time > 30:
                print(f"[+] Script {script} is running for more than 30 seconds with activity, letting it continue.")
                return True

        if success:
            print(f"[+] Script {script} succeeded.")
            return True
        else:
            print(f"[-] Script {script} did not succeed.")
            return False

    except subprocess.CalledProcessError as e:
        print(f"[-] Error running script on package {package_name}: {e}")
        return False
    except FileNotFoundError:
        print("[-] Ensure that 'frida' is installed and accessible from the command line.")
        sys.exit(1)
    except Exception as e:
        print(f"[-] Unexpected error running script {script}: {e}")
        return False

def main():
    print("=== Frida Script Executor ===")
    
    running_processes = list_running_processes()
    if not running_processes:
        print("[-] No running processes found. Exiting.")
        sys.exit(1)

    process_pid, process_name, package_name = choose_process(running_processes)
    print(f"\n[+] Selected process: {process_name} (PID: {process_pid})")

    frida_scripts = get_frida_scripts()
    if not frida_scripts:
        print("[-] No Frida scripts (.js files) found in the current directory. Exiting.")
        sys.exit(1)

    print(f"\n[+] Found {len(frida_scripts)} Frida script(s) to test.")

    for script in frida_scripts:
        success = run_frida_script(script, package_name)
        if success:
            print(f"\n[+] Bypass succeeded with {script}.")
            break
    else:
        print("\n[-] Custom root detection and SSL pinning detected. No scripts succeeded.")

if __name__ == '__main__':
    main()
