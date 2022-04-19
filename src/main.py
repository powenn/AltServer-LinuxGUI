import datetime
import hashlib
import json
import logging
import os
import subprocess
import sys
import threading
import time
from typing import List, Any

import requests
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QMessageBox, QSystemTrayIcon, QMenu, QAction, QDialog, QVBoxLayout, QLabel, QLineEdit, \
    QPushButton, QApplication, QProgressDialog

# Program constants
ALT_SERVER_NAME = "AltServer"
ALT_SERVER_VERSION = "v0.0.5"
ALT_SERVER_LINUX_NAME = "AltServer-Linux"
ALT_SERVER_MD5_SUM = "592f00dc6cf255c4277ec674711febdd"
ALT_STORE_NAME = "AltStore"
ALT_STORE_VERSION = "1_4_9"
ALT_STORE_MD5_SUM = "127add35f5a64a71ff30297a182b91ef"
GUI_NAME = "AltServer-LinuxGUI"
GUI_VERSION = "0.6"

# Path constants
PROGRAM_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
RESOURCES_DIRECTORY = os.path.join(PROGRAM_DIRECTORY, "resources")
USER_DATA_DIRECTORY = os.path.expanduser(f"~/.local/share/{GUI_NAME}")
USER_DATA_PATH = os.path.dirname(USER_DATA_DIRECTORY)
CONFIG_FILE_PATH = os.path.join(USER_DATA_DIRECTORY, "config.json")
LOG_DIRECTORY = os.path.join(USER_DATA_DIRECTORY, "logs")

# Networking constants
ALT_SERVER_URL = f"https://github.com/NyaMisty/AltServer-Linux/releases/download/{ALT_SERVER_VERSION}/AltServer-x86_64"
ALT_STORE_IPA_URL = f"https://cdn.altstore.io/file/altstore/apps/altstore/{ALT_STORE_VERSION}.ipa"
CHUNK_SIZE = 512
CONNECTION_CHECK_URL = "https://github.com"
CONNECTION_TIMEOUT = 5
MAX_CONNECTION_RETRIES = 5

# Logging constants
LOG_FILE_PATH = os.path.join(LOG_DIRECTORY, f"{GUI_NAME}-{GUI_VERSION}-{datetime.datetime.now()}.log")
LOG_MESSAGE_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
LOG_LEVEL = logging.INFO

# Dependency path constants
ALT_SERVER_EXEC = os.path.join(USER_DATA_DIRECTORY, f"{ALT_SERVER_NAME}_{ALT_SERVER_VERSION}.exec")
ALT_STORE_IPA_PATH = os.path.join(USER_DATA_DIRECTORY, f"{ALT_STORE_NAME}_{ALT_STORE_VERSION}.ipa")
IDEVICEPAIR_EXEC = "idevicepair"
IDEVICE_ID_EXEC = "idevice_id"

# Config keys
CONFIG_KEY_ALT_SERVER_UPDATE = "alt_server_update_date"
CONFIG_KEY_ALT_STORE_UPDATE = "alt_store_update_date"
CONFIG_KEY_START_DAEMON = "start_daemon_on_launch"

# GUI elements
GUI_APPLICATION = QApplication(sys.argv)
TRAY_MENU: QSystemTrayIcon or None = None
DAEMON_STATUS_TOGGLE: QAction or None = None
START_DAEMON_ON_LAUNCH_TOGGLE: QAction or None = None

# Runtime variables
LOGGING_INITIALIZED = False
DAEMON_OBJECT = None


