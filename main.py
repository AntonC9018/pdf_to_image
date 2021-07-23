import os
from subprocess import Popen
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

def convert_pdf_to_images(pdf_path, output_folder_path):
    if not os.path.isfile(pdf_path):
        return NO_SUCH_FILE

    if not os.path.exists(output_folder_path):
        return NO_SUCH_DIRECTORY

    prev_dir = os.curdir
    os.chdir(output_folder_path)
    try:
        command = f"pdftoppm {quote(pdf_path)} image -jpeg"
        print(f"Running {command}")
        process = Popen(command, cwd=output_folder_path)
        exit_code = process.wait()
        print("Done")

        if exit_code != 0:
            return COMMAND_FAILURE.format(str(process.stderr))

    except OSError:
        return PROCCESS_OPEN_FAILURE.format("pdftoppm")

    finally:
        os.chdir(prev_dir)

    return SUCCESS


def ask_for_pdf_input():
    return askopenfilename(title="Select pdf to convert", filetypes=[('pdf', 'pdf')])

def ask_for_output_directory():
    return askdirectory(title="Select output path")


def start_file_conversion_workflow():
    pdf_path = ask_for_pdf_input()
    if not pdf_path: return

    output_folder_path = ask_for_output_directory()
    if not output_folder_path: return

    result_message = convert_pdf_to_images(pdf_path, output_folder_path)
    messagebox.showinfo(RESULT, result_message)


def start_link_conversion_workflow():
    link = askstring(title="Link to pdf document", prompt="Paste URL to pdf document")
    if not link: return

    output_folder_path = ask_for_output_directory()
    if not output_folder_path: return


def start_ui():
    app = Tk()

    def_font = tkinter.font.nametofont("TkDefaultFont")
    def_font.config(size=16)

    buttons = []
    buttons.append(tkinter.Button(app, text=CONVERT, command=start_file_conversion_workflow))
    buttons.append(tkinter.Button(app, text=CONVERT_LINK, command=start_link_conversion_workflow))
    for b in buttons: b.pack()

    # start_file_conversion_workflow()
    mainloop()


if __name__ == "__main__":
    start_ui()
    # convert_pdf_to_images(r"E:\Coding\python\pdf_to_image\New folder\2021010f.PDF", r"E:\Coding\python\pdf_to_image\New folder")

