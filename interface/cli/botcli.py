#!/usr/bin/env python

"""Setup for Transcirrus CiaC"""

from __future__ import nested_scopes, division
import sys, os, time, getopt, subprocess, dialog, re
from multiprocessing import Process
'''
from transcirrus.common.auth import authorization
from transcirrus.common import node_util
from transcirrus.common import util
#import transcirrus.common.logger as logger
from transcirrus.common import config
from transcirrus.operations.initial_setup import run_setup
from transcirrus.operations.rollback_setup import rollback
from transcirrus.operations.change_adminuser_password import change_admin_password
from transcirrus.component.keystone.keystone_users import user_ops
from transcirrus.interfaces.shell import dashboard
from transcirrus.operations.restart_all_services import restart_services
'''
from IPy import IP

# compile email regex for easy use
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$")

progname = os.path.basename(sys.argv[0])
progversion = "0.3"
version_blurb = """Setup for TransCirrus Cloud
                   Version 0.1 2013"""

usage = """Usage: %(progname)s [option ...]
Setup for TransCirrus Cloud.

Options:
      --help                   display this message and exit
      --version                output version information and exit""" \
        % {"progname": progname}

# Global parameters
params = {}


def handle_exit_code(d, code):
    """Function showing how to interpret the dialog exit codes.

    This function is not used after every call to dialog in this demo
    for two reasons:

       1. For some boxes, unfortunately, dialog returns the code for
          ERROR when the user presses ESC (instead of the one chosen
          for ESC). As these boxes only have an OK button, and an
          exception is raised and correctly handled here in case of
          real dialog errors, there is no point in testing the dialog
          exit status (it can't be CANCEL as there is no CANCEL
          button; it can't be ESC as unfortunately, the dialog makes
          it appear as an error; it can't be ERROR as this is handled
          in dialog.py to raise an exception; therefore, it *is* OK).

       2. To not clutter simple code with things that are
          demonstrated elsewhere.

    """
    # d is supposed to be a Dialog instance
    if code in (d.DIALOG_CANCEL, d.DIALOG_ESC):
        if code == d.DIALOG_CANCEL:
            msg = "You chose cancel in the last dialog box. Do you want to " \
                  "exit setup?"
        else:
            msg = "You pressed ESC in the last dialog box. Do you want to " \
                  "exit setup?"
        # "No" or "ESC" will bring the user back to the demo.
        # DIALOG_ERROR is propagated as an exception and caught in main().
        # So we only need to handle OK here.
        if d.yesno(msg) == d.DIALOG_OK:
            clear_screen(d)
            sys.exit(0)
        return d.DIALOG_CANCEL
    else:
        # 'code' can be d.DIALOG_OK (most common case) or, depending on the
        # particular dialog box, d.DIALOG_EXTRA, d.DIALOG_HELP,
        # d.DIALOG_ITEM_HELP... (cf. _dialog_exit_status_vars in dialog.py)
        return code


def controls(d):
    """Defines the UI controls for the user"""
    d.msgbox("Use SPACE to select items (ie in a radio list) "
             "Use ARROW KEYS / TAB to move the cursor \n"
             "Use ENTER to submit and advance (OK or Cancel)", width=50)


def userbox(d):
    """Takes input of username"""
    while True:
        (code, answer) = d.inputbox("Username:", init="")
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return answer


def passwordbox(d):
    """Takes input of password"""
    while True:
        # 'insecure' keyword argument only asks dialog to echo asterisks when
        # the user types characters. Not *that* bad.
        (code, password) = d.passwordbox("Password:", insecure=True)
        if handle_exit_code(d, code) == d.DIALOG_OK:
            break
    return password


def firstTimeFlag(d):
    # Return the answer given to the question (also specifies if ESC was
    # pressed)
    return d.yesno("Would you like to perform Setup?",
                   yes_label="Yes, take me to Setup",
                   no_label="No, take me to Coalesce Dashboard", width=80)


