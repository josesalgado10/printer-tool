import urllib.request
from bs4 import BeautifulSoup
# from bs4.diagnose import diagnose


class Printer:
    def __init__(self, room: int):
        """
        This function initializes a printer object. It takes a room as a parameter and builds a URL based on that.
        URL built redirects to printer info URL, used to webscrape based on printer type.
        """
        univ_url = "http://prt-"
        self.p_url = univ_url + str(room)
        self.redir = urllib.request.urlopen(self.p_url).url
        self.location = str(room)

        # For parse_info: [0] for main page, [1] for main info, [2] for config (if applicable)
        self.parse_info = []
        self.model = ""
        self._determine_model()
        self.status = ""
        self.toner_lvl = ""
        self.drum_lvl = ""
        self.curr_page = ""
        self.latest_error = ""

# Private Functions

    def _determine_model(self) -> None:
        """
        Based on the redirected URL, we can determine the printer type.
        The code only supports the Brother printers located in the classrooms.
        This code visits each webpage with important printer info and adds it to the parse_info list attribute.
        This list is later parsed in _parse_content().
        """
        if self.redir[14:] == "/printer/main.html":  # For Brother HL-2270DW
            self.model = "Brother v1"
            with urllib.request.urlopen(self.redir) as main_page:
                content = str(main_page.read())
                self.parse_info.append(content)  # [0] content for main page
                # print(content)
            with urllib.request.urlopen(self.p_url + "/printer/maininfo.html") as main_info:
                content = str(main_info.read())
                self.parse_info.append(content)  # [1] content for maintenance information
                # print(content)
            with urllib.request.urlopen(self.p_url + "/printer/configu.html") as config:
                content = str(config.read())
                self.parse_info.append(content)  # [2] content for configuration
                # print(content, '\n')
            main_page.close()
            main_info.close()
            config.close()
        elif self.redir[14:] == "/general/status.html":  # For Brother HL-L5100DN & MFC-L2700DW
            self.model = "Brother v2"
            with urllib.request.urlopen(self.redir) as main_page:
                content = str(main_page.read())
                self.parse_info.append(content)  # [0] content for main page
                # print(content)
            with urllib.request.urlopen(self.p_url + "/general/information.html?kind=item") as main_info:
                content = str(main_info.read())
                self.parse_info.append(content)  # [1] content for maintenance information
                # print(content, '\n')
            main_page.close()
            main_info.close()
        else:
            print("Cannot determine printer type")

    def _parse_content(self) -> None:
        """
        This function parses the content in parse_info. It scrapes the html pages using the Beautiful Soup library.
        If needed, more attributes can be added to the scraping list.
        """
        try:
            if self.model == "Brother v1":
                # set status
                soup = BeautifulSoup(self.parse_info[0], 'html.parser')
                self.status = soup.find("tt").get_text().replace('\\r', '').strip()

                # set toner level
                soup = BeautifulSoup(self.parse_info[2], 'html.parser')
                self.toner_lvl = soup.find(attrs={"align": "LEFT"}).get_text(" ")

                # set true model
                soup = BeautifulSoup(self.parse_info[1], 'html.parser')
                self.model = soup.find_all(attrs={"valign": "TOP"})[1].get_text(strip=True)[14:]

                # set drum level
                self.drum_lvl = soup.find_all(attrs={"valign": "TOP"})[12].get_text(strip=True)[25:]

                # set current page
                self.curr_page = soup.find_all(attrs={"valign": "TOP"})[7].get_text()[14:]

                # set latest error
                info = soup.find_all(attrs={"valign": "TOP"})[53].get_text("|").split("|")
                self.latest_error = info[1] + " " + info[2].replace(":   ", " ")

                ''' this is used to find all info in main info page '''
                # for x in soup.find_all(attrs={"valign": "TOP"}):
                #     print(x.get_text())

            elif self.model == "Brother v2":
                # set status
                soup = BeautifulSoup(self.parse_info[0], 'html.parser')
                self.status = soup.find("div", id="moni_data").get_text()

                # set true model
                soup = BeautifulSoup(self.parse_info[1], 'html.parser')
                self.model = soup.find_all(attrs={"class": "items"})[0].get_text("|").split("|")[1]

                # set toner level
                self.toner_lvl = soup.find_all(attrs={"class": "items"})[2].get_text("|").split("|")[-1]

                # set drum level
                self.drum_lvl = soup.find_all(attrs={"class": "items"})[2].get_text("|").split("|")[2]

                # set current page
                self.curr_page = soup.find_all(attrs={"class": "items"})[1].get_text("|").split("|")[1]

                # set last error
                info = soup.find("table", attrs={"class": "list errorHistory"}).get_text("|").split("|")
                self.latest_error = info[1] + " " + info[2] + ": " + info[3].replace("\xa0:\xa0", "")

                ''' this is used to find all info in main info page '''
                # for x in soup.find_all(attrs={"class": "items"}):
                #     print(x.get_text("|").split("|"))
        except IndexError:
            print("\tCannot parse " + self.p_url + ". Please visit for details.")

    def _update_status(self) -> None:  # TODO
        """
        Changes displayed printer status by parsing the content in parse_info.
        Updates HTML file
        """
        pass

    # Public Functions

    def update_info(self):
        """
        Based on the printer model, the function pulls an updated printer webpage.
        This HTML text is stored in parse_info and can be parsed by calling update_status, which is done at the end of
        the function.
        """
        if self.model == "Brother HL-2270DW series":
            with urllib.request.urlopen(self.redir) as main_page:
                content = str(main_page.read())
                self.parse_info[0] = content  # [0] content for main page
            with urllib.request.urlopen(self.p_url + "/printer/maininfo.html") as main_info:
                content = str(main_info.read())
                self.parse_info[1] = content  # [1] content for maintenance information
            with urllib.request.urlopen(self.p_url + "/printer/configu.html") as config:
                content = str(config.read())
                self.parse_info[2] = content  # [2] content for configuration
            main_page.close()
            main_info.close()
            config.close()
        elif self.model == "Brother HL-L5100DN series" or self.model == "Brother MFC-L2700DW series":
            with urllib.request.urlopen(self.redir) as main_page:
                content = str(main_page.read())
                self.parse_info[0] = content  # [0] content for main page
            with urllib.request.urlopen(self.p_url + "/general/information.html?kind=item") as main_info:
                content = str(main_info.read())
                self.parse_info[1] = content  # [1] content for maintenance information
            main_page.close()
            main_info.close()
        self._parse_content()

    def show_status(self) -> None:
        """
        Prints all current printer attributes
        """
        print("\tModel:", self.model)
        print("\tStatus:", self.status)
        print("\tToner:", self.toner_lvl)
        print("\tDrum:", self.drum_lvl)
        print("\tCurrent Page:", self.curr_page)
        print("\tLatest Error:", self.latest_error)
