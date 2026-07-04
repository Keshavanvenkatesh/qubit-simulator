# logger.py
from datetime import datetime
import os
import glob

class logger:
    logger_name_list = []
    duplicate_logger_counter = 1
    can_i_write_logs = True
    files_rotated = 0

    def __init__(self, name, max_size=1048576, file_to_log="logging.txt"):
        base_name = str(name)
        if logger.check_logger_duplicate_name(base_name):
            unique_name = base_name + str(logger.duplicate_logger_counter)
            logger.duplicate_logger_counter += 1
            self.name = unique_name
        else:
            self.name = base_name
        logger.logger_name_list.append(self.name)
        self.can_i_write_logs = True
        self.max_size = max_size
        self.file_to_log = file_to_log

    # ---------------------- Helper Methods ----------------------
    @staticmethod
    def _get_timestamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def is_log_full(file="logging.txt", max_size=1048576):
        size = os.path.getsize(file) if os.path.exists(file) else 0
        return size > max_size

    @staticmethod
    def rotate_log(file, max_size=1048576):
        if os.path.exists(file) and os.path.getsize(file) > max_size:
            logger.files_rotated += 1
            folder = os.path.dirname(file)
            if folder == "":
                folder = "."
            base = os.path.basename(file)
            rotated_name = os.path.join(folder, f"{base}_{logger.files_rotated}.bak")
            os.rename(file, rotated_name)
            print(f"Log rotated: {rotated_name}")
            with open(file, "w", encoding="utf-8") as new_file:
                new_file.write(f"=== New log file created after rotation #{logger.files_rotated} ===\n")
        elif not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as new_file:
                new_file.write(f"=== New log file created ===\n")
        else:
            raise RuntimeError

    @staticmethod
    def handle_log_full(content):
        print("=================== LOG IS FULL ===================")
        print(content)
        print("===================================================")

    # ---------------------- Decorator ----------------------
    def logging(self, file_to_log="logging.txt"):
        def decorator(func):
            def wrapper(*args, **kwargs):
                timestamp = logger._get_timestamp()
                function_name = func.__name__
                arguments = [arg for arg in args]
                try:
                    result = func(*args, **kwargs)
                    log = (f"[NO ERROR] {timestamp} >>> logger:{self.name} "
                           f">>> function:{function_name}({arguments}) "
                           f":return({result}): no error")
                except Exception as e:
                    result = None
                    log = (f"[ERROR] {timestamp} >>> logger:{self.name} "
                           f">>> function:{function_name}({arguments}) "
                           f":return(None): {type(e).__name__} - {e}")

                if logger.is_log_full(file_to_log, self.max_size):
                    logger.rotate_log(file_to_log, self.max_size)

                if self.can_i_write_logs and logger.can_i_write_logs:
                    if logger.is_log_full(file_to_log, self.max_size):
                        logger.handle_log_full(log)
                    else:
                        with open(file_to_log, "a", encoding="utf-8") as file:
                            file.write(log + "\n")
                return result
            return wrapper
        return decorator

    # ---------------------- Manual Logs ----------------------
    def log_info(self, msg, function_name="unknown", arguments="[None]", return_value="None",
                 PREFIX="\t", POSTFIX="", file_to_log="logging.txt"):
        if logger.is_log_full(file_to_log, self.max_size):
            logger.rotate_log(file_to_log, self.max_size)
        timestamp = logger._get_timestamp()
        content = (f"{PREFIX}[INFO] {timestamp} >>> logger:{self.name} "
                   f">>> function:{function_name}({arguments}) "
                   f":return({return_value}): {msg} {POSTFIX}")
        if logger.is_log_full(file_to_log, self.max_size):
            logger.handle_log_full(content)
        else:
            with open(file_to_log, "a", encoding="utf-8") as file:
                file.write(content + "\n")

    def log_warning(self, msg, function_name="unknown", arguments="[None]", return_value="None",
                    PREFIX="\t", POSTFIX="", file_to_log="logging.txt"):
        if logger.is_log_full(file_to_log, self.max_size):
            logger.rotate_log(file_to_log, self.max_size)
        timestamp = logger._get_timestamp()
        content = (f"{PREFIX}[WARNING] {timestamp} >>> logger:{self.name} "
                   f">>> function:{function_name}({arguments}) "
                   f":return({return_value}): {msg} {POSTFIX}")
        if logger.is_log_full(file_to_log, self.max_size):
            logger.handle_log_full(content)
        else:
            with open(file_to_log, "a", encoding="utf-8") as file:
                file.write(content + "\n")

    def log_error(self, msg, function_name="unknown", arguments="[None]", return_value="None",
                  PREFIX="\t", POSTFIX="", file_to_log="logging.txt"):
        if logger.is_log_full(file_to_log, self.max_size):
            logger.rotate_log(file_to_log, self.max_size)
        timestamp = logger._get_timestamp()
        content = (f"{PREFIX}[ERROR] {timestamp} >>> logger:{self.name} "
                   f">>> function:{function_name}({arguments}) "
                   f":return({return_value}): {msg} {POSTFIX}")
        if logger.is_log_full(file_to_log, self.max_size):
            logger.handle_log_full(content)
        else:
            with open(file_to_log, "a", encoding="utf-8") as file:
                file.write(content + "\n")

    def log_passed(self, msg, function_name="unknown", arguments="[None]", return_value="None",
                  PREFIX="\t", POSTFIX="", file_to_log="logging.txt"):
        if logger.is_log_full(file_to_log, self.max_size):
            logger.rotate_log(file_to_log, self.max_size)
        timestamp = logger._get_timestamp()
        content = (f"{PREFIX}[SUCCESS] {timestamp} >>> logger:{self.name} "
                   f">>> function:{function_name}({arguments}) "
                   f":return({return_value}): {msg} {POSTFIX}")
        if logger.is_log_full(file_to_log, self.max_size):
            logger.handle_log_full(content)
        else:
            with open(file_to_log, "a", encoding="utf-8") as file:
                file.write(content + "\n")

    def log_failed(self, msg, function_name="unknown", arguments="[None]", return_value="None",
                  PREFIX="\t", POSTFIX="", file_to_log="logging.txt"):
        if logger.is_log_full(file_to_log, self.max_size):
            logger.rotate_log(file_to_log, self.max_size)
        timestamp = logger._get_timestamp()
        content = (f"{PREFIX}[FAILED] {timestamp} >>> logger:{self.name} "
                   f">>> function:{function_name}({arguments}) "
                   f":return({return_value}): {msg} {POSTFIX}")
        if logger.is_log_full(file_to_log, self.max_size):
            logger.handle_log_full(content)
        else:
            with open(file_to_log, "a", encoding="utf-8") as file:
                file.write(content + "\n")

    # ---------------------- Log File Management ----------------------
    @staticmethod
    def clear_all_logs(file_to_log="logging.txt"):
        files = sorted(glob.glob(file_to_log + "*"))
        if not files:
            print("No log files found.")
            return
        for f in files:
            with open(f, "w", encoding="utf-8") as file:
                file.write(f"=== Log cleared at {logger._get_timestamp()} ===\n")
        print(f"Cleared contents of {len(files)} log files.")

    @staticmethod
    def delete_all_logs(file_to_log="logging.txt"):
        files = sorted(glob.glob(file_to_log + "*"))
        if not files:
            print("No log files found.")
            return
        for f in files:
            if f == file_to_log:
                with open(f, "w", encoding="utf-8") as file:
                    file.write(f"=== Main log cleared at {logger._get_timestamp()} ===\n")
            else:
                os.remove(f)
                print(f"Deleted: {f}")
        print("Deleted rotated logs and cleared main log.")

    # ---------------------- Viewing Logs ----------------------
    @staticmethod
    def _truncate_line(entry, max_length=100):
        if len(entry) > max_length:
            return entry[:max_length] + "..."
        return entry

    def show_logs(self, log_file="logging.txt", max_len=120):
        files = sorted(glob.glob(log_file + "*"))
        if not files:
            print("THE LOG IS EMPTY !!!")
            return
        print("start of log -----")
        for f in files:
            with open(f, encoding="utf-8") as file:
                for line in file:
                    if f"logger:{self.name}" in line:
                        print(logger._truncate_line(line.strip(), max_len))
        print("end of log -----")

    @staticmethod
    def show_all_logs(log_file="logging.txt", max_len=120):
        files = sorted(glob.glob(log_file + "*"))
        if not files:
            print("THE LOG IS EMPTY !!!")
            return
        print("start of log -----")
        for f in files:
            with open(f, encoding="utf-8") as file:
                for line in file:
                    print(logger._truncate_line(line.strip(), max_len))
        print("end of log -----")

    @staticmethod
    def show_all_error(log_file="logging.txt", max_len=120):
        files = sorted(glob.glob(log_file + "*"))
        if not files:
            print("THE LOG IS EMPTY !!!")
            return
        print("start of log -----")
        for f in files:
            with open(f, encoding="utf-8") as file:
                for line in file:
                    if "[ERROR]" in line:
                        print(logger._truncate_line(line.strip(), max_len))
        print("end of log -----")

    @staticmethod
    def show_all_warning(log_file="logging.txt", max_len=120):
        files = sorted(glob.glob(log_file + "*"))
        if not files:
            print("THE LOG IS EMPTY !!!")
            return
        print("start of log -----")
        for f in files:
            with open(f, encoding="utf-8") as file:
                for line in file:
                    if "[WARNING]" in line:
                        print(logger._truncate_line(line.strip(), max_len))
        print("end of log -----")

    @staticmethod
    def show_all_info(log_file="logging.txt", max_len=120):
        files = sorted(glob.glob(log_file + "*"))
        if not files:
            print("THE LOG IS EMPTY !!!")
            return
        print("start of log -----")
        for f in files:
            with open(f, encoding="utf-8") as file:
                for line in file:
                    if "[INFO]" in line:
                        print(logger._truncate_line(line.strip(), max_len))
        print("end of log -----")

    @staticmethod
    def show_all_success(log_file="logging.txt", max_len=120):
        files = sorted(glob.glob(log_file + "*"))
        if not files:
            print("THE LOG IS EMPTY !!!")
            return
        print("start of log -----")
        for f in files:
            with open(f, encoding="utf-8") as file:
                for line in file:
                    if "[SUCCESS]" in line:
                        print(logger._truncate_line(line.strip(), max_len))
        print("end of log -----")

    @staticmethod
    def show_all_failed(log_file="logging.txt", max_len=120):
        files = sorted(glob.glob(log_file + "*"))
        if not files:
            print("THE LOG IS EMPTY !!!")
            return
        print("start of log -----")
        for f in files:
            with open(f, encoding="utf-8") as file:
                for line in file:
                    if "[FAILED]" in line:
                        print(logger._truncate_line(line.strip(), max_len))
        print("end of log -----")

    # ---------------------- Logger Management ----------------------
    @classmethod
    def show_logger(cls):
        for logger_item in cls.logger_name_list:
            print(logger_item)

    @classmethod
    def check_logger_duplicate_name(cls, new_logger_name):
        return new_logger_name in cls.logger_name_list

    def turn_on_log(self):
        self.can_i_write_logs = True

    def turn_off_log(self):
        self.can_i_write_logs = False

    @classmethod
    def turn_off_all_logs(cls):
        cls.can_i_write_logs = False

    @classmethod
    def turn_on_all_logs(cls):
        cls.can_i_write_logs = True

    @staticmethod
    def help():
        print("""
     Logger Class Help 

A custom logging system with:
- Function call logging (decorator-based)
- Manual log messages (info, warning, error)
- Automatic file rotation when exceeding max size
- View logs (all, per logger, error/warning/info only)
- Clear/delete log files
- Toggle logging ON/OFF per logger or globally
- Duplicate logger name handling

    Usage:
    my_logger = logger("example_logger", max_size=1024, file_to_log="logging.txt")

    @my_logger.logging()
    def add(a, b):
        return a + b

    add(5, 3)  # will log automatically

    Methods:

Logging
 - logging(file_to_log="logging.txt")  
      → Decorator for logging function calls

Manual Logs
 - log_info(msg, function_name="...", arguments="...", return_value="...", file_to_log="...")  
      → Write an info log  
 - log_warning(...)  
      → Write a warning log  
 - log_error(...)  
      → Write an error log  
- log_passed(...)
      → Write a success log
- log_failed(...)
      → Write a failed log

Viewing Logs
 - show_logs(log_file="logging.txt")  
      → Show logs only for this logger (across rotated files too)  
 - show_all_logs(log_file="logging.txt")  
      → Show all logs from all files  
 - show_all_error(log_file="logging.txt")  
      → Show only error logs  
 - show_all_warning(log_file="logging.txt")  
      → Show only warning logs  
 - show_all_info(log_file="logging.txt")  
      → Show only info logs  
- show_all_success(log_file="logging.txt")
      → Show only success logs
- show_all_failed(log_file="logging.txt")
      → Show only failed logs

Log File Management
 - clear_all_logs(file_to_log="logging.txt")  
      → Clears contents of ALL logs (main + rotated)  
 - delete_all_logs(file_to_log="logging.txt")  
      → Deletes all rotated logs, clears only main log  

Management
 - show_logger()  
      → Show all created logger names  
 - turn_on_log() / turn_off_log()  
      → Enable/disable logging for this logger  
 - turn_on_all_logs() / turn_off_all_logs()  
      → Enable/disable all loggers  

Rotation & Limits
 - rotate_log(file="logging.txt", max_size=N)  
      → Rotates current log file when it exceeds N bytes  
        (e.g., logging.txt → logging.txt_1.bak, logging.txt_2.bak, ...)  
      → A new empty logging.txt file is created automatically  
 - is_log_full(file="logging.txt", max_size=N)  
      → Returns True if file size exceeds N bytes  

Notes:
 - Default log file = logging.txt  
 - Default max size = 1 MB  
 - Rotated files are stored in the same directory with a `.bak` suffix  
 - Printed logs truncate long lines (default: 120 chars)  
 - Errors during decorated functions are caught and logged automatically  
""")

# =================== Example Usage ===================

if __name__ == "__main__":
    # Create a logger with 1 KB max file size for testing rotation
    my_logger = logger("example_logger", max_size=1024)

    @my_logger.logging()
    def add(a, b):
        return a + b

    @my_logger.logging()
    def divide(a, b):
        return a / b

    add(5, 3)
    divide(10, 2)
    divide(5, 0)  # will log ZeroDivisionError
    my_logger.log_info("This is a manual info log.")

    print("\n--- Logs for this logger ---")
    my_logger.show_logs()

    print("\n--- All logs ---")
    logger.show_all_logs()