def info_ha_primary(d, info_dict):
    while True:
        HIDDEN = 0x1

        elements = [
            ("Node Name:", 1, 1, info_dict['node_name'], 1, 24, 40, 40, 0x0),
            ("Uplink HA IP:", 2, 1, info_dict['up_ha_ip'], 2, 24, 40, 40, 0x0),
            ("Uplink IP:", 3, 1, info_dict['uplink_ip'], 3, 24, 40, 40, 0x0),
            ("Uplink Subnet Mask:", 4, 1, info_dict['uplink_subnet'], 4, 24, 40, 40, 0x0),
            ("Uplink Gateway:", 5, 1, info_dict['uplink_gateway'], 5, 24, 40, 40, 0x0),
            ("Uplink DNS:", 6, 1, info_dict['uplink_dns'], 6, 24, 40, 40, 0x0),
            ("Uplink Domain Name:", 7, 1, info_dict['uplink_domain'], 7, 24, 40, 40, 0x0),
            ("Management IP:", 8, 1, info_dict['mgmt_ip'], 8, 24, 40, 40, 0x0),
            ("Management Subnet Mask:", 9, 1, info_dict['mgmt_subnet'], 9, 24, 40, 40, 0x0),
            ("Management DNS:", 10, 1, info_dict['mgmt_dns'], 10, 24, 40, 40, 0x0),
            ("Management Domain Name:", 11, 1, info_dict['mgmt_domain'], 11, 24, 40, 40, 0x0),
            ("Public IP Start-Point:", 12, 1, info_dict['vm_ip_min'], 12, 24, 40, 40, 0x0),
            ("Public IP End-Point:", 13, 1, info_dict['vm_ip_max'], 13, 24, 40, 40, 0x0),
            ("Admin email:", 14, 1, info_dict['email'], 14, 24, 40, 40, 0x0),
            ("New Admin password:", 15, 1, info_dict['pwd'], 15, 24, 40, 40, HIDDEN),
            ("Confirm Password:", 16, 1, info_dict['cnfrm'], 16, 24, 40, 40, HIDDEN)
            ]
        (code, fields) = d.mixedform(
            "Please fill in Cloud Information:", elements, width=77, insecure=True)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    r_dict = dict()
    r_dict['node_name'] =       fields[0]
    r_dict['up_ha_ip'] =        fields[1]
    r_dict['uplink_ip'] =       fields[2]
    r_dict['uplink_subnet'] =   fields[3]
    r_dict['uplink_gateway'] =  fields[4]
    r_dict['uplink_dns'] =      fields[5]
    r_dict['uplink_domain'] =   fields[6]
    r_dict['mgmt_ip'] =         fields[7]
    r_dict['mgmt_subnet'] =     fields[8]
    r_dict['mgmt_dns'] =        fields[9]
    r_dict['mgmt_domain'] =     fields[10]
    r_dict['vm_ip_min'] =       fields[11]
    r_dict['vm_ip_max'] =       fields[12]
    r_dict['email'] =           fields[13]
    r_dict['pwd'] =             fields[14]
    r_dict['cnfrm'] =           fields[15]
    return r_dict


def info_ha_secondary(d, info_dict):
    while True:
        HIDDEN = 0x1
        elements = [
            ("Node Name:", 1, 1, info_dict['node_name'], 1, 24, 40, 40, 0x0),
            ("Uplink IP:", 2, 1, info_dict['uplink_ip'], 2, 24, 40, 40, 0x0),
            ("Uplink Subnet Mask:", 3, 1, info_dict['uplink_subnet'], 3, 24, 40, 40, 0x0),
            ("Uplink Gateway:", 4, 1, info_dict['uplink_gateway'], 4, 24, 40, 40, 0x0),
            ("Uplink DNS:", 5, 1, info_dict['uplink_dns'], 5, 24, 40, 40, 0x0),
            ("Uplink Domain Name:", 6, 1, info_dict['uplink_domain'], 6, 24, 40, 40, 0x0),
            ("Management IP:", 7, 1, info_dict['mgmt_ip'], 7, 24, 40, 40, 0x0),
            ("Management Subnet Mask:", 8, 1, info_dict['mgmt_subnet'], 8, 24, 40, 40, 0x0),
            ("Management DNS:", 9, 1, info_dict['mgmt_dns'], 9, 24, 40, 40, 0x0),
            ("Management Domain Name:", 10, 1, info_dict['mgmt_domain'], 10, 24, 40, 40, 0x0),
            ("Admin email:", 11, 1, info_dict['email'], 11, 24, 40, 40, 0x0),
            ("New Admin password:", 12, 1, info_dict['pwd'], 12, 24, 40, 40, HIDDEN),
            ("Confirm Password:", 13, 1, info_dict['cnfrm'], 13, 24, 40, 40, HIDDEN)
            ]

        (code, fields) = d.mixedform(
            "Please fill in Cloud Information:", elements, width=77, insecure=True)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    r_dict = dict()
    r_dict['node_name'] =       fields[0]
    r_dict['uplink_ip'] =       fields[1]
    r_dict['uplink_subnet'] =   fields[2]
    r_dict['uplink_gateway'] =  fields[3]
    r_dict['uplink_dns'] =      fields[4]
    r_dict['uplink_domain'] =   fields[5]
    r_dict['mgmt_ip'] =         fields[6]
    r_dict['mgmt_subnet'] =     fields[7]
    r_dict['mgmt_dns'] =        fields[8]
    r_dict['mgmt_domain'] =     fields[9]
    r_dict['email'] =           fields[10]
    r_dict['pwd'] =             fields[11]
    r_dict['cnfrm'] =           fields[12]
    return r_dict


