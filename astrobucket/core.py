"""Core module.
"""
import copy
import hashlib
import os
import shutil

from astropy.table import Table

from astrobucket.config import Config
from astrobucket.xselect import XselectCommander


def open_fits_astable(fits_path: str):
    table = Table.read(fits_path, hdu=1)
    return table


class Client:
    """
    Raises
        TypeError: If `obsid` is not str.
    """
    def __init__(self, fits_path: str, object_name: str,
                 satellite: str, obsid: str, verbose: bool = True,
                 save_cache: bool = True):
        if not isinstance(obsid, str):
            raise TypeError(f"{type(obsid)} is not supported.")

        self.fits_path = fits_path
        self.object_name = object_name
        self.satellite = satellite
        self.obsid = obsid
        self.verbose = verbose

        # self.inputs[1] indicate creation mode (={"curve", "spectrum"}).
        self.inputs = [fits_path, "none", object_name, satellite, obsid]

        self.server = Server(Config.cache_path, verbose, save_cache)

    def clear_cache(self, mode: str, *args):
        inputs = copy.copy(self.inputs)
        inputs[1] = mode
        if mode == "curve":
            dt = args[0]
            energy_range_kev = args[1]
            inputs.extend([dt, energy_range_kev])
        elif mode == "spectrum":
            de = args[0]
            energy_range_kev = args[1]
            inputs.extend([de, energy_range_kev])
        else:
            raise NotImplementedError()
        self.server.clear_cache(*inputs)

    def request_curve(self, dt: float, energy_range_kev: tuple or list,
                      verbose: bool = True):
        inputs = copy.copy(self.inputs)
        inputs[1] = "curve"
        inputs.extend([dt, (energy_range_kev[0], energy_range_kev[1])])
        curve = self.server.request(*inputs)
        return curve

    def request_event(self):
        table = open_fits_astable(self.fits_path)
        return table

    def request_spectrum(self, de: float, energy_range_kev: tuple,
                         verbose: bool = True):
        inputs = copy.copy(self.inputs)
        inputs[1] = "spectum"
        inputs.extend([de, energy_range_kev])
        spectrum = self.server.request(*inputs)
        return spectrum


class Creator:
    """Create request `astropy.table`.
    """
    def _create_curve(self):
        xsel_commander = XselectCommander()
        xsel_commander.create_curve(*self.inputs)

    def _create_spectrum(self):
        raise NotImplementedError("Comming soon...")
        # TODO: create spectrum.
        # de = self.inputs[-2]
        # energy_range = self.inputs[-1]
        spectrum = None
        return spectrum

    def create(self, *inputs):
        self.inputs = inputs
        self.mode = inputs[1]  # mode = {"curve", "spectrum"}
        if self.mode == "curve":
            self._create_curve()
        elif self.mode == "spectrum":
            self._create_spectrum()
        fits_path = os.path.join(Config.tmp_path, "xselect_tmp.fits")
        return fits_path


class Namer:
    """Name class.

    Raises
        TypeError: if inputs have other types exept to `int`, `float`, `str`,
            `list`, and `tuple`.
    """
    def _convert_float(self, value: float):
        if int(value) == value:
            return self._convert_int(int(value))
        word = str(value).rjust(10, "0")
        word = word.replace(".", "p")
        return word

    def _convert_int(self, value: int):
        word = str(value).rjust(10, "0")
        return word

    def _convert_multiple(self, value: list or tuple):
        words = [self._convert_single(v) for v in value]
        words = "-".join(words)
        return words

    def _convert_single(self, value: float or int or str):
        if isinstance(value, float):
            word = self._convert_float(value)
        elif isinstance(value, int):
            word = self._convert_int(value)
        elif isinstance(value, str):
            word = self._convert_str(value)
        elif isinstance(value, (list, tuple)):
            word = self._convert_multiple(value)
        return word

    def _convert_str(self, value: str):
        word = str(value)  # Copy instance.
        word = value.lower()
        word = word.replace(" ", "")
        return word

    def get_name(self, *inputs):
        word_list = []
        for t in inputs:
            if isinstance(t, (float, int, str)):
                word = self._convert_single(t)
            elif isinstance(t, (list, tuple)):
                word = self._convert_multiple(t)
            else:
                raise TypeError(f"{type(t)} is not supported.")
            word_list.append(word)
        fullname = "_".join(word_list)
        return fullname


class Server:
    """Server.

    If cache exists, return that. If not, inputs are passed to
    Creator instance.
    """
    def __init__(self, cache_path: str, verbose: bool = True,
                 save_cache: bool = True):
        self.cache_path = cache_path
        self.verbose = verbose
        self.save_cache = save_cache

    def _check_cache(self, filename: str):
        search_path = os.path.join(self.cache_path, filename)
        return os.path.exists(search_path)

    def _convert2hash(self, target: object):
        target_hash = hashlib.md5(target.encode()).hexdigest()
        return target_hash

    def _get_eventhash(self, event_path: str):
        """Get event hash by reading event file.
        """
        hash_ = hashlib.md5()
        with open(event_path, 'rb') as f:
            while True:
                chunk = f.read(2048 * hash_.block_size)
                if len(chunk) == 0:
                    break
                hash_.update(chunk)
        event_hash = hash_.hexdigest()
        return event_hash

    def clear_cache(self, *inputs):
        basename = Namer().get_name(*inputs[1:])
        filename_hash = self._convert2hash(basename)
        fits_path = os.path.join(self.cache_path, filename_hash)
        if os.path.exists(fits_path):
            os.remove(fits_path)

    def request(self, *inputs):

        # Use hash from combined hash of filename and event_hash to
        # ensure that the event file is the same as previous one.
        basename = Namer().get_name(*inputs[1:])
        filename_hash = self._convert2hash(basename)
        event_hash = self._get_eventhash(inputs[0])
        reference_hash = self._convert2hash(filename_hash + event_hash)

        exist = self._check_cache(reference_hash)
        fits_path = os.path.join(self.cache_path, reference_hash)
        if not exist:
            tmp_fits_path = Creator().create(*inputs)
            if self.save_cache:
                shutil.copy(tmp_fits_path, fits_path)
                fits_path = tmp_fits_path
        else:
            if self.verbose:
                print(f"use cache for {basename}")
        table = open_fits_astable(fits_path)

        return table
