import io
import os
import tkinter
from tkinter import mainloop, messagebox, Tk
from tkinter.filedialog import askdirectory, askopenfilename
from tkinter.simpledialog import askstring



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

from urllib.parse import urlparse
import shutil
import subprocess
import http.client
import ssl

def convert_pdf_url_to_images(url, output_folder):
    try:
        parsed_url = urlparse(url)
        ssl_context = ssl.create_default_context()
        connection = http.client.HTTPSConnection(parsed_url.hostname, context=ssl_context)
        # bypass security: https://stackoverflow.com/a/16627277/9731532
        connection.request(method="GET", url=url, headers={ 'User-Agent': 'Mozilla/5.0' })
        response = connection.getresponse()

        content_type = response.headers.get_content_type()
        if content_type != "application/pdf":
            raise Exception(content_type) 
        
        command = f"pdftoppm - image -jpeg"
        process = subprocess.Popen(command, stdin=subprocess.PIPE, cwd=output_folder)
        # file = open(os.path.join(output_folder, "test.pdf"), "wb")

        chunk_size = 8192
        current_amount = 0
        while True:
            chunk = response.read(chunk_size)
            current_amount += len(chunk)
            print(f"transferred: {current_amount}")
            if not chunk:
                # file.close()
                process.stdin.close()
                exit_code = process.wait()
                if exit_code != 0:
                    raise Exception("Non-zero exit code")
                break
            process.stdin.write(chunk)
            process.stdin.flush()

        connection.close()

    except Exception as exc:
        print(exc)

    print("done")


def start_url_pdf_conversion_workflow():
    url = askstring(title="Link to pdf document", prompt="Paste URL to pdf document")
    if not url: return

    output_folder_path = ask_for_output_directory()
    if not output_folder_path: return

    convert_pdf_url_to_images(url, output_folder_path)


def start_ui():
    app = Tk()

    def_font = tkinter.font.nametofont("TkDefaultFont")
    def_font.config(size=16)

    buttons = []
    buttons.append(tkinter.Button(app, text=CONVERT, command=start_file_conversion_workflow))
    buttons.append(tkinter.Button(app, text=CONVERT_LINK, command=start_url_pdf_conversion_workflow))
    for b in buttons: b.pack()

    # start_file_conversion_workflow()
    mainloop()


if __name__ == "__main__":
    # start_ui()
    # convert_pdf_to_images(r"E:\Coding\python\pdf_to_image\New folder\2021010f.PDF", r"E:\Coding\python\pdf_to_image\New folder")
    convert_pdf_url_to_images("https://media-cis-cdn.oriflame.com/-/media/MD/Images/Catalog/Brochures/2021010/EB72EA94B669547766596599FD4031F2/2021010.ashx?u=2107101123", r"E:\Coding\python\pdf_to_image\New folder")
    # convert_pdf_url_to_images("https://docs.python.org/3.7/library/http.client.html#module-http.client", None)

    # convert_pdf_url_to_images("http://www.africau.edu/images/default/sample.pdf", r"E:\Coding\python\pdf_to_image\New folder")