def info_cc(d, info_dict):
    while True:
        HIDDEN = 0x1
        elements = [
            ("Node Name:", 1, 1, info_dict['node_name'], 1, 24, 40, 40, 0x0),
            ("Uplink IP:", 2, 1, info_dict['uplink_ip'], 2, 24, 40, 40, 0x0),
            ("Uplink Subnet Mask:", 3, 1, info_dict['uplink_subnet'], 3, 24, 40, 40, 0x0),
            ("Uplink Gateway:", 4, 1, info_dict['uplink_gateway'], 4, 24, 40, 40, 0x0),
            ("Uplink DNS:", 5, 1, info_dict['uplink_dns'], 5, 24, 40, 40, 0x0),
            ("Uplink Domain Name:", 6, 1, info_dict['uplink_domain'], 6, 24, 40, 40, 0x0),
            ("Management IP:", 7, 1, info_dict['mgmt_ip'], 7, 24, 40, 40, 0x0),
            ("Management Subnet Mask:", 8, 1, info_dict['mgmt_subnet'], 8, 24, 40, 40, 0x0),
            ("Management DNS:", 9, 1, info_dict['mgmt_dns'], 9, 24, 40, 40, 0x0),
            ("Management Domain Name:", 10, 1, info_dict['mgmt_domain'], 10, 24, 40, 40, 0x0),
            ("Public IP Start-Point:", 11, 1, info_dict['vm_ip_min'], 11, 24, 40, 40, 0x0),
            ("Public IP End-Point:", 12, 1, info_dict['vm_ip_max'], 12, 24, 40, 40, 0x0),
            ("Admin email:", 13, 1, info_dict['email'], 13, 24, 40, 40, 0x0),
            ("New Admin password:", 14, 1, info_dict['pwd'], 14, 24, 40, 40, HIDDEN),
            ("Confirm Password:", 15, 1, info_dict['cnfrm'], 15, 24, 40, 40, HIDDEN)
            ]

        (code, fields) = d.mixedform(
            "Please fill in Cloud Information:", elements, width=77, insecure=True)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    r_dict = dict()
    r_dict['node_name'] =       fields[0]
    r_dict['uplink_ip'] =       fields[1]
    r_dict['uplink_subnet'] =   fields[2]
    r_dict['uplink_gateway'] =  fields[3]
    r_dict['uplink_dns'] =      fields[4]
    r_dict['uplink_domain'] =   fields[5]
    r_dict['mgmt_ip'] =         fields[6]
    r_dict['mgmt_subnet'] =     fields[7]
    r_dict['mgmt_dns'] =        fields[8]
    r_dict['mgmt_domain'] =     fields[9]
    r_dict['vm_ip_min'] =       fields[10]
    r_dict['vm_ip_max'] =       fields[11]
    r_dict['email'] =           fields[12]
    r_dict['pwd'] =             fields[13]
    r_dict['cnfrm'] =           fields[14]
    return r_dict


