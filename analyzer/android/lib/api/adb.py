# Copyright (C) 2014-2016 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.
# Originally contributed by Check Point Software Technologies, Ltd.

import logging
import os
import subprocess
import re
from lib.common.utils import send_file

log = logging.getLogger(__name__)

def install_sample(path):
    """Install the sample on the emulator via adb"""
    log.info("Installing sample in the device: %s", path)
    try:
        args = ["/system/bin/sh", "/system/bin/pm", "install", path]
        output = subprocess.check_output(args)
    except subprocess.CalledProcessError as e:
        log.error("Error installing sample: %r", e)
        return

    log.info("Installed sample: %r", output)

def execute_sample(package, activity):
    """Execute the sample on the emulator via adb"""
    try:
        package_activity = "%s/%s" % (package, activity)
        args = [
            "/system/bin/sh", "/system/bin/am", "start",
            "-n", package_activity,
        ]
        output = subprocess.check_output(args)
    except subprocess.CalledProcessError as e:
        log.error("Error executing package activity: %r", e)
        return

    log.info("Executed package activity: %r", output)

def dump_droidmon_logs(package):
    xposed_logs = "/data/data/de.robv.android.xposed.installer/log/error.log"
    if not os.path.exists(xposed_logs):
        log.info("Could not find any Xposed logs, skipping droidmon logs.")
        return

    tag = "Droidmon-apimonitor-%s" % package
    tag_error = "Droidmon-shell-%s" % package

    log_xposed, log_success, log_error = [], [], []

    for line in open(xposed_logs, "rb"):
        if tag in line:
            log_success.append(line.split(":", 1)[1])

        if tag_error in line:
            log_error.append(line.split(":", 1)[1])

        log_xposed.append(line)

    send_file("logs/xposed.log", "\n".join(log_xposed))
    send_file("logs/droidmon.log", "\n".join(log_success))
    send_file("logs/droidmon_error.log", "\n".join(log_error))

def execute_browser(url):
    """Start URL intent on the emulator."""
    try:
        args = [
            "/system/bin/sh", "/system/bin/am", "start",
            "-a", "android.intent.action.VIEW",
            "-d", url,
        ]
        output = subprocess.check_output(args)
    except subprocess.CalledProcessError as e:
        log.error("Error starting browser intent: %r", e)
        return

    log.info("Intent returned: %r", output)

def take_screenshot(filename):
    try:
        subprocess.check_output(["/system/bin/screencap", "-p",
                                 "/sdcard/%s" % filename])
    except subprocess.CalledProcessError as e:
        log.error("Error creating screenshot: %r", e)
        return

    return "/sdcard/%s" % filename

def shell(command):
    """
    Execute a command
    """
    output = ""
    if isinstance(command, list):
        args = command
    elif isinstance(command, str):
        args = command.split(" ")
    else:
        log.error("Error executing command with type: ", type(command))
        return output
    try:
        output = subprocess.check_output(args)
    except subprocess.CalledProcessError as e:
        log.error("Error executing command: %r", e)
    except OSError as e:
        log.error("Error executing command: %r", e)
    return output


def getPackagePath(package_name):
    """
    Get installed path of a package
    """
    command = "pm path %s" % package_name
    path = shell(command)
    if path:
        path = path.split(":")[1]
    return path


#Modified APIs from AndroidViewClient
#https://github.com/dtmilano/AndroidViewClient/
def getTopActivityName():
    """
    Get current activity
    """
    data = shell("dumpsys activity top").splitlines()
    regex = re.compile("\s*ACTIVITY ([A-Za-z0-9_.]+)/([A-Za-z0-9_.]+)")
    m = regex.search(data)
    if m:
        return m.group(1) + "/" + m.group(2)

def getDisplayInfo():
    displayInfo = getLogicalDisplayInfo()
    if displayInfo:
        return displayInfo
    displayInfo = getPhysicalDisplayInfo()
    if displayInfo:
        return displayInfo
    log.error("Error getting display info")
    return None

def getLogicalDisplayInfo():
    """
    Gets C{mDefaultViewport} and then C{deviceWidth} and C{deviceHeight} values from dumpsys.
    This is a method to obtain display logical dimensions and density
    """
    logicalDisplayRE = re.compile(".*DisplayViewport{valid=true, .*orientation=(?P<orientation>\d+), .*deviceWidth=(?P<width>\d+), deviceHeight=(?P<height>\d+).*")
    for line in shell("dumpsys display").splitlines():
        m = logicalDisplayRE.search(line, 0)
        if m:
            displayInfo = {}
            for prop in ["width", "height", "orientation"]:
                displayInfo[prop] = int(m.group(prop))
            for prop in ["density"]:
                d = getDisplayDensity(None, strip=True, invokeGetPhysicalDisplayIfNotFound=True)
                if d:
                    displayInfo[prop] = d
                else:
                    # No available density information
                    displayInfo[prop] = -1.0
            return displayInfo
    return None

def getPhysicalDisplayInfo():
    """
    Gets C{mPhysicalDisplayInfo} values from dumpsys. This is a method to obtain display dimensions and density
    """
    phyDispRE = re.compile("Physical size: (?P<width>)x(?P<height>).*Physical density: (?P<density>)", re.MULTILINE)
    data = shell("wm size") + shell("wm density")
    m = phyDispRE.search(data)
    if m:
        displayInfo = {}
        for prop in ["width", "height"]:
            displayInfo[prop] = int(m.group(prop))
        for prop in ["density"]:
            displayInfo[prop] = float(m.group(prop))
        return displayInfo
    phyDispRE = re.compile(
        ".*PhysicalDisplayInfo{(?P<width>\d+) x (?P<height>\d+), .*, density (?P<density>[\d.]+).*")
    for line in shell("dumpsys display").splitlines():
        m = phyDispRE.search(line, 0)
        if m:
            displayInfo = {}
            for prop in ["width", "height"]:
                displayInfo[prop] = int(m.group(prop))
            for prop in ["density"]:
                # In mPhysicalDisplayInfo density is already a factor, no need to calculate
                displayInfo[prop] = float(m.group(prop))
            return displayInfo
    # This could also be mSystem or mOverscanScreen
    phyDispRE = re.compile("\s*mUnrestrictedScreen=\((?P<x>\d+),(?P<y>\d+)\) (?P<width>\d+)x(?P<height>\d+)")
    # This is known to work on older versions (i.e. API 10) where mrestrictedScreen is not available
    dispWHRE = re.compile("\s*DisplayWidth=(?P<width>\d+) *DisplayHeight=(?P<height>\d+)")
    for line in shell("dumpsys window").splitlines():
        m = phyDispRE.search(line, 0)
        if not m:
            m = dispWHRE.search(line, 0)
        if m:
            displayInfo = {}
            BASE_DPI = 160.0
            for prop in ["width", "height"]:
                displayInfo[prop] = int(m.group(prop))
            for prop in ["density"]:
                d = 0
                if displayInfo and "density" in displayInfo:
                    d = displayInfo["density"]
                else:
                    _d = shell("getprop ro.sf.lcd_density").strip()
                    if _d:
                        d = float(_d) / BASE_DPI
                    else:
                        _d = shell("getprop qemu.sf.lcd_density").strip()
                        if _d:
                            d = float(_d) / BASE_DPI
                if d:
                    displayInfo[prop] = d
                else:
                    # No available density information
                    displayInfo[prop] = -1.0
            return displayInfo
    return None

def unlock():
    """
    Unlock the screen of the device
    """
    shell("input keyevent MENU")
    shell("input keyevent BACK")

def press(key):
    """
    Press a key
    """
    shell("input keyevent %s" % key)
    