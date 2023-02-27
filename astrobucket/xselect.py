"""Xselect module.
"""
import os
import subprocess

from astrobucket import Config
from astrobucket import satellite


class XselectCommander:
    def __init__(self):
        pass

    def _generate_curve_command(self, fits_file, dt, pi_lower, pi_upper):
        path = "/".join(fits_file.split("/")[:-1])
        file = fits_file.split("/")[-1]
        tmp_path = Config.tmp_path

        xsel_cmd = [
            f"xselect > {tmp_path}/xselect_log.log 2>&1 << EOF\n",
            "xsel\n",
            f"read event {file}\n",
            f"{path}\n",
            "yes\n",
            "\n",
            f"set binsize {dt}\n",
            "\n",
            f"filter pha_cutoff {pi_lower+1} {pi_upper}\n",
            "ext curve offset=no\n",
            f"save curve {tmp_path}/xselect_tmp.fits\n",
            "\n",
            "exit\n",
            "no\n",
            "EOF\n",
        ]

        script_path = os.path.join(tmp_path, "xselect_script.sh")
        with open(script_path, "w") as f:
            f.writelines(xsel_cmd)

        return script_path

    def _convert_kev2pi(self, kev: float, piperkev: float):
        pi = int(kev * piperkev)
        return pi

    def create_curve(self, *inputs):
        sat = satellite.get_satellite(inputs[3])
        piperkev = sat.piperkev

        fits_file = inputs[0]
        dt = inputs[-2]
        pi_lower = self._convert_kev2pi(inputs[-1][0], piperkev)
        pi_upper = self._convert_kev2pi(inputs[-1][1], piperkev)
        script_path = self._generate_curve_command(
            fits_file, dt, pi_lower, pi_upper)

        bash_cmd = ["bash", script_path]
        subprocess.run(bash_cmd)
        if os.path.exists("xselect.log"):
            os.remove("xselect.log")

    def create_spactrum(self, *inputs):
        raise NotImplementedError()