def info_cn(d, info_dict):
    while True:
        HIDDEN = 0x1
        elements = [
            ("Node Name:", 1, 1, info_dict['node_name'], 1, 24, 40, 40, 0x0),
            ("Management IP:", 2, 1, info_dict['mgmt_ip'], 2, 24, 40, 40, 0x0),
            ("Management Subnet Mask:", 3, 1, info_dict['mgmt_subnet'], 3, 24, 40, 40, 0x0),
            ("Management DNS:", 4, 1, info_dict['mgmt_dns'], 4, 24, 40, 40, 0x0),
            ("Management Domain Name:", 5, 1, info_dict['mgmt_domain'], 5, 24, 40, 40, 0x0),
            ("Admin email:", 6, 1, info_dict['email'], 6, 24, 40, 40, 0x0),
            ("New Admin password:", 7, 1, info_dict['pwd'], 7, 24, 40, 40, HIDDEN),
            ("Confirm Password:", 8, 1, info_dict['cnfrm'], 8, 24, 40, 40, HIDDEN)
            ]

        (code, fields) = d.mixedform(
            "Please fill in Cloud Information:", elements, width=77, insecure=True)

        if handle_exit_code(d, code) == d.DIALOG_OK:
            break

    r_dict = dict()
    r_dict['node_name'] =       fields[0]
    r_dict['mgmt_ip'] =         fields[1]
    r_dict['mgmt_subnet'] =     fields[2]
    r_dict['mgmt_dns'] =        fields[3]
    r_dict['mgmt_domain'] =     fields[4]
    r_dict['email'] =           fields[5]
    r_dict['pwd'] =             fields[6]
    r_dict['cnfrm'] =           fields[7]
    return r_dict


def singleNode(d):
    # Return the answer given to the question (also specifies if ESC was
    # pressed)
    return d.yesno("Is this currently a single node system?",
                   yes_label="Yes",
                   no_label="No, it contains other nodes (enable DHCP)", width=100)


def dhcp(d):
    d.gauge_start("Progress: 0%", title="Enabling DHCP...")

    for i in range(1, 101):
        if i < 50:
            d.gauge_update(i, "Progress: %d%%" % i, update_text=1)
        elif i == 50:
            d.gauge_update(i, "Over %d%%. Good." % i, update_text=1)
        elif i == 80:
            d.gauge_update(i, "Yeah, this boring crap will be over Really "
                              "Soon Now.", update_text=1)
        else:
            d.gauge_update(i)

        time.sleep(0.01 if params["fast_mode"] else 0.1)

    d.gauge_stop()


def success_msg(d, seconds):
    uplink = util.get_uplink_ip()
    d.pause("""\
Setup has completed successfully. The system is now ready to use\
 and updated with the information you have entered.  To connect to this unit\
 use the newly created Uplink IP address, %s, and login credentials."""
            % uplink, height=15, seconds=seconds)


def rollback_msg(d, seconds):
    d.pause("""\
Setup has encountered an issue.  The system will now rollback in %u seconds\
 to factory defaults.  Please attempt to rerun setup after rollback."""
            % seconds, height=15, seconds=seconds)


def clear_screen(d):
    program = "clear"

    try:
        p = subprocess.Popen([program], shell=False, stdout=None, stderr=None,
                             close_fds=True)
        retcode = p.wait()
    except os.error, e:
        d.msgbox("Unable to execute program '%s': %s." % (program,
                                                          e.strerror),
                 title="Error")
        return -1

    if retcode > 0:
        msg = "Program %s returned exit code %u." % (program, retcode)
    elif retcode < 0:
        msg = "Program %s was terminated by signal %u." % (program, -retcode)
    else:
        return 0

    d.msgbox(msg)
    return -1


