# -*- coding: utf-8 -*-
#
# Copyright © 2011 CEA
# Pierre Raybaut
# Licensed under the terms of the CECILL License
# (see guidata/__init__.py for details)

"""
qthelpers
---------

The ``guiqwt.qthelpers`` module provides helper functions for developing
easily Qt-based graphical user interfaces with guiqwt.

Ready-to-use open/save dialogs:
    :py:data:`guiqwt.qthelpers.exec_image_save_dialog`
        Executes an image save dialog box (QFileDialog.getSaveFileName)
    :py:data:`guiqwt.qthelpers.exec_image_open_dialog`
        Executes an image open dialog box (QFileDialog.getOpenFileName)
    :py:data:`guiqwt.qthelpers.exec_images_open_dialog`
        Executes an image*s* open dialog box (QFileDialog.getOpenFileNames)

Reference
~~~~~~~~~

.. autofunction:: exec_image_save_dialog
.. autofunction:: exec_image_open_dialog
.. autofunction:: exec_images_open_dialog
"""

import sys
import os.path as osp
import numpy as np

from qtpy.QtWidgets import QMessageBox
from qtpy.compat import getsavefilename, getopenfilename, getopenfilenames

# Local imports
from guiqwt.config import _
from guiqwt import io


# ===============================================================================
# Ready-to-use open/save dialogs
# ===============================================================================
def exec_image_save_dialog(parent, data, template=None, basedir="", app_name=None):
    """
    Executes an image save dialog box (QFileDialog.getSaveFileName)
        * parent: parent widget (None means no parent)
        * data: image pixel array data
        * template: image template (pydicom dataset) for DICOM files
        * basedir: base directory ('' means current directory)
        * app_name (opt.): application name (used as a title for an eventual
          error message box in case something goes wrong when saving image)

    Returns filename if dialog is accepted, None otherwise
    """
    saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
    sys.stdout = None
    if data.dtype.str == '<f8' or data.dtype.str == '<f4' :
        convert = True
        dt = np.dtype('uint8')
    else :
        convert = False
        dt = data.dtype
    try :
        filename, _filter = getsavefilename(parent, _("Save as"), basedir,
            io.iohandler.get_filters('save', dtype=data.dtype, template=template))
        sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err
    except TypeError:
        filename, _filter = getsavefilename(parent, _("Save as"), "",
            io.iohandler.get_filters('save', dtype=data.dtype, template=template))
        sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err
    if filename:
        filename = str(filename)
        kwargs = {}
        if osp.splitext(filename)[1].lower() == ".dcm":
            kwargs["template"] = template
        try:
            if convert == False or ext==".txt" or ext ==".csv" or ext==".asc" \
            or ext==".dat" or ext==".npy":
                io.imwrite(filename, data, **kwargs)
            else :
                if ext ==".tif" or ext==".tiff" or ext==".dcm":
                    dt = np.dtype('uint16')
                else :
                    dt = np.dtype('uint8')
                io.imwrite(filename, data, max_range = True, dtype = dt, **kwargs)
            return filename
        except Exception as msg:
            import traceback

            traceback.print_exc()
            QMessageBox.critical(
                parent,
                _("Error") if app_name is None else app_name,
                (_("%s could not be written:") % osp.basename(filename))
                + "\n"
                + str(msg),
            )
            return


def exec_image_open_dialog(
    parent, basedir="", app_name=None, to_grayscale=True, dtype=None
):
    """
    Executes an image open dialog box (QFileDialog.getOpenFileName)
        * parent: parent widget (None means no parent)
        * basedir: base directory ('' means current directory)
        * app_name (opt.): application name (used as a title for an eventual
          error message box in case something goes wrong when saving image)
        * to_grayscale (default=True): convert image to grayscale

    Returns (filename, data) tuple if dialog is accepted, None otherwise
    """
    saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
    sys.stdout = None
    filename, _filter = getopenfilename(
        parent, _("Open"), basedir, io.iohandler.get_filters("load", dtype=dtype)
    )
    sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err
    filename = str(filename)
    try:
        data = io.imread(filename, to_grayscale=to_grayscale)
    except Exception as msg:
        import traceback

        traceback.print_exc()
        QMessageBox.critical(
            parent,
            _("Error") if app_name is None else app_name,
            (_("%s could not be opened:") % osp.basename(filename)) + "\n" + str(msg),
        )
        return
    return filename, data