class AltServerDaemon:
    """
    Container object that handles interfacing with the AltServer daemon
    """
    __daemon_subprocess = None
    __daemon_thread = None

    def daemon_is_running(self) -> bool:
        """
        Checks if the daemon is still running
        :return: True if the daemon is running, False if not
        """
        if self.__daemon_subprocess is not None:
            if self.__daemon_subprocess.poll() is None:
                return True

        return False

    def start_daemon(self):
        """
        Starts the AltServer daemon
        :return: None
        """
        self.__daemon_thread = threading.Thread(daemon=True,
                                                name="altserver_daemon",
                                                target=self.__daemon_process)
        self.__daemon_thread.start()

    def stop_daemon(self):
        """
        Stops the AltServer daemon if it is running
        :return: None
        """
        if self.__daemon_subprocess is not None:
            self.__daemon_subprocess.kill()

        if self.__daemon_thread is not None:
            self.__daemon_thread.join()

        while self.daemon_is_running():
            logging.info(f"Waiting for {ALT_SERVER_NAME} daemon to stop")
            time.sleep(1)

        logging.info(f"Stopped {ALT_SERVER_NAME} daemon")

    def __daemon_process(self):
        """
        Actual daemon process that runs in the background once the daemon thread is started
        :return:
        """
        logging.info(f"Starting {ALT_SERVER_NAME} daemon")
        self.__daemon_subprocess = subprocess.Popen(ALT_SERVER_EXEC,
                                                    cwd=USER_DATA_PATH,
                                                    stderr=subprocess.STDOUT,
                                                    stdout=subprocess.PIPE)

        while True:
            # Update GUI to reflect daemon status
            self.__update_gui_status()

            # Log any output from the daemon process
            if self.__daemon_subprocess.poll() is None:
                daemon_stdout = self.__daemon_subprocess.stdout.readline().decode().strip()
                if daemon_stdout:
                    logging.info(f"{ALT_SERVER_NAME} Daemon: {daemon_stdout}")

            # If the daemon process stops print the exit code
            else:
                logging.info(f"{ALT_SERVER_NAME} Daemon: Exited with code {self.__daemon_subprocess.poll()}")
                break

    def __update_gui_status(self):
        """
        Updates relevant GUI elements to reflect the daemon's current status
        :return: None
        """
        if self.daemon_is_running():
            DAEMON_STATUS_TOGGLE.setText("AltServer daemon is running")
            DAEMON_STATUS_TOGGLE.setChecked(True)
        else:
            DAEMON_STATUS_TOGGLE.setText("AltServer daemon is stopped")
            DAEMON_STATUS_TOGGLE.setChecked(False)


class GuiDownloadThread(QThread):
    """
    Thread that handles downloading a file with a GUI progress bar
    """

    def __init__(self, file_url: str, output_path: str, progress_dialog: QProgressDialog):
        """
        Thread that handles downloading a file with a GUI progress bar
        :param file_url: URL to the file we want to download, Example: "https://path_to.file.com/file.zip"
        :param output_path: Local path where the file should be saved to, Example: "~/Downloads"
        :param progress_dialog: Popup dialog box containing a progress bar that tracks download status
        """
        super().__init__()
        self.file_url = file_url
        self.output_path = output_path
        self.progress_dialog = progress_dialog

    def run(self):
        """
        Executes the download process
        :return: None
        """
        download_file(self.file_url, self.output_path, self.progress_dialog)


def connection_check() -> bool:
    """
    Checks if we are able to connect to the internet
    :return: True if able to successfully connect to the internet, False if not
    """
    try:
        requests.get(CONNECTION_CHECK_URL, timeout=CONNECTION_TIMEOUT)
        return True
    except (requests.ConnectionError, requests.Timeout):
        logging.error(f"Unable to connect to test URL, '{CONNECTION_CHECK_URL}'")
        return False


def create_directory(directory_path: str, fail_exit: bool = False):
    """
    Attempts to a directory on the local host, optionally exits out if unable
    :param directory_path: Path to the directory we want to create, Example: "~/data"
    :param fail_exit: Boolean that denotes if the program should exit if unable to create the directory
    :return: None
    """
    if not os.path.exists(directory_path):
        try:
            if LOGGING_INITIALIZED:
                logging.info(f"Creating directory: '{directory_path}'")

            os.makedirs(directory_path)
        except Exception as err:
            if LOGGING_INITIALIZED:
                logging.error(f"Unable to create directory '{directory_path}', {err}")

            if fail_exit:
                sys.exit(1)