def setup(d):
    d.msgbox("Hello, and welcome to CoalesceShell, the command-line " +
             "interface tool for your TransCirrus system.\n"
             "\n"
             "Node Name: %s\n"
             "Node ID: %s\n"
             "\n"
             "Node Cluster IP: %s \n"
             "Node Uplink IP: %s\n"
             "Node MGMT IP: %s\n"
             % (
                 util.get_node_name(), util.get_node_id(), util.get_cluster_ip(), util.get_uplink_ip(), util.get_mgmt_ip()),
             width=60, height=15)

    controls(d)
    user_dict = None
    while (True):
        user = userbox(d)
        password = passwordbox(d)
        try:
            a = authorization(user, password)
            user_dict = a.get_auth()

            # Verify credentials
            # if cloud admin, continue setup
            # else re-prompt for credentials
            if user_dict['is_admin'] == 1 and user_dict['token'] is not None:
                break
            else:
                d.msgbox("Authentication failed, try again.", width=60, height=10)
        except:
            d.msgbox("Invalid credentials, try again.", width=60, height=10)

    first_time = node_util.check_first_time_boot()
    # Check to determine if first time (will be implemented differently
    # once we have those flags setup on database, this is just proof of concept
    if (first_time['first_time_boot'] == 'FALSE'):
        d.msgbox("Taking you to the Coalesce Dashboard...")
        dashboard.main(user_dict)
        # Direct user to Coalesce Dashboard
        clear_screen(d)
        return
    else:
        d.msgbox("Continue to first time setup.")

    info_dict = {
                    'node_name':        util.get_node_name(),
                    'uplink_ip':        "",
                    'up_ha_ip':         "",
                    'uplink_subnet':    "",
                    'uplink_gateway':   "",
                    'uplink_dns':       "",
                    'uplink_domain':    "",
                    'mgmt_ip':          "",
                    'mgmt_subnet':      "",
                    'mgmt_dns':         "",
                    'mgmt_domain':      "",
                    'vm_ip_min':        "",
                    'vm_ip_max':        "",
                    'email':            "",
                    'pwd':              "",
                    'cnfrm':            ""
                }

    while (True):
        if config.NODE_TYPE == 'ha':
            ha_type = util.get_ha_type()
            if ha_type == 'primary':
                info_dict = info_ha_primary(d, info_dict)
            elif ha_type == 'secondary':
                info_dict = info_ha_secondary(d, info_dict)
        elif config.NODE_TYPE == 'cn':
            info_dict = info_cn(d, info_dict)
        elif config.NODE_TYPE == 'cc':
            info_dict = info_cc(d, info_dict)

        # Confirm all entries exist
        for key in info_dict:
            if info_dict[key] == "":
                d.msgbox("Please fill out all fields, try again.", width=60, height=10)
            continue
        # Validate uplink ip
        if ('uplink_ip' in info_dict and valid_ip(info_dict['uplink_ip']) is False):
            d.msgbox("Invalid Uplink IP, try again.", width=60, height=10)
            continue
        # Validate uplink subnet
        if ('uplink_subnet' in info_dict and valid_ip(info_dict['uplink_subnet']) is False):
            d.msgbox("Invalid Uplink Subnet, try again.", width=60, height=10)
            continue
        # Validate uplink gateway
        if ('uplink_gateway' in info_dict and valid_ip(info_dict['uplink_gateway']) is False):
            d.msgbox("Invalid Uplink Gateway, try again.", width=60, height=10)
            continue
        # Validate gateway has same subnet as uplink
        if ('uplink_ip' in info_dict and 'uplink_gateway' in info_dict and 'uplink_subnet' and \
                    valid_ip_vm(info_dict['uplink_ip'], info_dict['uplink_gateway'], info_dict['uplink_subnet']) is False):
            d.msgbox("Invalid Uplink Gateway, Uplink and Gateway must be on the same subnet, try again.", width=60,
                     height=10)
            continue
        # Validate uplink dns
        if ('uplink_dns' in info_dict and valid_ip(info_dict['uplink_dns']) is False):
            d.msgbox("Invalid Uplink DNS, try again.", width=60, height=10)
            continue
        # Validate mgmt ip
        if ('mgmt_ip' in info_dict and valid_ip(info_dict['mgmt_ip']) is False):
            d.msgbox("Invalid Management IP, try again.", width=60, height=10)
            continue
        # Validate mgmt subnet
        if ('mgmt_subnet' in info_dict and valid_ip(info_dict['mgmt_subnet']) is False):
            d.msgbox("Invalid Management Subnet, try again.", width=60, height=10)
            continue
        # Validate mgmt dns
        if ('mgmt_dns' in info_dict and valid_ip(info_dict['mgmt_dns']) is False):
            d.msgbox("Invalid Management DNS, try again.", width=60, height=10)
            continue
        # Validate start point not equal to uplink
        if ('uplink_ip' in info_dict and 'vm_ip_min' in info_dict and 'uplink_subnet' and
                        valid_ip_vm(info_dict['uplink_ip'], info_dict['vm_ip_min'], info_dict['uplink_subnet']) is False):
            d.msgbox("Invalid VM Range Start-Point, try again.", width=60, height=10)
            continue
        # Validate end point greater than start point
        if ('vm_ip_min' in info_dict and 'vm_ip_max' in info_dict and 'uplink_subnet' in info_dict and
                        valid_ip_max(info_dict['vm_ip_min'], info_dict['vm_ip_max'], info_dict['uplink_subnet']) is False):
            d.msgbox("Invalid VM Range End-Point, try again.", width=60, height=10)
            continue
        # Validate end point not equal to uplink
        if ('uplink_ip' in info_dict and 'vm_ip_max' in info_dict and 'uplink_subnet' in info_dict and
                        valid_ip_vm(info_dict['uplink_ip'], info_dict['vm_ip_max'], info_dict['uplink_subnet']) is False):
            d.msgbox("Invalid VM Range End-Point, try again.", width=60, height=10)
            continue
        # Validate admin email
        if ('email' in info_dict and not EMAIL_REGEX.match(info_dict['email'])):
            d.msgbox("Invalid email format, try again.", width=60, height=10)
            continue
        # Validate new password
        if ('pwd' in info_dict and 'cnfrm' in info_dict and info_dict['pwd'] != info_dict['cnfrm'] and
                        len(info_dict['pwd']) != 0 and len(info_dict['cnfrm']) != 0):
            d.msgbox("Passwords did not match, try again.", width=60, height=10)
            continue
        # Make sure uplink and mgmt IPs don't match
        if ('uplink_ip' in info_dict and 'mgmt_ip' in info_dict and info_dict['uplink_ip'] == info_dict['mgmt_ip']):
            d.msgbox("Uplink IP and Management IP cannot match, try again.", width=60, height=10)
            continue
        break

    name_dict = {'old_name': util.get_node_name(), 'new_name': info_dict['node_name']}
    util.update_cloud_controller_name(name_dict)

    new_system_variables = []
    new_system_variables.append({"system_name": info_dict['node_name'], "parameter": "admin_api_ip", "param_value": '172.24.24.10'})
    new_system_variables.append({"system_name": info_dict['node_name'], "parameter": "int_api_ip", "param_value": '172.24.24.10'})
    if 'uplink_ip' in info_dict:
        new_system_variables.append({"system_name": info_dict['node_name'], "parameter": "uplink_ip", "param_value": info_dict['uplink_ip']})
        new_system_variables.append({"system_name": info_dict['node_name'], "parameter": "api_ip", "param_value": info_dict['uplink_ip']})
    if 'mgmt_ip' in info_dict:
        new_system_variables.append({"system_name": info_dict['node_name'], "parameter": "mgmt_ip", "param_value": info_dict['mgmt_ip']})
    if 'uplink_dns' in info_dict:
        new_system_variables.append({"system_name": info_dict['node_name'], "parameter": "uplink_dns", "param_value": info_dict['uplink_dns']})
    if 'uplink_gateway' in info_dict:
        new_system_variables.append({"system_name": info_dict['node_name'], "parameter": "uplink_gateway", "param_value": info_dict['uplink_gateway']})
    if 'uplink_domain' in info_dict:
        new_system_variables.append({"system_name": info_dict['node_name'], "parameter": "uplink_domain_name", "param_value": info_dict['uplink_domain']})
    if 'uplink_subnet' in info_dict:
        new_system_variables.append({"system_name": info_dict['node_name'], "parameter": "uplink_subnet", "param_value": info_dict['uplink_subnet']})
    if 'mgmt_domain' in info_dict:
        new_system_variables.append({"system_name": info_dict['node_name'], "parameter": "mgmt_domain_name", "param_value": info_dict['mgmt_domain']})
    if 'mgmt_subnet' in info_dict:
        new_system_variables.append({"system_name": info_dict['node_name'], "parameter": "mgmt_subnet", "param_value": info_dict['mgmt_subnet']})
    if 'mgmt_dns' in info_dict:
        new_system_variables.append({"system_name": info_dict['node_name'], "parameter": "mgmt_dns", "param_value": info_dict['mgmt_dns']})
    if 'vm_ip_min' in info_dict:
        new_system_variables.append({"system_name": info_dict['node_name'], "parameter": "vm_ip_min", "param_value": info_dict['vm_ip_min']})
    if 'vm_ip_max' in info_dict:
        new_system_variables.append({"system_name": info_dict['node_name'], "parameter": "vm_ip_max", "param_value": info_dict['vm_ip_max']})

    p = Process(target=run_setup, args=(new_system_variables, user_dict))
    p.start()

    got_error = False
    fill_text = "Preparing your cloud..."
    spinner = ["[|] ", "[/] ", "[-] ", "[\\] "]
    spin = 0
    d.gauge_start(text=fill_text)
    fill = 0
    count = 0
    last_message = "No message"
    while (1):
        spin = (spin + 1) % 4
        out = subprocess.Popen('sudo cat /var/log/caclogs/system.log | grep SETUP%s' % (count), shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out.wait()
        time.sleep(1)
        stat_raw = out.stdout.readlines()
        if (len(stat_raw) == 0):
            # check to see if we got an error message
            prc = subprocess.Popen('sudo cat /var/log/caclogs/system.log | grep SETUPERROR', shell=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            prc.wait()
            raw_msg = prc.stdout.readlines()
            if (len(raw_msg) == 0):
                # no error msg so let's make sure the process is still alive
                if p.is_alive():
                    d.gauge_update(fill, text=spinner[spin]+fill_text, update_text=1)
                    continue
                else:
                    # our process is dead and there was no error message so we need to report it
                    stat_raw = []
                    stat_raw.append("1:2:3:4:SETUPERROR:Setup adnormally terminated; please contact TransCirrus")
            else:
                # got an error msg so let the code below handle it
                stat_raw = raw_msg
        count += 1
        fill += 1.851
        stat = stat_raw[0].split(':')

        if len(stat) > 0:
            fill_text = stat[-1].strip()
        else:
            fill_text = ""

        if len(stat) > 1:
            key_text = stat[-2].strip()
        else:
            key_text = ""

        if (fill_text == "END"):
            p.join()
            fill = 0
            # update admin password
            o = Process(target=change_admin_password, args=(user_dict, info_dict['pwd']))
            o.start()
            forked = False
            while (1):
                if forked is False:
                    # update admin email
                    pid = os.fork()
                    forked = True
                    if pid == 0:
                        uo = user_ops(user_dict)
                        uo.update_user({'username': "admin", 'email': info_dict['email']})
                        os._exit(0)
                spin = (spin + 1) % 4
                d.gauge_update(fill, text=spinner[spin]+'Updating admin account...', update_text=1)
                fill += 7.692
                time.sleep(1)
                if (fill > 100):
                    o.join()
                    os.waitpid (pid, os.WNOHANG)
                    break
            break
        elif "SETUPERROR" in key_text:
            last_message = fill_text
            d.gauge_update(100, text=spinner[spin]+fill_text, update_text=1)
            got_error = True
            break
        else:
            d.gauge_update(fill, text=spinner[spin]+fill_text, update_text=1)
    d.gauge_stop()

    timeout = 10

    if got_error:
        d.msgbox("An error has occurred: " + last_message)
        rollback_msg(d, timeout)
        #clear_screen(d)
        rollback(user_dict)
        #util.reboot_system()
    elif p.exitcode == 0:
        restart_services()
        flag_set = node_util.set_first_time_boot('UNSET')
        if (flag_set['first_time_boot'] != 'OK'):
            d.msgbox("An error has occured in setting the first time boot flag.")
        success_msg(d, timeout)
        clear_screen(d)
    else:
        rollback_msg(d, timeout)
        #clear_screen(d)
        rollback(user_dict)
        #util.reboot_system()


def valid_ip(address):
    """
    Validate IP address using IPy library
    """
    try:
        if check_ip_format(address):
            IP(address)
            return True
        else:
            return False
    except ValueError:
        return False
    except Exception:
        return False


def check_ip_format(address):
    host_bytes = address.split('.')
    valid = [int(b) for b in host_bytes]
    valid = [b for b in valid if b >= 0 and b <= 255]
    return len(host_bytes) == 4 and len(valid) == 4


def valid_ip_vm(uplink, vm, mask):
    """
    Validate uplinkIP and vmIPs range are in a valid subnet using IPy
    """
    try:
        if IP(uplink).make_net(mask) == IP(vm).make_net(mask):
            return True
        else:
            return False
    except Exception:
        return False


def valid_ip_max(min_ip, max_ip, mask):
    """
    Validate that the max_ip IP address has the same network prefix of the min_ip IP address
    and that they both exist in the same subnet
    """
    try:
        if IP(min_ip).make_net(mask) == IP(max_ip).make_net(mask):
            return True
        else:
            return False
    except Exception:
        return False


def main():
    try:
        # If you want to use Xdialog (pathnames are also OK for the 'dialog'
        # argument), you can use:
        #   d = dialog.Dialog(dialog="Xdialog", compat="Xdialog")
        d = dialog.Dialog(dialog="dialog")
        d.add_persistent_args(["--backtitle", "TransCirrus - CoalesceShell"])

        setup(d)
    except dialog.error, exc_instance:
        sys.stderr.write("Error:\n\n%s\n" % exc_instance.complete_message())
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__": main()

#What to look for
# IP info
# MQTT broker
# MQTT port
# Interval
# 