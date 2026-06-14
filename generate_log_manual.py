from datetime import datetime


def generate_log(log_data, filename=None):
    """Create a log file with timestamped filename."""
    # Validate that log_data is a list
    if not isinstance(log_data, list):
        raise ValueError("log_data must be a list")
    
    # Generate filename with timestamp if not provided
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f"log_{timestamp}.txt"
    
    # Write log data to file
    with open(filename, 'w') as file:
        for entry in log_data:
            file.write(f"{entry}\n")
    
    # Print confirmation message
    print(f"Log written to {filename}")
    
    return filename


if __name__ == "__main__":
    # Example usage
    log_data = ["User logged in", "User updated profile", "Report exported"]
    filename = generate_log(log_data)
    print(f"Generated file: {filename}")