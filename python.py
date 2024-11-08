import paramiko
import time

def get_running_config(ip, username, password):
    """Connects to the Cisco device using SSH and retrieves the running configuration."""
    try:
        # Initialize SSH client and automatically add the device's SSH key if not already known
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print("Establishing SSH connection to retrieve running config...")
        # Establish SSH connection to the device
        ssh.connect(ip, username=username, password=password)
        print("SSH connection established.")
        
        # Run the command to retrieve the running configuration
        stdin, stdout, stderr = ssh.exec_command("show running-config")
        
        # Ensure we wait for the output to be completely returned
        stdout.channel.recv_exit_status()
        
        # Read and decode the output, then split it into lines
        config = stdout.read().decode().splitlines()
        
        # Close the SSH connection
        ssh.close()
        
        return config
    except Exception as e:
        print(f"Error retrieving config: {e}")
        return None

def load_hardening_guidelines(file_path):
    """Loads the hardening guidelines from a local file."""
    try:
        with open(file_path, 'r') as file:
            return file.read().splitlines()
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return None

def check_compliance(running_config, guidelines):
    """Compares the device's running configuration to the hardening guidelines."""
    non_compliant = [g for g in guidelines if g not in running_config]
    if non_compliant:
        print("Non-compliant configurations found:")
        print("\n".join(f"- {item}" for item in non_compliant))
    else:
        print("Configuration is compliant with hardening guidelines.")

def configure_syslog(ip, username, password, syslog_server_ip):
    """Connects to the Cisco device and configures it to send syslog messages to a specified server."""
    commands = [
        "configure terminal",
        f"logging host {syslog_server_ip}",  # Sets syslog server IP
        "logging trap informational",       # Sets logging level to informational
        "end",
        "write memory"                      # Saves configuration changes
    ]
    
    try:
        # Initialize SSH client and automatically add the device's SSH key if not already known
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print("Establishing SSH connection to configure syslog...")
        # Establish SSH connection to the device
        ssh.connect(ip, username=username, password=password)
        print("SSH connection established for syslog configuration.")
        
        # Send each command one at a time using exec_command
        for cmd in commands:
            print(f"Sending command: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            stdout.channel.recv_exit_status()  # Ensure command has finished
            time.sleep(1)  # Add a small delay between commands to ensure they execute correctly
        
        print(f"Syslog server {syslog_server_ip} configured successfully.")
        
        # Close the SSH connection
        ssh.close()
    except Exception as e:
        print(f"Error configuring syslog: {e}")

def main():
    """Main function that orchestrates the configuration retrieval, compliance check,
    and syslog configuration."""
    
    # Device connection details
    ip = "192.168.56.101"
    username = "cisco"
    password = "cisco123!"
    
    # Hardening guidelines file path
    guidelines_path = "cisco_hardening_guidelines.txt"
    
    # Syslog server IP
    syslog_server_ip = "192.168.1.100"
    
    # Step 1: Retrieve the running configuration from the device
    running_config = get_running_config(ip, username, password)
    
    # Step 2: Load hardening guidelines from the file
    guidelines = load_hardening_guidelines(guidelines_path)
    
    # Step 3: Check device compliance with hardening guidelines
    if running_config and guidelines:
        print("\nChecking compliance with hardening guidelines...")
        check_compliance(running_config, guidelines)
    
    # Step 4: Configure syslog for event logging on the device
    print("\nConfiguring syslog on the device...")
    configure_syslog(ip, username, password, syslog_server_ip)

# Run the script if executed as the main module
if __name__ == "__main__":
    main()