def exec_images_open_dialog(
    parent, basedir="", app_name=None, to_grayscale=True, dtype=None
):
    """
    Executes an image*s* open dialog box (QFileDialog.getOpenFileNames)
        * parent: parent widget (None means no parent)
        * basedir: base directory ('' means current directory)
        * app_name (opt.): application name (used as a title for an eventual
          error message box in case something goes wrong when saving image)
        * to_grayscale (default=True): convert image to grayscale

    Yields (filename, data) tuples if dialog is accepted, None otherwise
    """
    saved_in, saved_out, saved_err = sys.stdin, sys.stdout, sys.stderr
    sys.stdout = None
    filenames, _filter = getopenfilenames(
        parent, _("Open"), basedir, io.iohandler.get_filters("load", dtype=dtype)
    )
    sys.stdin, sys.stdout, sys.stderr = saved_in, saved_out, saved_err
    filenames = [str(fname) for fname in list(filenames)]
    if filenames != []:
        _base, ext = osp.splitext(filenames[0])
        if ext==".bin" or ext==".raw" or ext==".img" or ext==".imd":
            if osp.isfile(_base+".inf"):
                RAW = False
            else :
                RAW = True
        else :
            RAW = False
        params = {}
        if RAW==True:
            from guidata.dataset.datatypes import DataSet, ValueProp, NotProp
            from guidata.dataset.dataitems import (IntItem, ChoiceItem, BoolItem)
            offset_list = ('from_end', 'from_end_4k', 'auto')
            dtype_list = ('int16','int32','uint16','uint32')
            prop = ValueProp(False)
            class OpenParam(DataSet):
                dtype = ChoiceItem(_("Data Type"), list(zip(dtype_list, dtype_list)),
                                  default=dtype_list[2],\
                                  )
                mode = ChoiceItem(_("Offset mode"), list(zip(offset_list, offset_list)),
                                  default=offset_list[0],\
                                  help=_("* "'auto'" : try to read the offset in the header.\n \
                                  That should be the normal way of getting to offset, but it doesn't really work.\n \
                                  * "'from_end'": get offset as data_size - image_size\n\
                                  * "'from_end_4k'": same as "'from_end'" but additionnaly\n\
                                  substract 4092 (seems to be streak dependant..)")).set_prop("display", active=NotProp(prop))
                endian_switch = BoolItem(_("Little Endian Byte Order?"),
                                     default=True)
                manual_switch = BoolItem(_("Manual Offset"),
                                     default=True).set_prop("display", store=prop)
                m_offset = IntItem(_("Manual Offset"), default=0.,
                                 help=_("Value used for points outside the "
                                        "boundaries of the input if mode is "
                                        "'constant'")).set_prop("display", active=prop)
            class nOpenParam(DataSet):
                dtype = ChoiceItem(_("Data Type"), list(zip(dtype_list, dtype_list)),
                                  default=dtype_list[0],\
                                  )
                mode = ChoiceItem(_("Offset mode"), list(zip(offset_list, offset_list)),
                                  default=offset_list[0],\
                                  help=_("* "'auto'" : try to read the offset in the header.\n \
                                  That should be the normal way of getting to offset, but it doesn't really work.\n \
                                  * "'from_end'": get offset as data_size - image_size\n\
                                  * "'from_end_4k'": same as "'from_end'" but additionnaly\n\
                                  substract 4092 (seems to be streak dependant..)")).set_prop("display", active=NotProp(prop))
                endian_switch = BoolItem(_("Little Endian Byte Order?"),
                                     default=True)
                manual_switch = BoolItem(_("Manual Offset"),
                                     default=True).set_prop("display", store=prop)
                m_offset = IntItem(_("Manual Offset"), default=0.,
                                 help=_("Value used for points outside the "
                                        "boundaries of the input if mode is "
                                        "'constant'")).set_prop("display", active=prop)
                one4all = BoolItem(_("One Parameter for all?"),
                                     default=True)
                                     
            one4all = False
            if len(filenames)>1:
                param = nOpenParam(_("Open Raw Images"))
                if not param.edit() :
                    return
                if param.manual_switch==True:
                    offset = param.m_offset
                else:
                    offset = param.mode
                dtype = np.dtype(param.dtype)
                if param.endian_switch==False:
                    dtype = dtype.newbyteorder()
                params = {'offset': offset, 'dtype': dtype}
                one4all = param.one4all
    for filename in filenames:
        try:
            _base,ext = osp.splitext(filename)
            filename = str(filename)
            if RAW==True :
                if params == {} or not one4all :
                    if len(filenames)>1:
                        param = nOpenParam(_("Open Raw Images"))
                        if not param.edit() :
                            return
                        one4all = param.one4all
                    else :
                        param = OpenParam(_("Open Raw Image"))
                        if not param.edit() :
                            return
                    if param.manual_switch==True:
                        offset = param.m_offset
                    else:
                        offset = param.mode
                    dtype = np.dtype(param.dtype)
                    if param.endian_switch==False:
                        dtype = dtype.newbyteorder()
                    params = {'offset': offset, 'dtype': dtype}
            data = io.imread(filename, to_grayscale=to_grayscale, params=params)
        except Exception as msg:
            import traceback

            traceback.print_exc()
            QMessageBox.critical(
                parent,
                _("Error") if app_name is None else app_name,
                (_("%s could not be opened:") % osp.basename(filename))
                + "\n"
                + str(msg),
            )
            return
        yield filename, data