def download_file(file_url: str, output_path: str, progress_dialog: QProgressDialog = None) -> bool:
    """
    Downloads a file from the internet and saves it locally
    :param file_url: URL to the file we want to download, Example: "https://path_to.file.com/file.zip"
    :param output_path: Local path where the file should be saved to, Example: "~/Downloads"
    :param progress_dialog: Popup dialog box containing a progress bar that tracks download status
    :return: True if file was successfully downloaded, False if not
    """
    retry_counter = 0
    logging.info(f"Downloading file '{file_url}' to '{output_path}'")

    while True:
        try:
            with requests.get(file_url, stream=True, timeout=CONNECTION_TIMEOUT) as request:
                if request.ok:
                    if progress_dialog is not None:
                        chunk_counter = 0
                        progress_dialog.setRange(0, int(int(request.headers.get("Content-length")) / CHUNK_SIZE))

                    with open(output_path, "wb") as output_file:
                        for chunk in request.iter_content(chunk_size=CHUNK_SIZE):
                            output_file.write(chunk)

                            if progress_dialog is not None:
                                chunk_counter += 1
                                progress_dialog.setValue(chunk_counter)

                                if progress_dialog.wasCanceled():
                                    return False

                    logging.info(f"Successfully downloaded '{output_path}'")
                    return True

            raise requests.exceptions.ConnectionError(f"Failed to download file from URL '{file_url}'. {request.text}")

        except Exception as err:
            retry_counter += 1
            if retry_counter >= MAX_CONNECTION_RETRIES:
                logging.error(f"Failed to download '{file_url}' {MAX_CONNECTION_RETRIES} times, giving up. "
                              f"Error: {err}")
                return False
            else:
                time.sleep(2 * retry_counter)  # Sleep for a moment before attempting to download again


def exec_path_check(exec_name: str) -> bool:
    """
    Checks if the given exec is accessible via $PATH
    :param exec_name: Name of the exec we are checking for, Example: "git"
    :return: True if the exec could be located, False if not
    """
    for path in os.environ["PATH"].split(os.pathsep):
        exec_file = os.path.join(path, exec_name)
        if os.path.isfile(exec_file) and os.access(exec_file, os.X_OK):
            return True

    logging.error(f"Unable to locate exec: '{exec_name}'. Ensure it is installed and accessible via PATH.")
    return False


