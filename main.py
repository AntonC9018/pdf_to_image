import os

def quote(path : str) -> str:
    return '"' + path + '"'

NO_SUCH_FILE = "The specified file does not exist"
NO_SUCH_DIRECTORY = "The specified directory does not exist"
COMMAND_FAILURE = "Subcommand failure, could not convert.\n{0}"
PROCCESS_OPEN_FAILURE = "Could not open process '{0}'"
SUCCESS = "Success"
CONVERT = "Convert by selecting a file"
CONVERT_LINK = "Download the pdf from link, convert afterwards"
RESULT = "Result"
URL_CONTENT_TYPE = "The url is of wrong format: {0}. Expected {1}."
INVALID_URL = "Invalid URL: {0}"

def convert_pdf_to_images(pdf_path, output_folder):
    if not os.path.isfile(pdf_path):
        return NO_SUCH_FILE

    if not os.path.isdir(output_folder):
        return NO_SUCH_DIRECTORY

    try:
        command = f"pdftoppm {quote(pdf_path)} image -jpeg"
        print(f"Running {command}")
        process = subprocess.Popen(command, cwd=output_folder)
        exit_code = process.wait()

        if exit_code != 0:
            return COMMAND_FAILURE.format(str(process.stderr))

    except OSError:
        return PROCCESS_OPEN_FAILURE.format("pdftoppm")

    return SUCCESS


from urllib.parse import urlparse
import subprocess
import http.client
import ssl

def convert_pdf_url_to_images(url, output_folder, progress_callback=None):
    if progress_callback is None: 
        progress_callback = lambda total, added, current: print(f"transferred: {current} out of {total}")

    if not os.path.isdir(output_folder):
        return NO_SUCH_DIRECTORY

    try:
        parsed_url = urlparse(url)
        ssl_context = ssl.create_default_context()
        connection = http.client.HTTPSConnection(parsed_url.hostname, context=ssl_context)
        # bypass security: https://stackoverflow.com/a/16627277/9731532
        connection.request(method="GET", url=url, headers={ 'User-Agent': 'Mozilla/5.0' })
        response = connection.getresponse()

        content_type = response.headers.get_content_type()
        if content_type != "application/pdf":
            connection.close()
            return URL_CONTENT_TYPE.format(content_type, "application/pdf")

        content_length = int(response.headers.get('Content-Length'))

        command = "pdftoppm - image -jpeg"
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, cwd=output_folder)
        # file = open(os.path.join(output_folder, "test.pdf"), "wb")

        chunk_size = 8192
        current_amount = 0
        while True:
            chunk = response.read(chunk_size)
            current_amount += len(chunk)
            progress_callback(content_length, len(chunk), current_amount)
            
            if not chunk:
                # file.close()
                connection.close()
                process.stdin.close()
                exit_code = process.wait()
                if exit_code != 0:
                    return COMMAND_FAILURE.format(process.stderr)
                break
            process.stdin.write(chunk)
            process.stdin.flush()

    except OSError:
        return PROCCESS_OPEN_FAILURE.format("pdftoppm")

    except http.client.InvalidURL:
        return INVALID_URL.format(url)

    except Exception as exc:
        return str(exc) 

    return SUCCESS


import tkinter
from tkinter import mainloop, messagebox, Tk
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter.simpledialog import askstring
import tkinter.ttk
import tkinter.font

app = None
progress : tkinter.ttk.Progressbar = None


def ask_for_pdf_input():
    return askopenfilename(title="Select pdf to convert", filetypes=[('pdf', 'pdf')])

def ask_for_output_directory():
    return askdirectory(title="Select output path")


def start_file_conversion_workflow():
    pdf_path = ask_for_pdf_input()
    if not pdf_path: return

    output_folder = ask_for_output_directory()
    if not output_folder: return

    result_message = convert_pdf_to_images(pdf_path, output_folder)
    messagebox.showinfo(RESULT, result_message)


def start_url_pdf_conversion_workflow():
    url = askstring(title="Link to pdf document", prompt="Paste URL to pdf document")
    if not url: return

    output_folder_path = ask_for_output_directory()
    if not output_folder_path: return

    progress["value"] = 0

    def update_progress(total_bytes, added_bytes, current_bytes):
        progress["value"] = current_bytes / total_bytes * 100
        app.update_idletasks()

    result = convert_pdf_url_to_images(url, output_folder_path, update_progress)
    messagebox.showinfo(RESULT, result)
    progress["value"] = 0


def start_ui():
    global app
    global progress

    app = Tk()

    def_font = tkinter.font.nametofont("TkDefaultFont")
    def_font.config(size=16)

    buttons = []
    buttons.append(tkinter.Button(app, text=CONVERT, command=start_file_conversion_workflow))
    buttons.append(tkinter.Button(app, text=CONVERT_LINK, command=start_url_pdf_conversion_workflow))
    for b in buttons: b.pack()

    progress = tkinter.ttk.Progressbar(app, orient=tkinter.HORIZONTAL, length=300, mode='determinate')
    progress.pack(pady=5)

    # start_file_conversion_workflow()
    mainloop()


if __name__ == "__main__":
    start_ui()