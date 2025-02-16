from configparser import ConfigParser
from nornir import InitNornir
from nornir.core.filter import F as nf


class MvDB:
    """TODO"""
    subdir = "archives/"
    cfg = subdir + "config.yml"
    defaults = subdir + "default.yml"
    hosts =  subdir + "movies.yml"
    ini = subdir + "tech_specs.ini"

    def __init__(
        self,
        cfgFile: str=cfg,
        defaultFile: str=defaults,
        hostFile: str=hosts,
        iniFile: str=ini
    ):
        """Initializes MvDB Nr instance using specified inventory files.
        
        Args:
          cfgFile(str):
            Nornir config file. Defaults to "archives/config.yml".
          defaultFile(str):
            Nornir defaults file. Defaults to "archives/defaults.yml".
          hostFile(str):
            Nornir host file. Defaults to "archives/movies.yml".
          iniFile(str):
            ConfigParser INI file. Defaults to
            "archives/tech_specs.ini".
        """
        self.nr = InitNornir(cfgFile)
        self.inventory = self.nr.inventory
        self.parser = ConfigParser()

        self.parser.read(iniFile)

        self.genres = self.fetch_ini_data("summary", "genres", ",")
        self.subgenres = self.fetch_ini_data("summary", "subgenres", ",")
        self.descriptors = self.fetch_ini_data("summary","descriptors", ",")

        self.aspectRatios = self.fetch_ini_data("summary",
          "aspect_ratios", ",")
        self.mpaaRatings = self.fetch_ini_data("summary", "mpaa_ratings", ",")

        self.boutiqueLabels = self.fetch_ini_data("boutiqueLabels", "labels",
          ",")

        self.uhd = self.filter_group("4k_uhd")
        self.dv = self.filter_group("hdr10_dv")
        self.hdr10 = self.filter_group("hdr10")
        self.bd = self.filter_group("blu-ray")

        self.steelbooks = self.filter_group("steelbook")
        self.slipcovers = self.filter_group("slipcase")
        self.animation = self.filter_group("animation")
        self.monochrome = self.filter_group("black_white")

    def filter_group(self, group: str):
        """Creates filtered Nornir object via parent group.
        
        Args:
          group(str):
            Name of the parent group to use as a basis for filtering
            the movie library.

        Returns:
          Nornir object (e.g. MvDB.nr.filter()). This is done prior to
          the inventory phase to enable tasks to work against the filter
          (i.e. using MvDB.nr.run(task=task) to act against the entire
          or filtered inventory).
        """
        groupFilter = self.nr.filter(nf(has_parent_group=group))

        return groupFilter

    def fetch_ini_data(self, section: str, option: str, delimiter: str=None):
        """Fetches specified INI option.
        
        Can optionally split fetched data if it's a concatenated string
        by providing a delimiter.

        Args:
          section(str):
            The section header found in the INI file.
          option(str):
            The option to be retrieved.
          delimiter(str):
            Character used to optionally separate a concatenated string.
            Defaults to None.

        Returns:
          Data retrieved from the specified INI option.
        """
        data = self.parser.get(section, option)
        if delimiter is not None:
            data = data.split(delimiter)

        return data