def get_config_value(config_key: str, default_value: Any) -> Any:
    """
    Retrieves a value from the config
    :param config_key: Key for the value we want to get, Example: "locale"
    :param default_value: Value that should be returned if unable to load from config, Example: "en_US"
    :return: Config value or default
    """
    if os.path.isfile(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r") as config_file:
            config_dictionary = json.load(config_file)
            if config_key in config_dictionary.keys():
                return config_dictionary.get(config_key)

    return default_value


def get_resource(resource_file_name: str) -> str or None:
    """
    Attempts to get a resource file from the 'resources' directory
    :param resource_file_name: Name of the resource file we want to get, Example: "icon.png"
    :return: Path to the resource if it exists, or None if not
    """
    resource_path = os.path.join(RESOURCES_DIRECTORY, resource_file_name)
    if os.path.isfile(resource_path):
        return resource_path

    logging.error(f"Failed to locate resource file: '{resource_path}'")
    return None


def get_ios_device_udids() -> List[str]:
    """
    Gets the UDIDs of connected iOS devices
    :return: List of UDIDs from connected iOS devices, can be empty if unable to get UDIDs or no devices are connected
    """
    return subprocess.check_output([IDEVICE_ID_EXEC, "-l"], stderr=subprocess.DEVNULL).decode().split("\n")


def initialize_logging():
    """
    Initializes logging functionality
    :return: None
    """
    global LOGGING_INITIALIZED

    # Create log directory
    create_directory(LOG_DIRECTORY, fail_exit=True)

    # Configure logging to write to log file
    logging.basicConfig(format=LOG_MESSAGE_FORMAT,
                        filename=LOG_FILE_PATH,
                        level=LOG_LEVEL)

    # Configure logging to print messages to console
    console = logging.StreamHandler()
    console.setLevel(LOG_LEVEL)
    console.setFormatter(logging.Formatter(LOG_MESSAGE_FORMAT))
    logging.getLogger().addHandler(console)

    logging.info(f"Initialized log file: '{LOG_FILE_PATH}'")
    LOGGING_INITIALIZED = True


def pair_ios_device() -> bool:
    """
    Attempts to pair with a connected iOS device
    :return: True if able to pair, False if not
    """
    try:
        subprocess.check_call([IDEVICEPAIR_EXEC, "pair"], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        logging.info("Successfully paired with connected iOS device")
        return True
    except subprocess.CalledProcessError:
        logging.error("Failed to pair with connected iOS device")
        return False


def update_config(config_key: str, config_value: Any):
    """
    Updates the config with a new value
    :param config_key: Key for the value that we want to store in the config, Example: "locale"
    :param config_value: Value that should be stored in the config, Example: "en_US"
    :return: None
    """
    config_dictionary = {}

    if os.path.isfile(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r") as config_file:
            config_dictionary = json.load(config_file)

    config_dictionary.update({config_key: config_value})

    with open(CONFIG_FILE_PATH, "w") as config_file:
        config_file.write(json.dumps(config_dictionary, indent=4))


def gui_about_message():
    """
    Displays an 'about this program' popup window
    :return: None
    """
    msg_box = QMessageBox()
    msg_box.setIconPixmap(QPixmap(get_resource("Icon@128.png")))
    msg_box.setWindowTitle(f"About {ALT_SERVER_NAME}")
    msg_box.setInformativeText(f"{GUI_NAME} Version: {GUI_VERSION}\n"
                               f"{ALT_SERVER_LINUX_NAME} Version: {ALT_SERVER_VERSION}\n"
                               f"{ALT_STORE_NAME} Version: {ALT_STORE_VERSION.replace('_', '.')}\n\n"
                               f"{GUI_NAME} by powenn\n"
                               f"{ALT_SERVER_LINUX_NAME} by NyaMisty\n"
                               f"{ALT_SERVER_NAME} and {ALT_STORE_NAME} by Riley Testut")
    msg_box.setDetailedText("Source code:\n"
                            "https://github.com/powenn/AltServer-LinuxGUI")
    msg_box.exec()


def gui_critical_error(title: str, detailed_message: str, exit_code: int = 1):
    """
    Raises a message box with a critical error message and then exits
    :param title: Error message title, Example: "Failed to download file.zip"
    :param detailed_message: Detailed information about error, Example: "Verify file exists"
    :param exit_code: Exit code to exit with after displaying the message box, Example: 1
    :return: None
    """
    message_box = QMessageBox()
    message_box.setIcon(QMessageBox.Critical)
    message_box.setWindowTitle(title)
    message_box.setText(f"{title}.\n\n{detailed_message}.")
    message_box.exec()
    sys.exit(exit_code)


def gui_download(file_url: str, output_path: str, md5_sum: str) -> bool:
    """
    Download a file with a GUI progress box, verifies the file's integrity after download is complete
    :param file_url: URL to the file we want to download, Example: "https://path_to.file.com/file.zip"
    :param output_path: Local path where the file should be saved to, Example: "~/Downloads"
    :param md5_sum: MD5 checksum used to verify the file's integrity, Example: "592f00dc6cf255c4277ec674711febdd"
    :return: True if file downloaded and MD5 checksum matches, False if not
    """
    file_name = os.path.basename(output_path)

    # Create progress dialog window
    progress_dialog = QProgressDialog()
    progress_dialog.setWindowTitle(f"Downloading {file_name}")
    progress_dialog.setLabelText(file_url)
    progress_dialog.setFixedSize(progress_dialog.size())
    progress_dialog.setValue(0)

    # Create download thread and start download
    download_thread = GuiDownloadThread(file_url, output_path, progress_dialog)
    download_thread.start()
    progress_dialog.exec()

    # Check MD5 sum to verify file was downloaded successfully
    if os.path.isfile(output_path):
        with open(output_path, "rb") as downloaded_file:
            if md5_sum == hashlib.md5(downloaded_file.read()).hexdigest():
                logging.info(f"Verified integrity of '{file_name}'")
                return True

    logging.error(f"Unable to verify integrity of '{file_name}'")
    return False


def gui_initialization():
    """
    Initializes GUI items and constructs
    :return: None
    """
    try:
        logging.info(f"Starting {GUI_NAME}")

        # Initialize QT application
        icon = QIcon(get_resource("MenuBar.png"))
        GUI_APPLICATION.setApplicationName("AltServer")
        GUI_APPLICATION.setQuitOnLastWindowClosed(False)
        GUI_APPLICATION.setWindowIcon(QIcon(get_resource("AppIcon.png")))

        # Initialize menu and add 'About' option
        menu = QMenu()
        menu_item_about = QAction(f"About {ALT_SERVER_NAME}")
        menu_item_about.triggered.connect(gui_about_message)
        menu.addAction(menu_item_about)
        menu.addSeparator()

        # Add 'Install' option to menu
        menu_item_install = QAction(f"Install {ALT_STORE_NAME}")
        menu_item_install.triggered.connect(gui_install_alt_store)
        menu.addAction(menu_item_install)
        menu.addSeparator()

        # Add 'Pair' option to menu
        menu_item_pair = QAction("Pair")
        menu_item_pair.triggered.connect(pair_ios_device)
        menu.addAction(menu_item_pair)
        menu.addSeparator()

        # Add 'AltServer daemon toggle' option to menu
        global DAEMON_STATUS_TOGGLE
        DAEMON_STATUS_TOGGLE = QAction("Daemon toggle not initialized", checkable=True)
        DAEMON_STATUS_TOGGLE.triggered.connect(gui_toggle_daemon)
        DAEMON_STATUS_TOGGLE.setChecked(False)
        menu.addAction(DAEMON_STATUS_TOGGLE)

        # Add 'Autostart AltServer' option to menu
        global START_DAEMON_ON_LAUNCH_TOGGLE
        START_DAEMON_ON_LAUNCH_TOGGLE = QAction(f"Start {ALT_SERVER_NAME} daemon on launch", checkable=True)
        START_DAEMON_ON_LAUNCH_TOGGLE.triggered.connect(gui_toggle_start_daemon_on_launch)
        START_DAEMON_ON_LAUNCH_TOGGLE.setChecked(get_config_value(CONFIG_KEY_START_DAEMON, default_value=False))
        menu.addAction(START_DAEMON_ON_LAUNCH_TOGGLE)
        menu.addSeparator()

        # Add 'Quit' option to menu
        menu_item_quit = QAction(f"Quit {ALT_SERVER_NAME}")
        menu_item_quit.triggered.connect(gui_quit)
        menu_item_quit.setCheckable(False)
        menu_item_quit.setShortcut("Ctrl+Q")
        menu.addAction(menu_item_quit)

        # Initialize system tray icon and add menu to it
        global TRAY_MENU
        TRAY_MENU = QSystemTrayIcon()
        TRAY_MENU.setIcon(icon)
        TRAY_MENU.setVisible(True)
        TRAY_MENU.setContextMenu(menu)

        # If the user enabled auto start, start the daemon
        if get_config_value(CONFIG_KEY_START_DAEMON, default_value=False):
            DAEMON_OBJECT.start_daemon()

        # Start application
        GUI_APPLICATION.exec_()
    except Exception as err:
        logging.error(f"Failed to initialize GUI, {err}")
        sys.exit(1)


def gui_install_alt_store():
    """
    Installs AltStore on the connected iOS device
    :return: None
    """
    restart_daemon = False

    def installation_workflow():
        """
        AltStore installation process triggered by the 'Install' button
        :return: None
        """
        output_buffer = []
        install_command = [ALT_SERVER_EXEC,
                           "-u", connected_device_udids[0],
                           "-a", id_input_area.text(),
                           "-p", password_input_area.text(),
                           ALT_STORE_IPA_PATH]

        # Close the account information input window
        account_area.close()

        # Start the installation process
        logging.info(f"Installing {ALT_STORE_NAME} to connected iOS device: '{connected_device_udids[0]}'")
        install_process = subprocess.Popen(install_command,
                                           cwd=USER_DATA_PATH,
                                           stderr=subprocess.STDOUT,
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE)

        # Watch the installation process and react accordingly
        while True:
            if install_process.poll() is not None:
                logging.error(f"Installation process terminated unexpectedly. Exit code: {install_process.poll()}")
                return

            try:
                output_line = install_process.stdout.readline().decode().strip()
                line_log_message = f"{ALT_SERVER_NAME}: {output_line}"
                output_buffer.append(output_line)
            except ValueError:
                return

            # Install succeeded workflow
            if "Installation Succeeded" in output_line:
                logging.info(line_log_message)

                install_process.terminate()
                TRAY_MENU.showMessage("Installation Succeeded",
                                      "AltStore was successfully installed",
                                      QSystemTrayIcon.Information,
                                      5000)
                return

            # Install failed workflow
            elif "Installation Failed" in output_line:
                error_message = install_process.stdout.readline().decode().strip()
                logging.error(line_log_message)
                logging.error(f"{ALT_SERVER_NAME}: {error_message}")

                install_process.terminate()
                fail_message = f"{output_line}\n\n{error_message}"
                fail_popup = QMessageBox()
                fail_popup.setText(fail_message)
                fail_popup.exec()
                return

            # User prompted to continue workflow
            elif "Are you sure you want to continue?" in output_line:
                logging.warning(line_log_message)

                warning_message = "\n\n".join(output_buffer[-3:])
                warning_popup = QMessageBox()
                warning_button = QMessageBox.warning(warning_popup,
                                                     "Alert",
                                                     warning_message,
                                                     QMessageBox.Yes | QMessageBox.No,
                                                     QMessageBox.Yes)

                if warning_button == QMessageBox.Yes:
                    install_process.communicate(input=b"\n")

                if warning_button == QMessageBox.No:
                    install_process.terminate()
                    cancel_message_box = QMessageBox()
                    cancel_message_box.setText("Installation Canceled")
                    cancel_message_box.exec()
                    return

            # Two-factor authentication workflow
            elif "Requires two factor..." in output_line:

                def two_factor_button_action():
                    """
                    Sends two-factor authentication code provided by the user to the installation process
                    :return: None
                    """
                    two_factor_dialog.close()
                    code_2fa = two_factor_input.text()
                    logging.info(f"Submitting 2FA code: {code_2fa}")
                    code_2fa = code_2fa + "\n"
                    code_2fa_bytes = bytes(code_2fa.encode())
                    install_process.communicate(input=code_2fa_bytes)

                logging.info(line_log_message)

                two_factor_dialog = QDialog()
                two_factor_dialog.setWindowTitle("Two-Factor Authentication Required")
                two_factor_layout = QVBoxLayout()
                two_factor_label = QLabel(
                    "Please enter the two-factor authentication code that was sent to your device")
                two_factor_input = QLineEdit(placeholderText="2FA Code")
                send_two_factor_button = QPushButton()
                send_two_factor_button.setText("Send")
                send_two_factor_button.clicked.connect(two_factor_button_action)
                two_factor_layout.addWidget(two_factor_label)
                two_factor_layout.addWidget(two_factor_input)
                two_factor_layout.addWidget(send_two_factor_button)
                two_factor_dialog.setLayout(two_factor_layout)
                two_factor_dialog.exec()

            # If the output line is not handled just log it
            else:
                logging.info(line_log_message)

    # Stop the daemon if it's running
    if DAEMON_OBJECT.daemon_is_running():
        restart_daemon = True
        DAEMON_OBJECT.stop_daemon()

    # Throw an error message if unable to pair with connected iOS device
    if not pair_ios_device():
        errmsg_box = QMessageBox()
        errmsg_box.setText("Please make sure your iOS device is connected.\n\n"
                           "You may need to accept the trust dialog on your device before trying again.")
        errmsg_box.exec()
        return

    # Throw an error message if unable to get iOS device UDID
    connected_device_udids = get_ios_device_udids()
    if len(connected_device_udids) < 1:
        errmsg_box = QMessageBox()
        errmsg_box.setText("Unable to retrieve UDID for connected iOS device.")
        errmsg_box.exec()
        return

    # GUI for installation process
    account_area = QDialog()
    layout = QVBoxLayout()
    privacy_msg = QLabel(
        "Your Apple ID and password are not saved\n"
        "and are only sent to Apple for authentication.")
    privacy_msg.setFont(QFont("Arial", 10))
    label = QLabel("Please Enter your Apple ID and password")
    id_input_area = QLineEdit(placeholderText="Apple ID")
    password_input_area = QLineEdit(placeholderText="Password")
    password_input_area.setEchoMode(QLineEdit.EchoMode.Password)
    install_button = QPushButton()
    install_button.setText("Install")
    install_button.clicked.connect(installation_workflow)
    layout.addWidget(label)
    layout.addWidget(privacy_msg)
    layout.addWidget(id_input_area)
    layout.addWidget(password_input_area)
    layout.addWidget(install_button)
    account_area.setLayout(layout)
    account_area.exec()

    # Start the daemon if it was running before the install started
    if restart_daemon:
        DAEMON_OBJECT.start_daemon()


def gui_toggle_daemon():
    """
    Restarts the AltServer daemon
    :return: None
    """
    if DAEMON_OBJECT.daemon_is_running():
        DAEMON_OBJECT.stop_daemon()
    else:
        DAEMON_OBJECT.start_daemon()


def gui_toggle_start_daemon_on_launch():
    """
    Toggles the 'Start daemon on launch' option
    :return: None
    """
    new_toggle_status = not get_config_value(CONFIG_KEY_START_DAEMON, default_value=False)
    update_config(CONFIG_KEY_START_DAEMON, new_toggle_status)
    START_DAEMON_ON_LAUNCH_TOGGLE.setChecked(new_toggle_status)


def gui_quit():
    """
    Quits the program and any subprocesses
    :return: None
    """
    logging.info(f"Exiting {GUI_NAME}")
    DAEMON_OBJECT.stop_daemon()
    GUI_APPLICATION.quit()
    sys.exit(0)


if __name__ == "__main__":
    # Create data directory and initialize logging
    create_directory(USER_DATA_DIRECTORY, fail_exit=True)
    initialize_logging()

    # If idevicepair is not accessible, display an error message window and then exit
    if not exec_path_check(IDEVICEPAIR_EXEC):
        gui_critical_error(title=f"{IDEVICEPAIR_EXEC} could not be located",
                           detailed_message="Verify libimobiledevice is installed")

    # If idevice_id is not accessible, display an error message window and then exit
    if not exec_path_check(IDEVICE_ID_EXEC):
        gui_critical_error(title=f"{IDEVICE_ID_EXEC} could not be located",
                           detailed_message="Verify libimobiledevice is installed")

    # If unable to connect to the internet, exit out
    if not connection_check():
        gui_critical_error(title="Unable to connect to the internet",
                           detailed_message="Verify this host has a valid network connection")

    # Download AltServer Linux exec if needed
    if not os.path.exists(ALT_SERVER_EXEC):
        if gui_download(file_url=ALT_SERVER_URL, output_path=ALT_SERVER_EXEC, md5_sum=ALT_SERVER_MD5_SUM):
            update_config(CONFIG_KEY_ALT_SERVER_UPDATE, datetime.datetime.now().strftime("%c"))
            os.chmod(ALT_SERVER_EXEC, 0o755)
        else:
            os.remove(ALT_SERVER_EXEC)
            gui_critical_error(title=f"Failed to download {ALT_SERVER_LINUX_NAME}",
                               detailed_message=f"Please try again later")

    # Download AltStore IPA if needed
    if not os.path.exists(ALT_STORE_IPA_PATH):
        if gui_download(file_url=ALT_STORE_IPA_URL, output_path=ALT_STORE_IPA_PATH, md5_sum=ALT_STORE_MD5_SUM):
            update_config(CONFIG_KEY_ALT_STORE_UPDATE, datetime.datetime.now().strftime("%c"))
        else:
            os.remove(ALT_STORE_IPA_PATH)
            gui_critical_error(title=f"Failed to download {ALT_STORE_IPA_PATH}",
                               detailed_message=f"Please try again later")

    # Initialize daemon container object
    DAEMON_OBJECT = AltServerDaemon()

    # Start GUI
    gui_initialization()
