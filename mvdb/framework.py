from configparser import ConfigParser
from nornir import InitNornir
from nornir.core.filter import F as nf


class MvDB:
    """TODO"""
    subdir = "archives/"
    configFile = subdir + "config.yml"
    defaultFile = subdir + "default.yml"
    hostFile =  subdir + "movies.yml"
    cfgINI = subdir + "tech_specs.ini"

    def __init__(
            self,
            cf: str=configFile,
            df: str=defaultFile,
            hf: str=hostFile,
            ini: str=cfgINI
        ):
        """TODO"""
        self.nr = InitNornir(cf)
        self.cf = ConfigParser()

        self.cf.read(ini)
        self.genres = self.cf["summary"]["genres"].split(",")
        self.subgenres = self.cf["summary"]["subgenres"].split(",")
        self.descriptors = self.cf["summary"]["descriptors"].split(",")

        self.aspectRatios = self.cf["summary"]["aspect_ratios"].split(",")
        self.mpaaRatings = self.cf["summary"]["mpaa_ratings"].split(",")

        self.uhd = self.filter_group("4k_uhd")
        self.dv = self.filter_group("hdr10_dv")
        self.hdr10 = self.filter_group("hdr10")
        self.bd = self.filter_group("blu-ray")

        self.steelbooks = self.filter_group("steelbook")
        self.slipcovers = self.filter_group("slipcase")
        self.animation = self.filter_group("animation")
        self.monochrome = self.filter_group("black_white")

    def filter_group(self, group: str):
        """Creates filtered Nornir inventory object via parent group.
        
        Args:
          group(str):
            Name of the parent group to use as a basis for filtering
            the movie library.

        Returns:
          Nornir inventory object.
        """
        groupFilter = self.nr.inventory.filter(nf(has_parent_group=group))

        return groupFilter