import printer
import urllib.request
import urllib.error
import time
import threading
from bs4 import BeautifulSoup
# from bs4.diagnose import diagnose

# classrooms = all room numbers
classrooms = [301, 302, 303, 307, 308, 310, 311, 312, 321, 322,
              401, 402, 403, 406, 407, 408, 409, 416, 418, 421, 425, 427, 428, 429, 434, 435, 436]
online_printers = []  # list of printer.Printer objects
status_thread = None  # To always run check_status in the background


def network_setup() -> None:
    """
    Based on the classroom list, try to create a printer and add it to online printers
    """
    global classrooms, online_printers
    for rm in classrooms:
        try:
            online_printers.append(printer.Printer(rm))
            print("RM", rm, "fetched")

            with open("index.html") as html_file:
                text = html_file.read()
                soup = BeautifulSoup(text, 'html.parser')
                button = '''<button type="button" id="{room}" class="btn btn-success" data-toggle="modal" data-target="#Modal">{room}</button>\n'''
                button_soup = BeautifulSoup(button.format(room=rm), 'html.parser')
                soup.body.h4.append(button_soup)

            with open("index.html", "w") as output:
                output.write(str(soup))

            html_file.close()
            output.close()

        except urllib.error.URLError:
            print("Could not get printer info [GLOBAL]\n")


def check_status() -> None:
    """
    Pulls status from webpage, prints status on console.
    While program is running, check status of network printers every 5 minutes
    """
    global online_printers
    while True:
        for prntr in online_printers:
            prntr.update_info()
            # To show all printers after
            # print("RM", prntr.location, prntr.p_url + ":")
            # prntr.show_status()
        time.sleep(10)

        # if datetime == 12:00 AM:
        #     online_printers = []
        #     network_setup()


def update_modal(rm) -> None:
    global online_printers
    p_found = None
    for p in online_printers:
        if p.room == rm:
            p_found = p

    # HTML modal updating
    with open("index.html") as html_file:
        text = html_file.read()
        soup = BeautifulSoup(text, 'html.parser')

        model = soup.body.h3
        status = soup.find("h3", id="status")
        model.append("Model here " + p_found.model)
        status.append("Status here " + p_found.status)

    with open("index.html", "w") as output:
        output.write(str(soup))

    html_file.close()
    output.close()


def _refresh_thread() -> None:
    global status_thread
    status_thread = threading.Thread(target=check_status)
    status_thread.daemon = True
    status_thread.start()


if __name__ == '__main__':
    print("Building network...")
    network_setup()
    _refresh_thread()
    user = ''
    while True:
        user = input("printer-tool:~$ ")
        if user == "quit":
            print("Closing printer-tool...")
            break
        elif user == "ls":
            for p in online_printers:
                print("ROOM " + p.location + ":")
                p.show_status()
        elif user == "room":
            r = ''
            found = False
            while not found:
                r = input("Select room: ")
                for p in online_printers:
                    if p.location == r:
                        print("ROOM " + p.location + ":")
                        p.show_status()
                        found = True
                if not found:
                    print("Room not found. Select from the following:")
                    for p in online_printers:
                        print('\t' + p.location)
        elif user == "refresh":
            for p in online_printers:
                p.update_info()
            print("All printer information is up-to-date")
        elif user == "reload":
            online_printers = []
            print("Searching for printers...")
            network_setup()
            for p in online_printers:
                p.update_info()
            print("Printer list updated")
        elif user == "help":
            print("\tls     \tList all printers\n"
                  "\troom   \tSelect a room\n"
                  "\trefresh\tGet latest status of all printers\n"
                  "\treload \tIdentify all network printers\n"
                  "\tquit   \tTerminate program\n")
        else:
            print("Invalid Command. Type 'help' to see list of commands")
    print("\tTermination success")
